# src/accessibility_checker/build/process.py

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from ..utils.code_analyzer import CodeAnalyzer
from ..utils.config import ConfigurationManager
from ..core.batch import BatchPDFProcessor

class BuildProcess:
    """Manages the enhanced build process including code analysis."""
    
    def __init__(
        self,
        project_root: Path,
        anthropic_api_key: Optional[str] = None,
        config_path: Optional[str] = None
    ):
        self.project_root = project_root
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        self.config_path = config_path or str(project_root / "config.yaml")
        self.logger = logging.getLogger(__name__)
        
        # Setup directories
        self.input_dir = project_root / "input"
        self.output_dir = project_root / "output"
        self.analysis_dir = self.output_dir / "analysis"
        
        # Create necessary directories
        self._setup_directories()
        
    def _setup_directories(self):
        """Create necessary directories if they don't exist."""
        dirs = [
            self.input_dir,
            self.output_dir,
            self.analysis_dir,
            self.output_dir / "corrections",
            self.output_dir / "reports",
            self.output_dir / "processed_pdfs",
            self.output_dir / "logs",
            self.output_dir / "ocr_results",
            self.output_dir / "tagged",
            self.output_dir / "final"
        ]
        
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)

    async def run_code_analysis(self) -> Dict:
        """Run code analysis on the project."""
        if not self.anthropic_api_key:
            self.logger.warning("No Anthropic API key provided. Skipping code analysis.")
            return {'status': 'skipped', 'reason': 'No API key'}
            
        try:
            analyzer = CodeAnalyzer(self.anthropic_api_key)
            results = await analyzer.analyze_codebase(str(self.project_root))
            
            # Save analysis results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.analysis_dir / f"code_analysis_{timestamp}.json"
            
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
                
            self.logger.info(f"Code analysis completed. Results saved to: {output_file}")
            return {'status': 'success', 'output_file': str(output_file)}
            
        except Exception as e:
            self.logger.error(f"Code analysis failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}

    async def process_documents(self) -> Dict:
        """Process PDF documents using existing batch processor."""
        try:
            config_manager = ConfigurationManager(self.config_path)
            processing_config = config_manager.get_processing_config()
            
            processor = BatchPDFProcessor(
                str(self.input_dir),
                str(self.output_dir),
                max_workers=processing_config.max_workers
            )
            
            summary_df = processor.process_directory()
            
            return {
                'status': 'success',
                'files_processed': len(summary_df),
                'success_count': sum(summary_df['status'] == 'success'),
                'failed_count': sum(summary_df['status'] == 'failed')
            }
            
        except Exception as e:
            self.logger.error(f"Document processing failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}

    async def run_full_build(self) -> Dict:
        """Run the complete build process."""
        build_results = {
            'timestamp': datetime.now().isoformat(),
            'steps': {}
        }
        
        try:
            # Step 1: Code Analysis
            self.logger.info("Starting code analysis...")
            build_results['steps']['code_analysis'] = await self.run_code_analysis()
            
            # Step 2: Document Processing
            self.logger.info("Starting document processing...")
            build_results['steps']['document_processing'] = await self.process_documents()
            
            # Determine overall build status
            failed_steps = [
                step for step, result in build_results['steps'].items()
                if result.get('status') == 'failed'
            ]
            
            build_results['status'] = 'failed' if failed_steps else 'success'
            if failed_steps:
                build_results['failed_steps'] = failed_steps
                
            # Save build report
            self._save_build_report(build_results)
            
            return build_results
            
        except Exception as e:
            self.logger.error(f"Build process failed: {str(e)}")
            build_results['status'] = 'failed'
            build_results['error'] = str(e)
            return build_results

    def _save_build_report(self, results: Dict):
        """Save build results to a report file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / "reports" / f"build_report_{timestamp}.json"
        
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        self.logger.info(f"Build report saved to: {report_file}")

async def main():
    """Main function to run the build process."""
    # Get project root (3 levels up from this file)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    
    # Initialize and run build process
    build_process = BuildProcess(project_root)
    results = await build_process.run_full_build()
    
    # Print summary
    print("\nBuild Process Summary:")
    print(f"Status: {results['status']}")
    
    if results['status'] == 'success':
        for step, step_results in results['steps'].items():
            print(f"\n{step.replace('_', ' ').title()}:")
            for key, value in step_results.items():
                print(f"  {key}: {value}")
    else:
        print("\nBuild failed:")
        if 'failed_steps' in results:
            print("Failed steps:", ", ".join(results['failed_steps']))
        if 'error' in results:
            print("Error:", results['error'])

if __name__ == "__main__":
    asyncio.run(main())
