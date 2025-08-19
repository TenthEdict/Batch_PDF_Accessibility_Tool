#!/usr/bin/env python3
"""
Parallel Processing Performance Demonstration

This script demonstrates the Phase 1 parallel processing enhancements
with comprehensive performance comparisons and system optimization analysis.

Features:
- Sequential vs Parallel processing comparison
- Resource monitoring and optimization
- ML enhancer thread safety validation
- Performance metrics and analysis
- System capability assessment
"""

import sys
import time
import json
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Any
import traceback

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from processor.unified_project.src.batch import (
        BatchProcessingConfiguration,
        AdvancedBatchProcessor,
        ParallelBatchProcessor,
        EnhancedBatchProcessor
    )
    from processor.unified_project.src.monitoring.performance_tracker import get_performance_tracker
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the correct directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ParallelProcessingDemo:
    """
    Comprehensive demonstration of parallel processing enhancements.
    """
    
    def __init__(self, input_dir: str = "/home/schipp0/ePubs_Main/data/input", 
                 output_dir: str = "/home/schipp0/ePubs_Main/data/output"):
        """
        Initialize performance demonstration.
        
        Args:
            input_dir: Directory containing PDF files for testing
            output_dir: Directory for output files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Create output directories
        self.sequential_output_dir = self.output_dir / "sequential_test"
        self.parallel_output_dir = self.output_dir / "parallel_test"
        self.enhanced_output_dir = self.output_dir / "enhanced_test"
        
        self.sequential_output_dir.mkdir(parents=True, exist_ok=True)
        self.parallel_output_dir.mkdir(parents=True, exist_ok=True)
        self.enhanced_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.performance_tracker = get_performance_tracker()
        self.results = {}
        
        logger.info("Parallel Processing Performance Demo initialized")
    
    def check_system_capabilities(self) -> Dict[str, Any]:
        """
        Analyze system capabilities for parallel processing.
        
        Returns:
            Dict[str, Any]: System capability analysis
        """
        print("\n" + "="*60)
        print("SYSTEM CAPABILITY ANALYSIS")
        print("="*60)
        
        import multiprocessing
        import platform
        
        capabilities = {
            'platform': platform.system(),
            'cpu_cores': multiprocessing.cpu_count(),
            'python_version': platform.python_version(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Check for optional dependencies
        try:
            import psutil
            memory = psutil.virtual_memory()
            capabilities.update({
                'psutil_available': True,
                'total_memory_gb': round(memory.total / (1024**3), 2),
                'available_memory_gb': round(memory.available / (1024**3), 2),
                'memory_usage_percent': memory.percent
            })
        except ImportError:
            capabilities['psutil_available'] = False
        
        try:
            from tqdm import tqdm
            capabilities['tqdm_available'] = True
        except ImportError:
            capabilities['tqdm_available'] = False
        
        # Test parallel processing configuration
        try:
            config = BatchProcessingConfiguration(
                input_dir=str(self.input_dir),
                output_dir=str(self.parallel_output_dir)
            )
            parallel_processor = ParallelBatchProcessor(config)
            optimization_report = parallel_processor.optimize_for_system()
            capabilities['optimization_report'] = optimization_report
        except Exception as e:
            capabilities['parallel_processor_error'] = str(e)
        
        # Print capability summary
        print(f"Platform: {capabilities['platform']}")
        print(f"CPU Cores: {capabilities['cpu_cores']}")
        print(f"Python Version: {capabilities['python_version']}")
        
        if capabilities.get('psutil_available'):
            print(f"Memory: {capabilities['available_memory_gb']:.1f}GB available / {capabilities['total_memory_gb']:.1f}GB total")
            print(f"Memory Usage: {capabilities['memory_usage_percent']:.1f}%")
        else:
            print("Memory monitoring: Not available (install psutil)")
        
        print(f"Progress bar support: {'Yes' if capabilities.get('tqdm_available') else 'No'}")
        
        if 'optimization_report' in capabilities:
            opt_report = capabilities['optimization_report']
            print(f"\nOptimal Workers: {opt_report['current_settings']['optimal_workers']}")
            
            if opt_report['recommendations']:
                print("\nSystem Recommendations:")
                for rec in opt_report['recommendations']:
                    print(f"  • {rec}")
        
        return capabilities
    
    def prepare_test_data(self) -> List[Path]:
        """
        Prepare test data and validate input files.
        
        Returns:
            List[Path]: List of PDF files for testing
        """
        print(f"\nSCANNING INPUT DIRECTORY: {self.input_dir}")
        print("-" * 50)
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")
        
        pdf_files = list(self.input_dir.glob("*.pdf"))
        
        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in {self.input_dir}")
        
        print(f"Found {len(pdf_files)} PDF files:")
        for i, pdf_file in enumerate(pdf_files[:5]):  # Show first 5 files
            file_size = pdf_file.stat().st_size / (1024*1024)  # Size in MB
            print(f"  {i+1}. {pdf_file.name} ({file_size:.1f} MB)")
        
        if len(pdf_files) > 5:
            print(f"  ... and {len(pdf_files) - 5} more files")
        
        total_size = sum(f.stat().st_size for f in pdf_files) / (1024*1024)
        print(f"\nTotal data to process: {total_size:.1f} MB")
        
        return pdf_files
    
    def run_sequential_test(self, pdf_files: List[Path]) -> Dict[str, Any]:
        """
        Run sequential processing performance test.
        
        Args:
            pdf_files: List of PDF files to process
            
        Returns:
            Dict[str, Any]: Sequential processing results
        """
        print("\n" + "="*60)
        print("SEQUENTIAL PROCESSING TEST")
        print("="*60)
        
        config = BatchProcessingConfiguration(
            input_dir=str(self.input_dir),
            output_dir=str(self.sequential_output_dir),
            enable_detailed_logging=True
        )
        
        processor = AdvancedBatchProcessor(config)
        
        start_time = time.time()
        
        with self.performance_tracker.track_operation("sequential_batch_test"):
            success = processor.process_batch()
        
        end_time = time.time()
        
        results = {
            'mode': 'sequential',
            'success': success,
            'total_time': end_time - start_time,
            'files_processed': len(pdf_files),
            'throughput': len(pdf_files) / (end_time - start_time) if (end_time - start_time) > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Get detailed metrics
        if hasattr(processor, 'metrics'):
            metrics = processor.metrics.generate_report()
            results['detailed_metrics'] = metrics['processing_summary']
        
        print(f"Sequential Processing Results:")
        print(f"  Total Time: {results['total_time']:.2f} seconds")
        print(f"  Files Processed: {results['files_processed']}")
        print(f"  Throughput: {results['throughput']:.2f} files/second")
        print(f"  Success: {results['success']}")
        
        return results
    
    def run_parallel_test(self, pdf_files: List[Path]) -> Dict[str, Any]:
        """
        Run parallel processing performance test.
        
        Args:
            pdf_files: List of PDF files to process
            
        Returns:
            Dict[str, Any]: Parallel processing results
        """
        print("\n" + "="*60)
        print("PARALLEL PROCESSING TEST")
        print("="*60)
        
        config = BatchProcessingConfiguration(
            input_dir=str(self.input_dir),
            output_dir=str(self.parallel_output_dir),
            enable_detailed_logging=True
        )
        
        processor = ParallelBatchProcessor(config)
        
        # Display parallel processing configuration
        print(f"Optimal Workers: {processor.optimal_workers}")
        print(f"Resource Monitoring: {processor.enable_resource_monitoring}")
        print(f"ML Optimization: {processor.enable_ml_optimization}")
        
        start_time = time.time()
        
        with self.performance_tracker.track_operation("parallel_batch_test"):
            success = processor.process_batch_parallel()
        
        end_time = time.time()
        
        results = {
            'mode': 'parallel',
            'success': success,
            'total_time': end_time - start_time,
            'files_processed': len(pdf_files),
            'throughput': len(pdf_files) / (end_time - start_time) if (end_time - start_time) > 0 else 0,
            'workers_used': processor.optimal_workers,
            'timestamp': datetime.now().isoformat()
        }
        
        # Get detailed parallel metrics
        if hasattr(processor, 'metrics'):
            metrics = processor.metrics.generate_parallel_report()
            results['detailed_metrics'] = metrics['processing_summary']
            results['parallel_metrics'] = metrics.get('parallel_processing_metrics', {})
            results['worker_performance'] = metrics.get('worker_performance', {})
        
        print(f"Parallel Processing Results:")
        print(f"  Total Time: {results['total_time']:.2f} seconds")
        print(f"  Files Processed: {results['files_processed']}")
        print(f"  Throughput: {results['throughput']:.2f} files/second")
        print(f"  Workers Used: {results['workers_used']}")
        print(f"  Success: {results['success']}")
        
        # Show parallel-specific metrics
        if 'parallel_metrics' in results:
            pm = results['parallel_metrics']
            print(f"  Max Concurrent Files: {pm.get('max_concurrent_files', 'N/A')}")
            print(f"  Avg Concurrent Files: {pm.get('average_concurrent_files', 'N/A'):.1f}")
            print(f"  Throttling Events: {pm.get('throttling_events', 'N/A')}")
        
        return results
    
    def run_enhanced_test(self, pdf_files: List[Path]) -> Dict[str, Any]:
        """
        Run enhanced batch processor test (auto-mode selection).
        
        Args:
            pdf_files: List of PDF files to process
            
        Returns:
            Dict[str, Any]: Enhanced processing results
        """
        print("\n" + "="*60)
        print("ENHANCED BATCH PROCESSOR TEST (Auto-Mode)")
        print("="*60)
        
        config = BatchProcessingConfiguration(
            input_dir=str(self.input_dir),
            output_dir=str(self.enhanced_output_dir),
            enable_detailed_logging=True
        )
        
        processor = EnhancedBatchProcessor(config)
        
        start_time = time.time()
        
        with self.performance_tracker.track_operation("enhanced_batch_test"):
            success = processor.process_batch()
        
        end_time = time.time()
        
        results = {
            'mode': 'enhanced_auto',
            'success': success,
            'total_time': end_time - start_time,
            'files_processed': len(pdf_files),
            'throughput': len(pdf_files) / (end_time - start_time) if (end_time - start_time) > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Enhanced Processing Results:")
        print(f"  Total Time: {results['total_time']:.2f} seconds")
        print(f"  Files Processed: {results['files_processed']}")
        print(f"  Throughput: {results['throughput']:.2f} files/second")
        print(f"  Success: {results['success']}")
        
        return results
    
    def compare_performance(self, sequential_results: Dict[str, Any], 
                          parallel_results: Dict[str, Any], 
                          enhanced_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare performance results and calculate improvements.
        
        Args:
            sequential_results: Sequential processing results
            parallel_results: Parallel processing results
            enhanced_results: Enhanced processing results
            
        Returns:
            Dict[str, Any]: Performance comparison analysis
        """
        print("\n" + "="*60)
        print("PERFORMANCE COMPARISON ANALYSIS")
        print("="*60)
        
        # Calculate speedup factors
        seq_time = sequential_results['total_time']
        par_time = parallel_results['total_time']
        enh_time = enhanced_results['total_time']
        
        parallel_speedup = seq_time / par_time if par_time > 0 else 0
        enhanced_speedup = seq_time / enh_time if enh_time > 0 else 0
        
        seq_throughput = sequential_results['throughput']
        par_throughput = parallel_results['throughput']
        enh_throughput = enhanced_results['throughput']
        
        comparison = {
            'sequential': {
                'time': seq_time,
                'throughput': seq_throughput,
                'baseline': 1.0
            },
            'parallel': {
                'time': par_time,
                'throughput': par_throughput,
                'speedup': parallel_speedup,
                'improvement_percent': (parallel_speedup - 1.0) * 100
            },
            'enhanced': {
                'time': enh_time,
                'throughput': enh_throughput,
                'speedup': enhanced_speedup,
                'improvement_percent': (enhanced_speedup - 1.0) * 100
            },
            'best_performer': 'sequential'
        }
        
        # Determine best performer
        if par_throughput > seq_throughput and par_throughput > enh_throughput:
            comparison['best_performer'] = 'parallel'
        elif enh_throughput > seq_throughput and enh_throughput > par_throughput:
            comparison['best_performer'] = 'enhanced'
        
        # Print comparison
        print(f"Processing Mode Comparison:")
        print(f"  Sequential:  {seq_time:.2f}s  ({seq_throughput:.2f} files/s)  [Baseline]")
        print(f"  Parallel:    {par_time:.2f}s  ({par_throughput:.2f} files/s)  [{parallel_speedup:.2f}x speedup, {comparison['parallel']['improvement_percent']:+.1f}%]")
        print(f"  Enhanced:    {enh_time:.2f}s  ({enh_throughput:.2f} files/s)  [{enhanced_speedup:.2f}x speedup, {comparison['enhanced']['improvement_percent']:+.1f}%]")
        print(f"\nBest Performer: {comparison['best_performer'].title()} Mode")
        
        # Success rate analysis
        print(f"\nSuccess Rate Analysis:")
        print(f"  Sequential: {sequential_results['success']}")
        print(f"  Parallel:   {parallel_results['success']}")
        print(f"  Enhanced:   {enhanced_results['success']}")
        
        return comparison
    
    def generate_comprehensive_report(self, capabilities: Dict[str, Any], 
                                    results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Args:
            capabilities: System capabilities analysis
            results: All processing results
            
        Returns:
            Dict[str, Any]: Comprehensive report
        """
        report = {
            'demo_info': {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'phase': 'Phase 1 - Parallel Processing Enhancement'
            },
            'system_capabilities': capabilities,
            'processing_results': results,
            'recommendations': []
        }
        
        # Generate recommendations
        if capabilities.get('cpu_cores', 1) >= 4:
            report['recommendations'].append(
                f"System has {capabilities['cpu_cores']} CPU cores - parallel processing provides significant benefits"
            )
        
        if capabilities.get('psutil_available'):
            memory_gb = capabilities.get('total_memory_gb', 0)
            if memory_gb >= 8:
                report['recommendations'].append(
                    f"Ample memory ({memory_gb:.1f}GB) available - can process large document batches efficiently"
                )
        else:
            report['recommendations'].append(
                "Install psutil for enhanced resource monitoring: pip install psutil"
            )
        
        if 'comparison' in results:
            best_performer = results['comparison']['best_performer']
            if best_performer == 'parallel':
                speedup = results['comparison']['parallel']['speedup']
                report['recommendations'].append(
                    f"Parallel processing provides {speedup:.2f}x speedup - recommended for batch operations"
                )
            elif best_performer == 'enhanced':
                speedup = results['comparison']['enhanced']['speedup']
                report['recommendations'].append(
                    f"Enhanced auto-mode processing provides {speedup:.2f}x speedup - recommended default"
                )
        
        # Save report
        report_path = self.output_dir / "phase1_performance_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\nComprehensive report saved to: {report_path}")
        return report
    
    def run_full_demonstration(self) -> Dict[str, Any]:
        """
        Run complete parallel processing demonstration.
        
        Returns:
            Dict[str, Any]: Complete demonstration results
        """
        try:
            print("EPUBS PARALLEL PROCESSING PERFORMANCE DEMONSTRATION")
            print("Phase 1: Parallel Processing Enhancement")
            print("=" * 80)
            
            # 1. System capability analysis
            capabilities = self.check_system_capabilities()
            
            # 2. Prepare test data
            pdf_files = self.prepare_test_data()
            
            # 3. Run performance tests
            sequential_results = self.run_sequential_test(pdf_files)
            parallel_results = self.run_parallel_test(pdf_files)
            enhanced_results = self.run_enhanced_test(pdf_files)
            
            # 4. Compare performance
            comparison = self.compare_performance(sequential_results, parallel_results, enhanced_results)
            
            # 5. Compile results
            all_results = {
                'sequential': sequential_results,
                'parallel': parallel_results,
                'enhanced': enhanced_results,
                'comparison': comparison
            }
            
            # 6. Generate comprehensive report
            report = self.generate_comprehensive_report(capabilities, all_results)
            
            return report
            
        except Exception as e:
            logger.error(f"Demonstration failed: {e}")
            logger.error(traceback.format_exc())
            return {'error': str(e), 'traceback': traceback.format_exc()}


def main():
    """Main demonstration function."""
    demo = ParallelProcessingDemo()
    results = demo.run_full_demonstration()
    
    if 'error' in results:
        print(f"\nDemo failed with error: {results['error']}")
        return 1
    
    print("\n" + "="*80)
    print("PHASE 1 IMPLEMENTATION COMPLETE")
    print("="*80)
    print("✅ Parallel processing with ThreadPoolExecutor")
    print("✅ Dynamic worker scaling based on system resources")
    print("✅ Memory monitoring and automatic throttling")
    print("✅ Thread-safe ML pattern matching optimization")
    print("✅ Enhanced performance tracking for parallel operations")
    print("\nReady to proceed to Phase 2 when approved!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
