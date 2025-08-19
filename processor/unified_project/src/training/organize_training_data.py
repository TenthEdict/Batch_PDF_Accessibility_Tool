        logger.info(f"  - Invalid PDFs: {len(invalid_pdfs)}")
        logger.info(f"")
        logger.info(f"Training Split Distribution:")
        for split_name, file_list in splits.items():
            percentage = (len(file_list) / len(valid_pdfs)) * 100
            logger.info(f"  - {split_name.capitalize()}: {len(file_list)} files ({percentage:.1f}%)")
        logger.info(f"")
        logger.info(f"Metadata Analysis (sample of {metadata['sample_size']} files):")
        characteristics = metadata['document_characteristics']
        logger.info(f"  - Average page count: {characteristics['avg_page_count']:.1f}")
        logger.info(f"  - WCAG levels: {dict(characteristics['wcag_levels'])}")
        logger.info(f"  - PDF/UA versions: {dict(characteristics['pdf_ua_versions'])}")
        logger.info(f"  - Languages: {dict(characteristics['languages'])}")
        logger.info(f"  - Compliance patterns: {dict(characteristics['compliance_patterns'])}")
        logger.info(f"")
        logger.info(f"Next Steps:")
        logger.info(f"  1. Run accessibility data extraction on training set")
        logger.info(f"  2. Train ML models using extracted patterns")
        logger.info(f"  3. Integrate trained models into Phase 2B pipeline")
        logger.info(f"  4. Validate on test set for compliance accuracy")
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
    
    # Override default ratios if provided
    organizer.train_ratio = args.train_ratio
    organizer.val_ratio = args.val_ratio
    organizer.test_ratio = args.test_ratio
    
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
