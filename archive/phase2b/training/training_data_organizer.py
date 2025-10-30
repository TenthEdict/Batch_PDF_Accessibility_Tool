#!/usr/bin/env python3
"""
Training Data Organizer for Accessibility Compliance Learning

This module organizes compliant PDF datasets for training machine learning models
to automatically generate WCAG/PDF-UA/ADA compliant accessibility structures.

Key Capabilities:
- Dataset validation and integrity checking
- Train/validation/test splits with configurable ratios
- Metadata extraction and manifest generation  
- Progress tracking and comprehensive error handling
- Integration with existing Phase 2B infrastructure

Integration Points:
- CLI compatibility with organize-training-data command
- AccessibilityDataExtractor coordination
- FAISS vector database preparation
- Hierarchical cache system compatibility
"""

import logging
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import time
import random
from collections import defaultdict

# PDF processing imports (existing infrastructure)
try:
    import fitz  # PyMuPDF
    PDF_DEPS_AVAILABLE = True
except ImportError:
    PDF_DEPS_AVAILABLE = False
    fitz = None

logger = logging.getLogger(__name__)


@dataclass
class DatasetStatistics:
    """Statistics for training dataset organization."""
    
    total_files: int
    valid_files: int
    invalid_files: int
    train_files: int
    validation_files: int
    test_files: int
    total_size_mb: float
    avg_file_size_mb: float
    organization_time_seconds: float
    
    
@dataclass
class TrainingManifest:
    """Manifest for training dataset configuration."""
    
    dataset_name: str
    organization_timestamp: float
    dataset_statistics: DatasetStatistics
    train_ratio: float
    validation_ratio: float
    test_ratio: float
    source_directory: str
    output_directory: str
    file_validation_criteria: Dict[str, Any]
    metadata_sample_size: int


