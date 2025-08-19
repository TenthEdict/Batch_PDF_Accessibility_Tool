# Phase 2B Installation and Setup Guide

## Overview
Phase 2B adds advanced caching and ML optimization features to the ePubs Accessibility Enhancement system:
- **FAISS Vector Database**: 10x faster document similarity search
- **Hierarchical Caching**: Multi-level caching with predictive prefetch
- **Enhanced ML Optimization**: Academic document pattern recognition

## Installation

### 1. Install Phase 2B Dependencies
```bash
# Install with ML dependencies (includes FAISS)
pip install epubs-accessibility[ml]

# Or install specific dependencies
pip install faiss-cpu>=1.7.4 scikit-learn>=1.3.0 joblib>=1.3.0
```

### 2. Verify Installation
```bash
# Check if Phase 2B components are available
epubs validate-phase2b --help

# Run system capability analysis
python -c "
try:
    import faiss
    import sklearn
    print('✅ Phase 2B dependencies installed successfully')
    print(f'   FAISS version: Available')
    print(f'   GPU support: {faiss.get_num_gpus()} GPUs detected' if hasattr(faiss, 'get_num_gpus') else '   GPU support: Not available')
except ImportError as e:
    print(f'❌ Phase 2B dependencies missing: {e}')
"
```

## Usage

### Basic Phase 2B Processing
```bash
# Enable Phase 2B for batch processing
epubs batch-process input_dir/ output_dir/ --phase2b

# Or use explicit mode
epubs batch-process input_dir/ output_dir/ --mode phase2b
```

### Performance Validation
```bash
# Run comprehensive performance comparison
epubs validate-phase2b

# With custom directories
epubs validate-phase2b input_dir/ output_dir/

# With verbose output
epubs validate-phase2b --verbose
```

### Processing Mode Comparison
```bash
# Sequential processing (baseline)
epubs batch-process input_dir/ output_dir/ --mode sequential

# Phase 1 parallel processing (3-5x speedup)
epubs batch-process input_dir/ output_dir/ --mode parallel

# Phase 2B enhanced processing (5-8x speedup)
epubs batch-process input_dir/ output_dir/ --mode phase2b
```

## Performance Expectations

### Expected Speedups
- **Phase 1 Parallel**: 3-5x faster than sequential processing
- **Phase 2B Total**: 5-8x faster than sequential processing
- **FAISS Similarity Search**: 10x faster than traditional algorithms
- **Cache Hit Rate**: 70-80% for similar academic document batches

### Optimal Use Cases
- **Academic Document Collections**: Most effective with scholarly papers
- **Similar Document Batches**: Higher cache hit rates with related documents
- **Large Collections**: Greater benefits with 10+ documents
- **Repeat Processing**: Improved performance on subsequent runs

## System Requirements

### Minimum Requirements
- **CPU**: Multi-core processor (4+ cores recommended)
- **Memory**: 8GB RAM (16GB+ recommended for large batches)
- **Disk Space**: 2GB for cache storage
- **Python**: 3.9+ with pip

### Optimal Performance
- **CPU**: 8+ cores with high clock speeds
- **Memory**: 32GB+ RAM for large document collections
- **Storage**: SSD for cache directory (`~/.epubs/phase2b_cache/`)
- **GPU**: NVIDIA GPU with CUDA support (optional, for FAISS acceleration)

## Configuration

### Cache Settings
The system automatically creates cache directories:
```
~/.epubs/phase2b_cache/
├── memory/     # L1 cache (512MB default)
├── ssd/        # L2 cache (2GB default)  
├── disk/       # L3 cache (8GB default)
└── ml_knowledge/  # ML patterns and models
```

### Environment Variables
```bash
# Optional: Set custom cache directory
export EPUBS_CACHE_DIR="/path/to/cache"

# Optional: Disable GPU acceleration
export FAISS_NO_GPU=1
```

## Troubleshooting

### Common Issues

#### FAISS Installation Issues
```bash
# Linux: Install with conda if pip fails
conda install -c conda-forge faiss-cpu

# macOS: Ensure compatible Python version
python --version  # Should be 3.9+
pip install --upgrade pip
pip install faiss-cpu
```

#### Memory Issues
```bash
# Reduce cache sizes for systems with limited RAM
# System automatically adjusts based on available memory
# Monitor with: epubs validate-phase2b --verbose
```

#### Performance Issues
```bash
# Check system capabilities
epubs validate-phase2b --verbose

# Verify adequate disk space for cache
df -h ~/.epubs/

# Monitor resource usage during processing
htop  # or Activity Monitor on macOS
```

### Fallback Behavior
Phase 2B is designed with graceful fallback:
- **No ML dependencies**: Falls back to Phase 1 parallel processing
- **Insufficient memory**: Automatically reduces cache sizes
- **No GPU**: Uses CPU-only FAISS processing
- **Cache errors**: Continues without caching

## Performance Monitoring

### Built-in Analytics
```bash
# View Phase 2B performance report after processing
# Reports include:
# - FAISS vector database statistics
# - Hierarchical cache hit rates
# - ML pattern recognition confidence
# - Overall performance improvements
```

### Cache Statistics
```bash
# Check cache performance
ls -la ~/.epubs/phase2b_cache/
du -sh ~/.epubs/phase2b_cache/*

# Clear cache if needed
rm -rf ~/.epubs/phase2b_cache/
```

## Best Practices

### For Optimal Performance
1. **Process similar documents together** - improves cache hit rates
2. **Use SSD storage** - faster cache access
3. **Allow adequate memory** - prevents throttling
4. **Run validation first** - establishes baseline performance

### For Academic Workflows
1. **Batch journal articles** - similar structure improves ML learning
2. **Separate document types** - different processing optimizations
3. **Monitor cache hit rates** - indicates system effectiveness
4. **Regular validation** - track performance improvements over time

## Support

### Getting Help
- **Verbose mode**: Add `--verbose` to any command for detailed logging
- **Validation report**: Run `epubs validate-phase2b` for system analysis
- **Check dependencies**: Verify ML packages are correctly installed
- **Cache diagnostics**: Monitor `~/.epubs/phase2b_cache/` directory

### Reporting Issues
When reporting Phase 2B issues, include:
- Output from `epubs validate-phase2b --verbose`
- System specifications (CPU, RAM, OS)
- Error messages and logs
- Document types being processed
