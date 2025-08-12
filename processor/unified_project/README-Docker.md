# Docker Setup

Docker configuration for ePubs Accessibility Enhancement Processor.

## Setup

### Using Docker Compose
```bash
# Build and run production container
docker-compose up epubs-processor

# Build and run development container
docker-compose up epubs-processor-dev
```

### Using Docker Directly
```bash
# Build image
docker build -f processor/unified_project/Dockerfile --target production -t epubs-processor .

# Run container
docker run -v $(pwd)/input:/data/input:ro \
           -v $(pwd)/output:/data/output \
           -v $(pwd)/logs:/data/logs \
           epubs-processor process input.pdf output.pdf --mode academic
```

## Processing

### Single PDF File
```bash
# Using docker-compose
docker-compose run epubs-processor process /data/input/document.pdf /data/output/enhanced.pdf --mode academic --verbose

# Using docker directly
docker run -v $(pwd)/input:/data/input:ro \
           -v $(pwd)/output:/data/output \
           epubs-processor process /data/input/document.pdf /data/output/enhanced.pdf --mode academic
```

### Batch Processing
```bash
# Using docker-compose
docker-compose run epubs-processor batch-process /data/input /data/output --verbose

# Using docker directly
docker run -v $(pwd)/input:/data/input:ro \
           -v $(pwd)/output:/data/output \
           epubs-processor batch-process /data/input /data/output
```

## Pipeline Usage

### Cache Management
```bash
# Show cache statistics
docker-compose run epubs-processor cache stats

# Clear cache
docker-compose run epubs-processor cache clear
```

### Development Container
```bash
# Build development image
docker build -f processor/unified_project/Dockerfile --target development -t epubs-processor-dev .

# Run with source code mounted
docker run -v $(pwd):/app -v $(pwd)/input:/data/input:ro -v $(pwd)/output:/data/output epubs-processor-dev
```

### Environment Variables
```bash
PYTHONPATH=/app
TESSDATA_PREFIX=/usr/share/tessdata
PYTHONUNBUFFERED=1
```

### Volume Mounts
- `/data/input`: Input directory (read-only)
- `/data/output`: Output directory (writable)
- `/data/logs`: Log files directory (writable)
- `/app/processor/unified_project/config`: Configuration files (read-only)

### Processing Modes
- `academic`: Optimized for academic papers and research documents
- `basic`: Standard processing for general documents
- `minimal`: Minimal processing for quick results

### CLI Commands
- `process`: Process a single PDF file
- `batch-process`: Process multiple PDF files in a directory
- `cache`: Cache management (stats, clear, prune)
- `stats`: Performance statistics and reporting
