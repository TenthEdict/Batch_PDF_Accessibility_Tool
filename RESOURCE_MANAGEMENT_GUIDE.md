# ePubs Batch Processing - Resource Management Guide

## PROBLEM RESOLVED: Resource Throttling

**Issue:** The parallel batch processor was ignoring the `--workers` parameter and auto-detecting too many workers, causing CPU saturation and resource throttling.

**Root Cause:** Bug in worker parameter passing - the command line `--workers` value wasn't being passed to the processor constructors.

**Fix Applied:** Updated main.py and phase2b_enhanced_processor.py to properly pass the max_workers parameter through the chain.

## RECOMMENDED USAGE

### 1. ALWAYS Specify Worker Count
```bash
# For systems with limited resources (recommended for most users)
python -m processor.unified_project.src.main batch-process data/input data/output --workers 2

# For high-performance systems (8+ cores, 16+ GB RAM)
python -m processor.unified_project.src.main batch-process data/input data/output --workers 4

# For resource-constrained systems
python -m processor.unified_project.src.main batch-process data/input data/output --workers 1
```

### 2. MONITOR System Resources
```bash
# Monitor CPU and memory usage during processing
htop          # Interactive process monitor
top           # Basic process monitor  
free -h       # Memory usage
```

### 3. AVOID Concurrent Operations
- **DON'T** run multiple batch processing operations simultaneously
- **DON'T** run batch-process and validate-phase2b at the same time
- **DO** wait for one operation to complete before starting another

### 4. CHOOSE Appropriate Processing Mode

#### Phase2B (Recommended - Fastest)
```bash
python -m processor.unified_project.src.main batch-process data/input data/output --mode phase2b --workers 2
```
- **Best for:** Most scenarios (5-8x speedup with caching and ML)
- **Resource usage:** Moderate (uses FAISS vector DB and caching)
- **Recommended workers:** 2-4 depending on system

#### Parallel (Fallback)
```bash
python -m processor.unified_project.src.main batch-process data/input data/output --mode parallel --workers 2
```
- **Best for:** Systems without Phase2B dependencies
- **Resource usage:** Moderate (pure parallel processing)
- **Recommended workers:** 2-3 depending on system

#### Sequential (Safe Mode)
```bash
python -m processor.unified_project.src.main batch-process data/input data/output --mode sequential
```
- **Best for:** Very limited resources or debugging
- **Resource usage:** Low (single-threaded)
- **Recommended workers:** N/A (single-threaded)

## SYSTEM SPECIFICATIONS GUIDE

### For 4-8 GB RAM Systems:
```bash
--workers 2    # Conservative, prevents memory pressure
```

### For 8-16 GB RAM Systems:
```bash
--workers 3    # Balanced performance/resources
```

### For 16+ GB RAM Systems:
```bash
--workers 4    # Aggressive performance
```

### For Development/Testing:
```bash
--workers 1    # Single worker for debugging
```

## TROUBLESHOOTING

### High CPU Usage (>80%)
1. Check for multiple Python processes: `ps aux | grep python`
2. Reduce worker count: `--workers 1` or `--workers 2`
3. Kill stuck processes: `pkill python` (careful!) or specific PIDs

### High Memory Usage (>80%)
1. Check memory: `free -h`
2. Reduce worker count: `--workers 1`
3. Use sequential mode: `--mode sequential`

### Stuck/Orphaned Processes
1. Find Tesseract processes: `ps aux | grep tesseract`
2. Kill them: `pkill tesseract`
3. Find Python processes: `ps aux | grep python`
4. Kill specific PIDs: `kill <PID>`

### Resource Throttling Warnings
```
WARNING - Resource throttling triggered - Memory: X%, CPU: Y%
```
**Solution:** Reduce worker count and restart with fewer workers.

## MONITORING COMMANDS

```bash
# Check active batch processing
ps aux | grep "batch-process"

# Check system resources
htop
free -h
df -h    # Disk space

# Check for stuck OCR processes
ps aux | grep tesseract

# Kill all tesseract processes (if stuck)
pkill tesseract

# Monitor logs in real-time
tail -f logs/parallel_batch_processing.log
```

## BEST PRACTICES

1. **Start Conservative:** Begin with `--workers 2` and increase if stable
2. **Monitor First Run:** Watch resource usage during initial processing
3. **One Operation at a Time:** Never run concurrent batch operations
4. **Regular Cleanup:** Check for orphaned processes after interruptions
5. **Use Phase2B Mode:** Provides best performance with smart resource management

## EMERGENCY CLEANUP

If system becomes unresponsive:
```bash
# Kill all Python batch processing
pkill -f "batch-process"

# Kill all Tesseract OCR processes
pkill tesseract

# Check remaining high-CPU processes
top
```

**Remember:** The resource throttling issue is now fixed, but following these guidelines ensures optimal performance and prevents resource exhaustion.
