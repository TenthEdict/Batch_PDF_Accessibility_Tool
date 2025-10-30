#!/usr/bin/env python3
"""
Training Data Organization Script

This script helps organize the 1600+ compliant PDF files for accessibility training.
Provides utilities for data preparation, validation, and batch processing setup.

Features:
- PDF file validation and organization
- Training/validation/test split creation
- Metadata extraction and cataloging
- Integration with AccessibilityDataExtractor

Usage:
    python organize_training_data.py --source /path/to/1600/pdfs --output data/training/accessibility
"""

import logging
import json
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import argparse
import random
from collections import defaultdict

# Import our accessibility extractor
try:
    from .accessibility_data_extractor import AccessibilityDataExtractor
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from processor.unified_project.src.training.accessibility_data_extractor import AccessibilityDataExtractor

logger = logging.getLogger(__name__)


class TrainingDataOrganizer:
    """Organize compliant PDF files for accessibility training."""
    
    def __init__(self, source_dir: Path, output_dir: Path):
        """
        Initialize training data organizer.
        
        Args:
            source_dir: Directory containing the 1600+ compliant PDF files
            output_dir: Directory to organize training data (data/training/accessibility)
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        
        # Create output structure
        self.compliant_pdfs_dir = self.output_dir / "compliant_pdfs"
        self.train_dir = self.output_dir / "train"
        self.validation_dir = self.output_dir / "validation" 
        self.test_dir = self.output_dir / "test"
        self.metadata_dir = self.output_dir / "metadata"
        
        # Create directories
        for dir_path in [self.compliant_pdfs_dir, self.train_dir, self.validation_dir, 
                        self.test_dir, self.metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        try:
            self.extractor = AccessibilityDataExtractor(self.output_dir)
        except Exception as e:
            logger.warning(f"AccessibilityDataExtractor initialization failed: {e}")
            self.extractor = None
        
        logger.info(f"TrainingDataOrganizer initialized:")
        logger.info(f"  Source: {self.source_dir}")
        logger.info(f"  Output: {self.output_dir}")
    
    def validate_source_pdfs(self) -> Tuple[List[Path], List[Path]]:
        """
        Validate PDF files in source directory and all subdirectories.
        
        Supports nested folder structures for easy organization of compliant PDFs.
        
        Returns:
            Tuple of (valid_pdfs, invalid_pdfs)
        """
        logger.info("Validating source PDF files (including subdirectories)...")
        
        # Find all PDF files recursively
        pdf_files = list(self.source_dir.glob("**/*.pdf"))
        
        # Log folder structure for user feedback
        folders_found = set()
        for pdf_file in pdf_files:
            relative_path = pdf_file.relative_to(self.source_dir)
            if len(relative_path.parts) > 1:  # File is in subdirectory
                folder_path = relative_path.parent
                folders_found.add(str(folder_path))
        
        if folders_found:
            logger.info(f"Found PDFs in {len(folders_found)} subdirectories:")
            for folder in sorted(folders_found):
                folder_pdfs = len(list(self.source_dir.glob(f"{folder}/*.pdf")))
                logger.info(f"  {folder}/: {folder_pdfs} PDFs")
        
        logger.info(f"Total PDF files found: {len(pdf_files)}")
        
        valid_pdfs = []
        invalid_pdfs = []
        
        for pdf_file in pdf_files:
            try:
                # Basic PDF validation
                import fitz
                doc = fitz.open(str(pdf_file))
                
                # Check if PDF has content
                if len(doc) > 0:
                    valid_pdfs.append(pdf_file)
                    logger.debug(f"✅ Valid: {pdf_file.relative_to(self.source_dir)}")
                else:
                    invalid_pdfs.append(pdf_file)
                    logger.debug(f"❌ Empty: {pdf_file.relative_to(self.source_dir)}")
                
                doc.close()
                
            except Exception as e:
                logger.warning(f"❌ Invalid PDF {pdf_file.relative_to(self.source_dir)}: {str(e)}")
                invalid_pdfs.append(pdf_file)
        
        logger.info(f"Validation complete: {len(valid_pdfs)} valid, {len(invalid_pdfs)} invalid")
        
        # Log folder-wise validation summary
        if folders_found:
            logger.info("Validation summary by folder:")
            for folder in sorted(folders_found):
                folder_files = [f for f in pdf_files if str(f.relative_to(self.source_dir)).startswith(folder)]
                folder_valid = [f for f in folder_files if f in valid_pdfs]
                logger.info(f"  {folder}/: {len(folder_valid)}/{len(folder_files)} valid")
        
        return valid_pdfs, invalid_pdfs
    
    def create_training_splits(self, pdf_files: List[Path], 
                             train_ratio: float = 0.7,
                             val_ratio: float = 0.15,
                             test_ratio: float = 0.15,
                             random_seed: int = 42) -> Dict[str, List[Path]]:
        """
        Create train/validation/test splits from PDF files.
        
        Args:
            pdf_files: List of valid PDF file paths
            train_ratio: Proportion for training (default: 0.7)
            val_ratio: Proportion for validation (default: 0.15) 
            test_ratio: Proportion for testing (default: 0.15)
            random_seed: Random seed for reproducible splits
            
        Returns:
            Dictionary with 'train', 'validation', 'test' file lists
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"
        
        logger.info(f"Creating training splits with ratios: train={train_ratio}, val={val_ratio}, test={test_ratio}")
        
        # Shuffle files with fixed seed for reproducibility
        random.seed(random_seed)
        shuffled_files = pdf_files.copy()
        random.shuffle(shuffled_files)
        
        total_files = len(shuffled_files)
        train_count = int(total_files * train_ratio)
        val_count = int(total_files * val_ratio)
        
        splits = {
            'train': shuffled_files[:train_count],
            'validation': shuffled_files[train_count:train_count + val_count],
            'test': shuffled_files[train_count + val_count:]
        }
        
        logger.info(f"Split sizes: train={len(splits['train'])}, "
                   f"validation={len(splits['validation'])}, test={len(splits['test'])}")
        
        return splits
    
    def copy_files_to_splits(self, splits: Dict[str, List[Path]]) -> bool:
        """Copy PDF files to their respective training split directories, preserving source organization info."""
        try:
            total_files = sum(len(file_list) for file_list in splits.values())
            logger.info(f"Copying {total_files} PDF files to training split directories...")
            
            for split_name, file_list in splits.items():
                split_dir = getattr(self, f"{split_name}_dir")
                
                logger.info(f"📁 Copying {len(file_list)} files to {split_name}/ directory")
                
                # Track source folder distribution
                source_folders = defaultdict(int)
                
                for pdf_file in file_list:
                    dest_file = split_dir / pdf_file.name
                    
                    # Track source folder for reporting
                    relative_path = pdf_file.relative_to(self.source_dir)
                    if len(relative_path.parts) > 1:
                        source_folder = str(relative_path.parent)
                        source_folders[source_folder] += 1
                    else:
                        source_folders['root'] += 1
                    
                    # Handle filename conflicts by adding a suffix
                    counter = 1
                    original_dest = dest_file
                    while dest_file.exists():
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest_file = split_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                        
                        if counter == 1:  # First conflict
                            logger.info(f"   📝 Renaming duplicate: {pdf_file.name} → {dest_file.name}")
                    
                    shutil.copy2(pdf_file, dest_file)
                
                # Log source folder distribution for this split
                if len(source_folders) > 1:
                    logger.info(f"   📊 {split_name.title()} set source distribution:")
                    for folder, count in sorted(source_folders.items()):
                        folder_display = folder if folder != 'root' else '(root directory)'
                        logger.info(f"      {folder_display}: {count} files")
                
                logger.info(f"✅ Completed copying {split_name} files")
            
            return True
            
        except Exception as e:
            logger.error(f"Error copying files to splits: {str(e)}")
            return False
    
    def analyze_folder_structure(self) -> Dict[str, Any]:
        """Analyze the folder structure of source PDFs for organization insights."""
        logger.info("Analyzing source folder structure...")
        
        pdf_files = list(self.source_dir.glob("**/*.pdf"))
        
        structure_analysis = {
            'total_pdfs': len(pdf_files),
            'folders': {},
            'max_depth': 0,
            'has_nested_structure': False
        }
        
        for pdf_file in pdf_files:
            relative_path = pdf_file.relative_to(self.source_dir)
            depth = len(relative_path.parts) - 1  # Subtract 1 for the file itself
            
            structure_analysis['max_depth'] = max(structure_analysis['max_depth'], depth)
            
            if depth > 0:
                structure_analysis['has_nested_structure'] = True
                folder_path = str(relative_path.parent)
                
                if folder_path not in structure_analysis['folders']:
                    structure_analysis['folders'][folder_path] = {
                        'pdf_count': 0,
                        'depth': depth
                    }
                
                structure_analysis['folders'][folder_path]['pdf_count'] += 1
            else:
                # File in root directory
                if 'root' not in structure_analysis['folders']:
                    structure_analysis['folders']['root'] = {
                        'pdf_count': 0,
                        'depth': 0
                    }
                structure_analysis['folders']['root']['pdf_count'] += 1
        
        # Log analysis results
        logger.info(f"📁 Folder structure analysis:")
        logger.info(f"   Total PDFs: {structure_analysis['total_pdfs']}")
        logger.info(f"   Maximum folder depth: {structure_analysis['max_depth']}")
        logger.info(f"   Nested structure: {'Yes' if structure_analysis['has_nested_structure'] else 'No'}")
        logger.info(f"   Folders found: {len(structure_analysis['folders'])}")
        
        if structure_analysis['folders']:
            logger.info(f"📊 PDF distribution by folder:")
            for folder, info in sorted(structure_analysis['folders'].items()):
                folder_display = folder if folder != 'root' else '(root directory)'
                logger.info(f"   {folder_display}: {info['pdf_count']} PDFs (depth: {info['depth']})")
        
        return structure_analysis
    
    def extract_batch_metadata(self, max_sample_size: int = 50) -> Dict[str, Any]:
        """
        Extract metadata from a sample of training files for analysis.
        
        Args:
            max_sample_size: Maximum number of files to sample for metadata extraction
            
        Returns:
            Dictionary containing batch metadata analysis
        """
        logger.info(f"Extracting metadata from sample of up to {max_sample_size} files...")
        
        if not self.extractor:
            logger.warning("AccessibilityDataExtractor not available, skipping metadata extraction")
            return {
                'sample_size': 0,
                'extraction_timestamp': 'N/A',
                'document_characteristics': {},
                'feature_analysis': {},
                'error': 'AccessibilityDataExtractor not available'
            }
        
        # Sample files from train directory
        train_files = list(self.train_dir.glob("*.pdf"))
        sample_files = train_files[:max_sample_size] if len(train_files) > max_sample_size else train_files
        
        # Extract profiles for sample
        profiles = []
        for pdf_file in sample_files:
            try:
                profile = self.extractor.extract_document_profile(pdf_file)
                if profile:
                    profiles.append(profile)
            except Exception as e:
                logger.warning(f"Failed to extract profile from {pdf_file.name}: {e}")
        
        # Analyze metadata patterns
        metadata_analysis = {
            'sample_size': len(profiles),
            'extraction_timestamp': str(self.extractor._generate_document_id(Path('timestamp'))),
            'document_characteristics': {
                'avg_page_count': sum(p.page_count for p in profiles) / len(profiles) if profiles else 0,
                'wcag_levels': defaultdict(int),
                'pdf_ua_versions': defaultdict(int),
                'languages': defaultdict(int),
                'compliance_patterns': defaultdict(int)
            },
            'feature_analysis': {
                'avg_feature_vector_length': 0,
                'feature_ranges': {}
            }
        }
        
        # Aggregate characteristics
        for profile in profiles:
            metadata_analysis['document_characteristics']['wcag_levels'][profile.wcag_level] += 1
            metadata_analysis['document_characteristics']['pdf_ua_versions'][profile.pdf_ua_version] += 1
            metadata_analysis['document_characteristics']['languages'][profile.language] += 1
            
            for pattern in profile.compliance_patterns:
                metadata_analysis['document_characteristics']['compliance_patterns'][pattern.content_type] += 1
        
        # Convert defaultdicts to regular dicts for JSON serialization
        for key in ['wcag_levels', 'pdf_ua_versions', 'languages', 'compliance_patterns']:
            metadata_analysis['document_characteristics'][key] = dict(
                metadata_analysis['document_characteristics'][key]
            )
        
        # Save metadata analysis
        metadata_file = self.metadata_dir / "training_metadata_analysis.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata_analysis, f, indent=2)
        
        logger.info(f"Saved metadata analysis: {metadata_file}")
        return metadata_analysis
        """
        Extract metadata from a sample of training files for analysis.
        
        Args:
            max_sample_size: Maximum number of files to sample for metadata extraction
            
        Returns:
            Dictionary containing batch metadata analysis
        """
        logger.info(f"Extracting metadata from sample of up to {max_sample_size} files...")
        
        if not self.extractor:
            logger.warning("AccessibilityDataExtractor not available, skipping metadata extraction")
            return {
                'sample_size': 0,
                'extraction_timestamp': 'N/A',
                'document_characteristics': {},
                'feature_analysis': {},
                'error': 'AccessibilityDataExtractor not available'
            }
        
        # Sample files from train directory
        train_files = list(self.train_dir.glob("*.pdf"))
        sample_files = train_files[:max_sample_size] if len(train_files) > max_sample_size else train_files
        
        # Extract profiles for sample
        profiles = []
        for pdf_file in sample_files:
            try:
                profile = self.extractor.extract_document_profile(pdf_file)
                if profile:
                    profiles.append(profile)
            except Exception as e:
                logger.warning(f"Failed to extract profile from {pdf_file.name}: {e}")
        
        # Analyze metadata patterns
        metadata_analysis = {
            'sample_size': len(profiles),
            'extraction_timestamp': str(self.extractor._generate_document_id(Path('timestamp'))),
            'document_characteristics': {
                'avg_page_count': sum(p.page_count for p in profiles) / len(profiles) if profiles else 0,
                'wcag_levels': defaultdict(int),
                'pdf_ua_versions': defaultdict(int),
                'languages': defaultdict(int),
                'compliance_patterns': defaultdict(int)
            },
            'feature_analysis': {
                'avg_feature_vector_length': 0,
                'feature_ranges': {}
            }
        }
        
        # Aggregate characteristics
        for profile in profiles:
            metadata_analysis['document_characteristics']['wcag_levels'][profile.wcag_level] += 1
            metadata_analysis['document_characteristics']['pdf_ua_versions'][profile.pdf_ua_version] += 1
            metadata_analysis['document_characteristics']['languages'][profile.language] += 1
            
            for pattern in profile.compliance_patterns:
                metadata_analysis['document_characteristics']['compliance_patterns'][pattern.content_type] += 1
        
        # Convert defaultdicts to regular dicts for JSON serialization
        for key in ['wcag_levels', 'pdf_ua_versions', 'languages', 'compliance_patterns']:
            metadata_analysis['document_characteristics'][key] = dict(
                metadata_analysis['document_characteristics'][key]
            )
        
        # Save metadata analysis
        metadata_file = self.metadata_dir / "training_metadata_analysis.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata_analysis, f, indent=2)
        
        logger.info(f"Saved metadata analysis: {metadata_file}")
        return metadata_analysis
    
    def create_training_manifest(self, splits: Dict[str, List[Path]], metadata: Dict[str, Any]) -> bool:
        """Create training manifest file with complete dataset information."""
        try:
            manifest = {
                'dataset_info': {
                    'total_files': sum(len(file_list) for file_list in splits.values()),
                    'split_sizes': {split: len(file_list) for split, file_list in splits.items()},
                    'source_directory': str(self.source_dir),
                    'organization_timestamp': str(self.extractor._generate_document_id(Path('manifest')) if self.extractor else 'N/A'),
                    'accessibility_focus': 'WCAG/PDF-UA/ADA compliance training'
                },
                'file_organization': {
                    'train_directory': str(self.train_dir),
                    'validation_directory': str(self.validation_dir),
                    'test_directory': str(self.test_dir),
                    'metadata_directory': str(self.metadata_dir)
                },
                'training_configuration': {
                    'feature_vector_size': 128,  # 32 existing + 96 accessibility
                    'target_compliance_standards': ['WCAG 2.1 AA', 'PDF/UA-1', 'Section 508'],
                    'ml_integration': 'Phase 2B FAISS vector database and hierarchical caching',
                    'expected_models': ['DocumentClassifier', 'TagTreePredictor', 'ComplianceValidator']
                },
                'metadata_sample': metadata
            }
            
            manifest_file = self.output_dir / "training_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Created training manifest: {manifest_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create training manifest: {str(e)}")
            return False
    
    def organize_complete_dataset(self, max_metadata_sample: int = 50) -> bool:
        """
        Complete dataset organization workflow with folder structure support.
        
        Args:
            max_metadata_sample: Maximum files for metadata extraction sample
            
        Returns:
            True if organization completed successfully
        """
        logger.info("Starting complete dataset organization...")
        
        # Step 0: Analyze folder structure for better user feedback
        structure_analysis = self.analyze_folder_structure()
        
        # Step 1: Validate source PDFs
        valid_pdfs, invalid_pdfs = self.validate_source_pdfs()
        
        if not valid_pdfs:
            logger.error("No valid PDF files found in source directory")
            return False
        
        if len(valid_pdfs) < 100:
            logger.warning(f"Only {len(valid_pdfs)} valid PDFs found. Consider adding more training data.")
        
        # Log folder organization benefits if applicable
        if structure_analysis['has_nested_structure']:
            logger.info("✅ Nested folder structure detected - this helps organize different types of compliant PDFs!")
            logger.info("   Training splits will preserve source folder distribution information.")
        
        # Step 2: Create training splits
        splits = self.create_training_splits(valid_pdfs)
        
        # Step 3: Copy files to split directories (with folder organization tracking)
        if not self.copy_files_to_splits(splits):
            logger.error("Failed to copy files to split directories")
            return False
        
        # Step 4: Extract metadata sample
        metadata = self.extract_batch_metadata(max_metadata_sample)
        
        # Step 5: Create training manifest (include folder structure info)
        manifest_data = {
            'splits': splits,
            'metadata': metadata,
            'folder_structure': structure_analysis
        }
        
        if not self.create_training_manifest(splits, metadata):
            logger.error("Failed to create training manifest")
            return False
        
        # Step 6: Log summary
        self._log_organization_summary(valid_pdfs, invalid_pdfs, splits, metadata, structure_analysis)
        
        logger.info("Dataset organization completed successfully!")
        return True
    
    def _log_organization_summary(self, valid_pdfs: List[Path], invalid_pdfs: List[Path],
                                splits: Dict[str, List[Path]], metadata: Dict[str, Any], 
                                structure_analysis: Dict[str, Any]):
        """Log summary of dataset organization including folder structure information."""
        logger.info("\n" + "="*60)
        logger.info("ACCESSIBILITY TRAINING DATA ORGANIZATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Source Directory: {self.source_dir}")
        logger.info(f"Output Directory: {self.output_dir}")
        logger.info(f"")
        
        logger.info(f"📁 Folder Structure:")
        logger.info(f"  - Total folders: {len(structure_analysis['folders'])}")
        logger.info(f"  - Maximum depth: {structure_analysis['max_depth']}")
        logger.info(f"  - Nested structure: {'Yes' if structure_analysis['has_nested_structure'] else 'No'}")
        
        if structure_analysis['has_nested_structure']:
            logger.info(f"  - Folder distribution:")
            for folder, info in sorted(structure_analysis['folders'].items()):
                folder_display = folder if folder != 'root' else '(root directory)'
                logger.info(f"    • {folder_display}: {info['pdf_count']} PDFs")
        
        logger.info(f"")
        logger.info(f"📄 PDF File Validation:")
        logger.info(f"  - Valid PDFs: {len(valid_pdfs)}")
        logger.info(f"  - Invalid PDFs: {len(invalid_pdfs)}")
        logger.info(f"")
        logger.info(f"📊 Training Split Distribution:")
        for split_name, file_list in splits.items():
            percentage = (len(file_list) / len(valid_pdfs)) * 100
            logger.info(f"  - {split_name.capitalize()}: {len(file_list)} files ({percentage:.1f}%)")
        logger.info(f"")
        logger.info(f"🔍 Metadata Analysis (sample of {metadata['sample_size']} files):")
        characteristics = metadata['document_characteristics']
        logger.info(f"  - Average page count: {characteristics.get('avg_page_count', 0):.1f}")
        logger.info(f"  - WCAG levels: {dict(characteristics.get('wcag_levels', {}))}")
        logger.info(f"  - PDF/UA versions: {dict(characteristics.get('pdf_ua_versions', {}))}")
        logger.info(f"  - Languages: {dict(characteristics.get('languages', {}))}")
        logger.info(f"  - Compliance patterns: {dict(characteristics.get('compliance_patterns', {}))}")
        logger.info(f"")
        logger.info(f"🚀 Next Steps:")
        logger.info(f"  1. Run accessibility data extraction on training set")
        logger.info(f"  2. Train ML models using extracted patterns")
        logger.info(f"  3. Integrate trained models into Phase 2B pipeline")
        logger.info(f"  4. Validate on test set for compliance accuracy")
        
        if structure_analysis['has_nested_structure']:
            logger.info(f"")
            logger.info(f"💡 Folder Organization Benefits:")
            logger.info(f"  - Source folder information preserved in training splits")
            logger.info(f"  - Easy to track which types of compliant PDFs perform best")
            logger.info(f"  - Helpful for analyzing model performance by document category")
        
        logger.info("="*60)


