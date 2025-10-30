#!/usr/bin/env python3
"""
Unified Scraper-Processor Pipeline Orchestration

This module provides a seamless integration between the document scraper
and accessibility processor, supporting both macOS and WSL environments.
"""

import os
import sys
import platform
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import json
import tempfile
import shutil

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scraper.purdue_downloader import process_purdue_library_content, process_url_list
from scraper.optimized_downloader import optimize_purdue_download
from processor.unified_project.src.services.enhancement_service import EnhancementService
from processor.unified_project.src.orchestration.duplicate_detection import DuplicateDetectionManager


class CrossPlatformPipelineConfig:
    """
    Cross-platform configuration management for the scraper-processor pipeline.
    
    Handles platform-specific differences between macOS and WSL environments
    while providing a unified interface. Prioritizes S: drive access when available.
    """
    
    def __init__(self, base_working_dir: Optional[str] = None, force_local: bool = False):
        self.platform = platform.system().lower()
        self.is_wsl = self._detect_wsl()
        self.force_local = force_local
        
        # Determine the working directory with S: drive priority
        if force_local or not self._detect_s_drive_access():
            # Use local directory if forced or S: drive not accessible
            self.base_working_dir = Path(base_working_dir) if base_working_dir else self._get_default_working_dir()
            self.using_s_drive = False
        else:
            # Use S: drive - the organizational requirement
            self.base_working_dir = self._get_s_drive_path()
            self.using_s_drive = True
        
        # Create platform-appropriate directory structure
        self.scraper_output_dir = self.base_working_dir / "scraped_documents"
        self.processor_input_dir = self.scraper_output_dir  # Direct handoff
        self.processor_output_dir = self.base_working_dir / "enhanced_documents"
        self.pipeline_logs_dir = self.base_working_dir / "pipeline_logs"
        self.temp_dir = self.base_working_dir / "temp_pipeline"
        
        # Processing configuration
        self.enhancement_mode = "academic"
        self.language = "en-US"
        self.force_ocr = True
        
        # Scraper configuration
        self.scraper_workers = 3
        self.use_shared_driver = True
        self.use_optimized_downloads = True
        self.manual_login = False
        
        # Duplicate detection configuration
        self.enable_duplicate_detection = True
        self.skip_existing_files = True
        
    def _detect_wsl(self) -> bool:
        """Detect if running in WSL environment."""
        try:
            # Multiple detection methods for reliability
            if "microsoft" in platform.release().lower():
                return True
            
            if os.path.exists('/proc/sys/fs/binfmt_misc/WSLInterop'):
                return True
            
            with open('/proc/version', 'r') as f:
                version = f.read().lower()
                if 'microsoft' in version or 'wsl' in version:
                    return True
        except:
            pass
        
        return False
    
    def _get_s_drive_path(self) -> Path:
        """Get the S: drive path for the current platform."""
        if self.is_wsl:
            return Path("/mnt/s/Departments/ePubs/Accessibility_Project")
        elif self.platform == "darwin":  # macOS
            # Correct mount point for macOS Accessibility_Project volume
            return Path("/Volumes/Accessibility_Project")
        else:
            # Linux fallback
            return Path("/mnt/s/Departments/ePubs/Accessibility_Project")
    
    def _detect_s_drive_access(self) -> bool:
        """Detect if S: drive is accessible on the current platform."""
        try:
            s_drive_path = self._get_s_drive_path()
            
            # Check if the path exists and is accessible
            if not s_drive_path.exists():
                return False
            
            # Try to create a small test file to verify write access
            test_file = s_drive_path / ".pipeline_access_test"
            try:
                test_file.touch()
                test_file.unlink()  # Clean up
                return True
            except (OSError, PermissionError):
                # Path exists but not writable
                return False
                
        except Exception:
            return False
    
    def _get_default_working_dir(self) -> Path:
        """Get platform-appropriate default working directory."""
        if self.platform == "darwin":  # macOS
            return Path.home() / "Documents" / "ePubs_Pipeline"
        elif self.is_wsl:  # WSL
            # Try to use a consistent location that works in WSL
            wsl_home = Path.home()
            return wsl_home / "ePubs_Pipeline"
        else:  # Linux
            return Path.home() / "ePubs_Pipeline"
    
    def create_directories(self) -> bool:
        """Create all required directories."""
        try:
            directories = [
                self.scraper_output_dir,
                self.processor_output_dir,
                self.pipeline_logs_dir,
                self.temp_dir
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            logging.error(f"Failed to create directories: {e}")
            if self.using_s_drive:
                logging.error("S: drive may not be properly mounted or accessible")
                logging.error("Please verify S: drive is mounted and writable")
            return False
    
    def validate_configuration(self) -> Tuple[bool, str]:
        """Validate the pipeline configuration and return status with message."""
        try:
            # Check base directory accessibility
            if not self.base_working_dir.exists():
                if self.using_s_drive:
                    return False, f"S: drive not accessible at {self.base_working_dir}. Please verify mount."
                else:
                    return False, f"Working directory not accessible at {self.base_working_dir}"
            
            # Test write permissions
            test_file = self.base_working_dir / ".pipeline_test"
            try:
                test_file.touch()
                test_file.unlink()
            except (OSError, PermissionError):
                return False, f"No write permission to {self.base_working_dir}"
            
            # Create directories
            if not self.create_directories():
                return False, "Failed to create required directories"
            
            status_msg = f"Using {'S: drive' if self.using_s_drive else 'local directory'} at {self.base_working_dir}"
            return True, status_msg
            
        except Exception as e:
            return False, f"Configuration validation failed: {e}"
    
    def get_scraper_config(self) -> Dict:
        """Get configuration for the scraper component."""
        return {
            "download_directory": str(self.scraper_output_dir),
            "max_workers": self.scraper_workers,
            "use_shared_driver": self.use_shared_driver,
            "manual_login": self.manual_login,
            "platform": self.platform,
            "is_wsl": self.is_wsl
        }
    
    def get_processor_config(self) -> Dict:
        """Get configuration for the processor component."""
        return {
            "input_dir": str(self.processor_input_dir),
            "output_dir": str(self.processor_output_dir),
            "mode": self.enhancement_mode,
            "language": self.language,
            "force_ocr": self.force_ocr
        }


class PipelineProgress:
    """
    Progress tracking and coordination between scraper and processor operations.
    """
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.start_time = datetime.now()
        self.progress_file = log_dir / f"pipeline_progress_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        
        self.state = {
            "pipeline_id": self.start_time.isoformat(),
            "start_time": self.start_time.isoformat(),
            "current_phase": "initialization",
            "scraper_stats": {
                "urls_processed": 0,
                "files_downloaded": 0,
                "failed_downloads": 0
            },
            "processor_stats": {
                "files_processed": 0,
                "successful_enhancements": 0,
                "failed_enhancements": 0
            },
            "completed_files": [],
            "failed_files": [],
            "current_operation": ""
        }
        
        self._save_progress()
    
    def update_phase(self, phase: str):
        """Update the current pipeline phase."""
        self.state["current_phase"] = phase
        self.state["current_operation"] = f"Entering {phase} phase"
        self._save_progress()
    
    def update_scraper_progress(self, urls_processed: int = 0, files_downloaded: int = 0, failed_downloads: int = 0):
        """Update scraper progress statistics."""
        if urls_processed > 0:
            self.state["scraper_stats"]["urls_processed"] += urls_processed
        if files_downloaded > 0:
            self.state["scraper_stats"]["files_downloaded"] += files_downloaded
        if failed_downloads > 0:
            self.state["scraper_stats"]["failed_downloads"] += failed_downloads
        
        self._save_progress()
    
    def update_processor_progress(self, files_processed: int = 0, successful: int = 0, failed: int = 0):
        """Update processor progress statistics."""
        if files_processed > 0:
            self.state["processor_stats"]["files_processed"] += files_processed
        if successful > 0:
            self.state["processor_stats"]["successful_enhancements"] += successful
        if failed > 0:
            self.state["processor_stats"]["failed_enhancements"] += failed
        
        self._save_progress()
    
    def add_completed_file(self, original_path: str, enhanced_path: str):
        """Record a successfully completed file."""
        self.state["completed_files"].append({
            "original_path": original_path,
            "enhanced_path": enhanced_path,
            "completed_at": datetime.now().isoformat()
        })
        self._save_progress()
    
    def add_failed_file(self, file_path: str, error: str):
        """Record a failed file."""
        self.state["failed_files"].append({
            "file_path": file_path,
            "error": error,
            "failed_at": datetime.now().isoformat()
        })
        self._save_progress()
    
    def update_current_operation(self, operation: str):
        """Update the current operation description."""
        self.state["current_operation"] = operation
        self._save_progress()
    
    def _save_progress(self):
        """Save current progress to disk."""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.warning(f"Failed to save progress: {e}")
    
    def finalize(self) -> Dict:
        """Finalize progress tracking and return summary."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        self.state.update({
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "current_phase": "completed",
            "current_operation": "Pipeline completed"
        })
        
        self._save_progress()
        return self.state


class ScraperProcessorPipeline:
    """
    Unified pipeline that coordinates document scraping and accessibility processing.
    
    This class provides a seamless workflow from document acquisition to
    accessibility enhancement, supporting both single URLs and batch operations.
    """
    
    def __init__(self, config: Optional[CrossPlatformPipelineConfig] = None):
        self.config = config or CrossPlatformPipelineConfig()
        self.logger = self._setup_logging()
        self.progress: Optional[PipelineProgress] = None
        self.enhancement_service: Optional[EnhancementService] = None
        self.duplicate_manager: Optional[DuplicateDetectionManager] = None
    
    def _setup_logging(self) -> logging.Logger:
        """Set up comprehensive logging for the pipeline."""
        # Ensure log directory exists
        self.config.pipeline_logs_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.config.pipeline_logs_dir / f"pipeline_{timestamp}.log"
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Configure logger
        logger = logging.getLogger('ScraperProcessorPipeline')
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def initialize_pipeline(self) -> bool:
        """Initialize the pipeline infrastructure."""
        try:
            self.logger.info("🚀 Initializing Scraper-Processor Pipeline")
            self.logger.info(f"Platform: {self.config.platform} {'(WSL)' if self.config.is_wsl else ''}")
            
            # Validate configuration and directory setup
            config_valid, config_msg = self.config.validate_configuration()
            if not config_valid:
                self.logger.error(f"❌ Configuration validation failed: {config_msg}")
                return False
            
            self.logger.info(f"✅ {config_msg}")
            
            # Initialize progress tracking
            self.progress = PipelineProgress(self.config.pipeline_logs_dir)
            self.progress.update_phase("initialization")
            
            # Initialize enhancement service
            self.enhancement_service = EnhancementService()
            
            # Initialize duplicate detection if enabled
            if self.config.enable_duplicate_detection:
                self.duplicate_manager = DuplicateDetectionManager(self.config.base_working_dir)
                stats = self.duplicate_manager.get_processing_statistics()
                self.logger.info(f"📊 Duplicate detection enabled - {stats.get('total_files', 0)} tracked files")
            
            self.logger.info("✅ Pipeline initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline initialization failed: {e}")
            return False
    
    def scrape_urls(self, urls: Union[str, List[str]], username: Optional[str] = None, password: Optional[str] = None) -> Tuple[int, int]:
        """
        Scrape documents from URL(s).
        
        Returns:
            Tuple of (successful_downloads, failed_downloads)
        """
        if not self.progress:
            raise RuntimeError("Pipeline not initialized")
        
        self.progress.update_phase("scraping")
        
        # Normalize URLs to list
        if isinstance(urls, str):
            url_list = [urls]
        else:
            url_list = urls
        
        self.logger.info(f"📥 Starting document scraping for {len(url_list)} URL(s)")
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, url in enumerate(url_list):
            self.progress.update_current_operation(f"Scraping URL {i+1}/{len(url_list)}: {url}")
            self.logger.info(f"Processing URL {i+1}/{len(url_list)}: {url}")
            
            try:
                # Use optimized download strategy if enabled
                if self.config.use_optimized_downloads:
                    success_count, failed_count = optimize_purdue_download(
                        base_url=url,
                        download_dir=str(self.config.scraper_output_dir),
                        username=username,
                        password=password,
                        use_optimized_strategy=True,
                        manual_login=self.config.manual_login
                    )
                    success = success_count > 0
                else:
                    # Fall back to original scraper
                    success = process_purdue_library_content(
                        base_url=url,
                        username=username,
                        password=password,
                        custom_download_dir=str(self.config.scraper_output_dir),
                        shared_driver=self.config.use_shared_driver
                    )
                
                if success:
                    successful_downloads += 1
                    self.progress.update_scraper_progress(urls_processed=1, files_downloaded=1)
                    self.logger.info(f"✅ Successfully scraped: {url}")
                else:
                    failed_downloads += 1
                    self.progress.update_scraper_progress(urls_processed=1, failed_downloads=1)
                    self.logger.error(f"❌ Failed to scrape: {url}")
                    
            except Exception as e:
                failed_downloads += 1
                self.progress.update_scraper_progress(urls_processed=1, failed_downloads=1)
                self.logger.error(f"❌ Exception scraping {url}: {e}")
        
        self.logger.info(f"📥 Scraping completed: {successful_downloads} successful, {failed_downloads} failed")
        return successful_downloads, failed_downloads
    
    def process_scraped_documents(self) -> Tuple[int, int]:
        """
        Process all documents in the scraper output directory.
        
        Returns:
            Tuple of (successful_enhancements, failed_enhancements)
        """
        if not self.progress or not self.enhancement_service:
            raise RuntimeError("Pipeline not initialized")
        
        self.progress.update_phase("processing")
        
        # Find all PDF files in the scraper output directory
        pdf_files = list(self.config.processor_input_dir.glob("**/*.pdf"))
        
        if not pdf_files:
            self.logger.warning("No PDF files found to process")
            return 0, 0
        
        self.logger.info(f"📝 Starting accessibility enhancement for {len(pdf_files)} document(s)")
        
        successful_enhancements = 0
        failed_enhancements = 0
        
        for i, input_file in enumerate(pdf_files):
            # Create relative path structure to preserve organization
            relative_path = input_file.relative_to(self.config.processor_input_dir)
            output_subdir = self.config.processor_output_dir / relative_path.parent
            output_subdir.mkdir(parents=True, exist_ok=True)
            output_file = output_subdir / f"{input_file.stem}_enhanced.pdf"
            
            self.progress.update_current_operation(f"Processing document {i+1}/{len(pdf_files)}: {input_file.name}")
            self.logger.info(f"Processing document {i+1}/{len(pdf_files)}: {input_file.name}")
            
            # Check for duplicates if enabled
            if self.duplicate_manager and self.config.skip_existing_files:
                is_duplicate, existing_record = self.duplicate_manager.is_file_already_processed(input_file)
                if is_duplicate and existing_record:
                    if existing_record.processing_status == "enhanced" and existing_record.enhanced_path:
                        enhanced_exists = Path(existing_record.enhanced_path).exists()
                        if enhanced_exists:
                            self.logger.info(f"⏭️  Skipping already enhanced file: {input_file.name}")
                            successful_enhancements += 1
                            self.progress.update_processor_progress(files_processed=1, successful=1)
                            self.progress.add_completed_file(str(input_file), existing_record.enhanced_path)
                            continue
            
            try:
                # Prepare enhancement parameters
                enhancement_kwargs = {
                    "language": self.config.language,
                    "title": None,  # Will be extracted from document
                    "author": None,  # Will be extracted from document
                }
                
                success = self.enhancement_service.enhance_document(
                    input_path=input_file,
                    output_path=output_file,
                    mode=self.config.enhancement_mode,
                    **enhancement_kwargs
                )
                
                if success:
                    successful_enhancements += 1
                    self.progress.update_processor_progress(files_processed=1, successful=1)
                    self.progress.add_completed_file(str(input_file), str(output_file))
                    
                    # Record enhanced file in duplicate detection
                    if self.duplicate_manager:
                        self.duplicate_manager.record_enhanced_file(
                            input_file, output_file, self.config.platform
                        )
                    
                    self.logger.info(f"✅ Successfully enhanced: {input_file.name}")
                else:
                    failed_enhancements += 1
                    self.progress.update_processor_progress(files_processed=1, failed=1)
                    self.progress.add_failed_file(str(input_file), "Enhancement service returned False")
                    self.logger.error(f"❌ Failed to enhance: {input_file.name}")
                    
            except Exception as e:
                failed_enhancements += 1
                self.progress.update_processor_progress(files_processed=1, failed=1)
                self.progress.add_failed_file(str(input_file), str(e))
                self.logger.error(f"❌ Exception processing {input_file.name}: {e}")
        
        self.logger.info(f"📝 Processing completed: {successful_enhancements} successful, {failed_enhancements} failed")
        return successful_enhancements, failed_enhancements
    
    def execute_full_pipeline(self, urls: Union[str, List[str]], username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """
        Execute the complete scraper-processor pipeline.
        
        Returns:
            Dictionary with pipeline execution results
        """
        try:
            # Initialize pipeline
            if not self.initialize_pipeline():
                raise RuntimeError("Pipeline initialization failed")
            
            self.logger.info("🚀 Starting full scraper-processor pipeline execution")
            
            # Phase 1: Scraping
            scrape_success, scrape_failed = self.scrape_urls(urls, username, password)
            
            # Phase 2: Processing (only if we have documents)
            if scrape_success > 0:
                process_success, process_failed = self.process_scraped_documents()
            else:
                self.logger.warning("No documents were successfully scraped, skipping processing phase")
                process_success, process_failed = 0, 0
            
            # Finalize and generate report
            self.progress.update_phase("finalizing")
            final_results = self.progress.finalize()
            
            # Summary
            total_success = min(scrape_success, process_success) if process_success > 0 else 0
            
            self.logger.info("=" * 80)
            self.logger.info("🎯 Pipeline Execution Summary")
            self.logger.info(f"📥 Scraping: {scrape_success} successful, {scrape_failed} failed")
            self.logger.info(f"📝 Processing: {process_success} successful, {process_failed} failed")
            self.logger.info(f"✅ End-to-end successful: {total_success}")
            self.logger.info(f"📁 Enhanced documents: {self.config.processor_output_dir}")
            self.logger.info(f"📄 Detailed logs: {self.config.pipeline_logs_dir}")
            self.logger.info("=" * 80)
            
            return {
                "success": True,
                "scraping": {"successful": scrape_success, "failed": scrape_failed},
                "processing": {"successful": process_success, "failed": process_failed},
                "end_to_end_successful": total_success,
                "output_directory": str(self.config.processor_output_dir),
                "progress_details": final_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline execution failed: {e}")
            if self.progress:
                self.progress.add_failed_file("pipeline", str(e))
                final_results = self.progress.finalize()
            else:
                final_results = {}
            
            return {
                "success": False,
                "error": str(e),
                "progress_details": final_results
            }


def main():
    """CLI entry point for the unified scraper-processor pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified Scraper-Processor Pipeline')
    parser.add_argument('--url', help='Single URL to scrape and process')
    parser.add_argument('--urls', help='File containing list of URLs to process')
    parser.add_argument('--working-dir', help='Base working directory for pipeline operations')
    parser.add_argument('--username', help='Username for authentication')
    parser.add_argument('--password', help='Password for authentication')
    parser.add_argument('--mode', default='academic', help='Processing mode (default: academic)')
    parser.add_argument('--language', default='en-US', help='Document language (default: en-US)')
    parser.add_argument('--no-ocr', action='store_true', help='Disable OCR processing')
    parser.add_argument('--workers', type=int, default=3, help='Number of scraper workers (default: 3)')
    parser.add_argument('--force-local', action='store_true', help='Force use of local directory instead of S: drive')
    parser.add_argument('--legacy-scraper', action='store_true', help='Use legacy scraper instead of optimized downloader')
    parser.add_argument('--manual-login', action='store_true', help='Enable manual login mode - browser will pause for credential entry')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate arguments
    if not args.url and not args.urls:
        parser.error("Either --url or --urls must be specified")
    
    # Prepare URLs
    if args.url:
        urls = [args.url]
    else:
        try:
            with open(args.urls, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        except Exception as e:
            print(f"Error reading URLs file: {e}")
            return 1
    
    # Create configuration
    config = CrossPlatformPipelineConfig(
        base_working_dir=args.working_dir,
        force_local=args.force_local or (args.working_dir is not None)  # Force local if custom dir specified or explicitly requested
    )
    config.enhancement_mode = args.mode
    config.language = args.language
    config.force_ocr = not args.no_ocr
    config.scraper_workers = args.workers
    config.use_optimized_downloads = not args.legacy_scraper
    config.manual_login = args.manual_login
    
    # Create and execute pipeline
    pipeline = ScraperProcessorPipeline(config)
    
    # Get credentials if needed
    username = args.username
    password = args.password
    
    # Handle credential input based on login mode
    if args.manual_login:
        print("Manual login mode enabled - credentials will be entered in browser")
        print("No credential input needed - you will login manually in the browser")
        # In manual login mode, credentials are optional fallbacks
        username = None
        password = None
    else:
        # Traditional credential input
        if not username:
            username = input("Enter username (optional): ").strip() or None
        if not password and username:
            import getpass
            password = getpass.getpass("Enter password: ")
    
    # Execute pipeline
    results = pipeline.execute_full_pipeline(urls, username, password)
    
    if results["success"]:
        print(f"\n✅ Pipeline completed successfully!")
        print(f"Enhanced documents available in: {results['output_directory']}")
        return 0
    else:
        print(f"\n❌ Pipeline failed: {results.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())