class TrainingDataOrganizer:
    """
    Organizes compliant PDF datasets for accessibility training.
    
    Provides comprehensive dataset management including validation,
    splitting, and manifest generation optimized for machine learning
    workflows and Phase 2B infrastructure integration.
    """
    
    def __init__(self, source_dir: Path, output_dir: Path):
        """
        Initialize the training data organizer.
        
        Args:
            source_dir: Directory containing 1600+ compliant PDF files
            output_dir: Directory for organized training data
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        
        # Validation criteria
        self.file_validation_criteria = {
            'min_file_size_bytes': 1024,  # 1KB minimum
            'max_file_size_bytes': 100 * 1024 * 1024,  # 100MB maximum
            'required_extensions': ['.pdf'],
            'encoding_validation': True
        }
        
        # Organization statistics
        self.statistics = None
        
        logger.info(f"TrainingDataOrganizer initialized: {source_dir} -> {output_dir}")
    
    def validate_dataset(self) -> Tuple[List[Path], List[Tuple[Path, str]]]:
        """
        Validate all PDF files in the source directory.
        
        Returns:
            Tuple of (valid_files, invalid_files_with_reasons)
        """
        logger.info("Starting dataset validation...")
        
        valid_files = []
        invalid_files = []
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory does not exist: {self.source_dir}")
        
        # Find all PDF files
        pdf_files = list(self.source_dir.rglob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files for validation")
        
        for pdf_file in pdf_files:
            try:
                validation_result = self._validate_single_file(pdf_file)
                if validation_result[0]:
                    valid_files.append(pdf_file)
                else:
                    invalid_files.append((pdf_file, validation_result[1]))
                    
            except Exception as e:
                invalid_files.append((pdf_file, f"Validation error: {str(e)}"))
        
        logger.info(f"Validation complete: {len(valid_files)} valid, {len(invalid_files)} invalid")
        return valid_files, invalid_files
    
    def _validate_single_file(self, pdf_file: Path) -> Tuple[bool, str]:
        """
        Validate a single PDF file.
        
        Args:
            pdf_file: Path to PDF file
            
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        # Check file size
        file_size = pdf_file.stat().st_size
        if file_size < self.file_validation_criteria['min_file_size_bytes']:
            return False, "File too small"
        if file_size > self.file_validation_criteria['max_file_size_bytes']:
            return False, "File too large"
        
        # Check file extension
        if pdf_file.suffix.lower() not in self.file_validation_criteria['required_extensions']:
            return False, "Invalid file extension"
        
        # Check PDF integrity if PyMuPDF available
        if PDF_DEPS_AVAILABLE:
            try:
                doc = fitz.open(pdf_file)
                if doc.page_count == 0:
                    doc.close()
                    return False, "Empty PDF document"
                doc.close()
            except Exception as e:
                return False, f"PDF structure error: {str(e)}"
        
        return True, "Valid"
    
    def create_training_splits(self, 
                             valid_files: List[Path],
                             train_ratio: float = 0.7,
                             val_ratio: float = 0.15,
                             test_ratio: float = 0.15) -> Dict[str, List[Path]]:
        """
        Create train/validation/test splits from valid files.
        
        Args:
            valid_files: List of validated PDF files
            train_ratio: Training set ratio
            val_ratio: Validation set ratio  
            test_ratio: Test set ratio
            
        Returns:
            Dictionary with train, validation, and test file lists
        """
        # Validate ratios
        total_ratio = train_ratio + val_ratio + test_ratio
        if abs(total_ratio - 1.0) > 1e-6:
            raise ValueError(f"Ratios must sum to 1.0, got {total_ratio}")
        
        # Shuffle files for random distribution
        shuffled_files = valid_files.copy()
        random.shuffle(shuffled_files)
        
        total_files = len(shuffled_files)
        train_count = int(total_files * train_ratio)
        val_count = int(total_files * val_ratio)
        test_count = total_files - train_count - val_count  # Ensure all files used
        
        splits = {
            'train': shuffled_files[:train_count],
            'validation': shuffled_files[train_count:train_count + val_count],
            'test': shuffled_files[train_count + val_count:]
        }
        
        logger.info(f"Created splits: train={len(splits['train'])}, "
                   f"validation={len(splits['validation'])}, test={len(splits['test'])}")
        
        return splits
    
    def organize_files_to_splits(self, splits: Dict[str, List[Path]]) -> Dict[str, Path]:
        """
        Organize files into train/validation/test directories.
        
        Args:
            splits: Dictionary with file splits
            
        Returns:
            Dictionary with split directory paths
        """
        split_dirs = {}
        
        for split_name, file_list in splits.items():
            split_dir = self.output_dir / split_name
            split_dir.mkdir(parents=True, exist_ok=True)
            split_dirs[split_name] = split_dir
            
            logger.info(f"Copying {len(file_list)} files to {split_name} directory")
            
            for source_file in file_list:
                dest_file = split_dir / source_file.name
                shutil.copy2(source_file, dest_file)
        
        logger.info("File organization to splits completed")
        return split_dirs    
    def generate_manifest(self, 
                         statistics: DatasetStatistics,
                         train_ratio: float,
                         val_ratio: float, 
                         test_ratio: float,
                         metadata_sample_size: int) -> TrainingManifest:
        """
        Generate training manifest with dataset configuration.
        
        Args:
            statistics: Dataset statistics
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            metadata_sample_size: Sample size for metadata extraction
            
        Returns:
            TrainingManifest object
        """
        manifest = TrainingManifest(
            dataset_name=f"accessibility_training_{int(time.time())}",
            organization_timestamp=time.time(),
            dataset_statistics=statistics,
            train_ratio=train_ratio,
            validation_ratio=val_ratio,
            test_ratio=test_ratio,
            source_directory=str(self.source_dir),
            output_directory=str(self.output_dir),
            file_validation_criteria=self.file_validation_criteria,
            metadata_sample_size=metadata_sample_size
        )
        
        return manifest
    
    def save_manifest(self, manifest: TrainingManifest) -> Path:
        """
        Save training manifest to JSON file.
        
        Args:
            manifest: TrainingManifest to save
            
        Returns:
            Path to saved manifest file
        """
        manifest_file = self.output_dir / "training_manifest.json"
        
        # Convert dataclasses to dict for JSON serialization
        manifest_dict = asdict(manifest)
        
        with open(manifest_file, 'w') as f:
            json.dump(manifest_dict, f, indent=2)
        
        logger.info(f"Training manifest saved: {manifest_file}")
        return manifest_file
    
    def extract_sample_metadata(self, valid_files: List[Path], sample_size: int) -> Dict[str, Any]:
        """
        Extract metadata from a sample of valid files for analysis.
        
        Args:
            valid_files: List of validated PDF files
            sample_size: Number of files to sample for metadata
            
        Returns:
            Dictionary with metadata analysis
        """
        if not PDF_DEPS_AVAILABLE:
            logger.warning("PyMuPDF not available - skipping metadata extraction")
            return {"status": "skipped", "reason": "PyMuPDF not available"}
        
        sample_files = random.sample(valid_files, min(sample_size, len(valid_files)))
        metadata_analysis = {
            "sample_size": len(sample_files),
            "total_files": len(valid_files),
            "file_metadata": [],
            "aggregate_stats": defaultdict(int)
        }
        
        logger.info(f"Extracting metadata from {len(sample_files)} sample files")
        
        for pdf_file in sample_files:
            try:
                file_metadata = self._extract_file_metadata(pdf_file)
                metadata_analysis["file_metadata"].append(file_metadata)
                
                # Update aggregate statistics
                metadata_analysis["aggregate_stats"]["total_pages"] += file_metadata.get("page_count", 0)
                if file_metadata.get("has_text", False):
                    metadata_analysis["aggregate_stats"]["files_with_text"] += 1
                if file_metadata.get("has_images", False):
                    metadata_analysis["aggregate_stats"]["files_with_images"] += 1
                    
            except Exception as e:
                logger.warning(f"Failed to extract metadata from {pdf_file}: {e}")
        
        # Calculate averages
        if metadata_analysis["file_metadata"]:
            total_pages = metadata_analysis["aggregate_stats"]["total_pages"]
            metadata_analysis["aggregate_stats"]["avg_pages_per_file"] = (
                total_pages / len(metadata_analysis["file_metadata"])
            )
        
        return metadata_analysis
    
    def _extract_file_metadata(self, pdf_file: Path) -> Dict[str, Any]:
        """
        Extract metadata from a single PDF file.
        
        Args:
            pdf_file: Path to PDF file
            
        Returns:
            Dictionary with file metadata
        """
        metadata = {
            "filename": pdf_file.name,
            "file_size_bytes": pdf_file.stat().st_size,
            "file_size_mb": pdf_file.stat().st_size / (1024 * 1024)
        }
        
        try:
            doc = fitz.open(pdf_file)
            
            # Basic document info
            metadata["page_count"] = doc.page_count
            metadata["has_text"] = False
            metadata["has_images"] = False
            metadata["pdf_metadata"] = doc.metadata
            
            # Sample first few pages for content analysis
            sample_pages = min(3, doc.page_count)
            for page_num in range(sample_pages):
                page = doc[page_num]
                
                # Check for text content
                if page.get_text().strip():
                    metadata["has_text"] = True
                
                # Check for images
                if page.get_images():
                    metadata["has_images"] = True
            
            doc.close()
            
        except Exception as e:
            metadata["extraction_error"] = str(e)
        
        return metadata
    
    def save_metadata_analysis(self, metadata_analysis: Dict[str, Any]) -> Path:
        """
        Save metadata analysis to JSON file.
        
        Args:
            metadata_analysis: Metadata analysis dictionary
            
        Returns:
            Path to saved analysis file
        """
        metadata_dir = self.output_dir / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        
        analysis_file = metadata_dir / "training_metadata_analysis.json"
        
        with open(analysis_file, 'w') as f:
            json.dump(metadata_analysis, f, indent=2)
        
        logger.info(f"Metadata analysis saved: {analysis_file}")
        return analysis_file
    
    def organize_complete_dataset(self, 
                                metadata_sample: int = 50,
                                train_ratio: float = 0.7,
                                val_ratio: float = 0.15,
                                test_ratio: float = 0.15) -> bool:
        """
        Execute complete dataset organization pipeline.
        
        Args:
            metadata_sample: Number of files for metadata extraction
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            
        Returns:
            True if successful, False otherwise
        """
        try:
            start_time = time.time()
            logger.info("Starting complete dataset organization pipeline")
            
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: Validate dataset
            valid_files, invalid_files = self.validate_dataset()
            
            if not valid_files:
                logger.error("No valid files found in dataset")
                return False
            
            # Step 2: Create training splits
            splits = self.create_training_splits(valid_files, train_ratio, val_ratio, test_ratio)
            
            # Step 3: Organize files to directories
            split_dirs = self.organize_files_to_splits(splits)
            
            # Step 4: Extract sample metadata
            metadata_analysis = self.extract_sample_metadata(valid_files, metadata_sample)
            metadata_file = self.save_metadata_analysis(metadata_analysis)
            
            # Step 5: Calculate statistics
            organization_time = time.time() - start_time
            total_size_bytes = sum(f.stat().st_size for f in valid_files)
            
            statistics = DatasetStatistics(
                total_files=len(valid_files) + len(invalid_files),
                valid_files=len(valid_files),
                invalid_files=len(invalid_files),
                train_files=len(splits['train']),
                validation_files=len(splits['validation']),
                test_files=len(splits['test']),
                total_size_mb=total_size_bytes / (1024 * 1024),
                avg_file_size_mb=(total_size_bytes / len(valid_files)) / (1024 * 1024),
                organization_time_seconds=organization_time
            )
            
            # Step 6: Generate and save manifest
            manifest = self.generate_manifest(
                statistics, train_ratio, val_ratio, test_ratio, metadata_sample
            )
            manifest_file = self.save_manifest(manifest)
            
            # Step 7: Log completion summary
            logger.info("Dataset organization completed successfully")
            logger.info(f"Total files processed: {statistics.total_files}")
            logger.info(f"Valid files: {statistics.valid_files}")
            logger.info(f"Invalid files: {statistics.invalid_files}")
            logger.info(f"Organization time: {organization_time:.2f} seconds")
            logger.info(f"Training manifest: {manifest_file}")
            logger.info(f"Metadata analysis: {metadata_file}")
            
            self.statistics = statistics
            return True
            
        except Exception as e:
            logger.error(f"Dataset organization failed: {str(e)}")
            return False


# CLI Integration and Example Usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize training data for accessibility compliance")
    parser.add_argument("source_dir", help="Source directory with PDF files")
    parser.add_argument("output_dir", help="Output directory for organized data")
    parser.add_argument("--train-ratio", type=float, default=0.7, help="Training set ratio")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="Validation set ratio")
    parser.add_argument("--test-ratio", type=float, default=0.15, help="Test set ratio")
    parser.add_argument("--metadata-sample", type=int, default=50, help="Metadata sample size")
    
    args = parser.parse_args()
    
    organizer = TrainingDataOrganizer(Path(args.source_dir), Path(args.output_dir))
    success = organizer.organize_complete_dataset(
        args.metadata_sample, args.train_ratio, args.val_ratio, args.test_ratio
    )
    
    exit(0 if success else 1)