def main():
    """Command line interface for training data organization."""
    parser = argparse.ArgumentParser(
        description="Organize compliant PDF files for accessibility training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Organize 1600 compliant PDFs for training
  python organize_training_data.py --source /path/to/compliant/pdfs --output data/training/accessibility
  
  # Organize with custom split ratios
  python organize_training_data.py --source /path/to/pdfs --output data/training/accessibility \\
    --train-ratio 0.8 --val-ratio 0.1 --test-ratio 0.1
  
  # Extract metadata from larger sample
  python organize_training_data.py --source /path/to/pdfs --output data/training/accessibility \\
    --metadata-sample 100
        """
    )
    
    parser.add_argument("--source", "-s", type=Path, required=True,
                       help="Source directory containing 1600+ compliant PDF files")
    parser.add_argument("--output", "-o", type=Path, required=True,
                       help="Output directory for organized training data")
    parser.add_argument("--train-ratio", type=float, default=0.7,
                       help="Training set ratio (default: 0.7)")
    parser.add_argument("--val-ratio", type=float, default=0.15,
                       help="Validation set ratio (default: 0.15)")
    parser.add_argument("--test-ratio", type=float, default=0.15,
                       help="Test set ratio (default: 0.15)")
    parser.add_argument("--metadata-sample", type=int, default=50,
                       help="Number of files for metadata extraction (default: 50)")
    parser.add_argument("--random-seed", type=int, default=42,
                       help="Random seed for reproducible splits (default: 42)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Validate ratios
    total_ratio = args.train_ratio + args.val_ratio + args.test_ratio
    if abs(total_ratio - 1.0) > 1e-6:
        parser.error(f"Train/validation/test ratios must sum to 1.0 (got {total_ratio})")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Check source directory exists
    if not args.source.exists():
        parser.error(f"Source directory does not exist: {args.source}")
    
    # Initialize organizer
    organizer = TrainingDataOrganizer(args.source, args.output)
    
    # Run organization
    success = organizer.organize_complete_dataset(args.metadata_sample)
    
    if success:
        print(f"\n✅ Training data organization completed successfully!")
        print(f"📁 Training data organized in: {args.output}")
        print(f"📊 Training manifest: {args.output}/training_manifest.json")
        print(f"📈 Metadata analysis: {args.output}/metadata/training_metadata_analysis.json")
        print(f"\n🚀 Ready for accessibility model training!")
    else:
        print(f"\n❌ Training data organization failed. Check logs for details.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
