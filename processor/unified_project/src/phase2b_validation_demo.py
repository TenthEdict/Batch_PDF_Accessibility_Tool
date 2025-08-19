#!/usr/bin/env python3
"""
Phase 2B Performance Validation Demo

This script demonstrates and validates the Phase 2B enhancements:
- FAISS Vector Database for 10x faster similarity search
- Hierarchical Caching with predictive prefetch (Memory -> SSD -> Disk)
- Advanced ML optimization with academic document patterns
- Combined Phase 1+2B target: 5-8x total speedup

Usage:
    python phase2b_demo.py [input_directory] [output_directory]

Features Demonstrated:
- Sequential vs Parallel vs Phase 2B performance comparison
- FAISS similarity search performance analysis
- Hierarchical cache hit rate and efficiency metrics
- ML pattern recognition and optimization benefits
- Resource utilization and system optimization
"""

import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import platform

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import Phase 2B components
try:
    from processor.unified_project.src.batch.phase2b_enhanced_processor import (
        Phase2BEnhancedBatchProcessor, create_phase2b_batch_processor
    )
    from processor.unified_project.src.batch.parallel_batch_processor import ParallelBatchProcessor
    from processor.unified_project.src.batch.advanced_batch_processor import (
        AdvancedBatchProcessor, BatchProcessingConfiguration
    )
    
    # Phase 2B specific imports
    from processor.unified_project.src.ml.faiss_vector_db import get_vector_database
    from processor.unified_project.src.caching.hierarchical_cache import HierarchicalCacheManager
    from processor.unified_project.src.enhancers.thread_safe_ml_enhancer import ThreadSafeAdaptiveMLEnhancer
    
    PHASE2B_AVAILABLE = True
except ImportError as e:
    print(f"Phase 2B components not available: {e}")
    PHASE2B_AVAILABLE = False

# Standard imports
import multiprocessing

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase2BPerformanceValidator:
    """
    Comprehensive Phase 2B performance validation and demonstration.
    
    Tests and compares:
    - Sequential processing (baseline)
    - Phase 1 parallel processing 
    - Phase 2B enhanced processing (FAISS + Hierarchical Cache + ML)
    """
    
    def __init__(self, input_dir: Path, output_dir: Path):
        """Initialize Phase 2B performance validator."""
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.results = {}
        
        # Create output directories
        self.sequential_output = output_dir / "sequential"
        self.parallel_output = output_dir / "parallel" 
        self.phase2b_output = output_dir / "phase2b"
        
        for output_path in [self.sequential_output, self.parallel_output, self.phase2b_output]:
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Find PDF files
        self.pdf_files = list(self.input_dir.glob("*.pdf"))
        if not self.pdf_files:
            raise ValueError(f"No PDF files found in {input_dir}")
        
        logger.info(f"Found {len(self.pdf_files)} PDF files for testing")
        logger.info(f"Phase 2B components available: {PHASE2B_AVAILABLE}")
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive Phase 2B validation."""
        print("\n" + "="*80)
        print("🚀 PHASE 2B PERFORMANCE VALIDATION")
        print("="*80)
        
        # System capability analysis
        self.analyze_system_capabilities()
        
        # Sequential processing baseline
        print("\n📊 Running Sequential Processing (Baseline)...")
        sequential_result = self.run_sequential_processing()
        
        # Phase 1 parallel processing
        print("\n⚡ Running Phase 1 Parallel Processing...")
        parallel_result = self.run_parallel_processing()
        
        # Phase 2B enhanced processing
        if PHASE2B_AVAILABLE:
            print("\n🎯 Running Phase 2B Enhanced Processing...")
            phase2b_result = self.run_phase2b_processing()
        else:
            print("\n❌ Phase 2B components not available - skipping enhanced processing")
            phase2b_result = None
        
        # Performance comparison and analysis
        print("\n📈 Analyzing Performance Results...")
        comparison_results = self.analyze_performance_comparison(
            sequential_result, parallel_result, phase2b_result
        )
        
        # Phase 2B specific analysis
        if PHASE2B_AVAILABLE and phase2b_result:
            print("\n🔍 Analyzing Phase 2B Enhancements...")
            phase2b_analysis = self.analyze_phase2b_enhancements(phase2b_result)
            comparison_results['phase2b_analysis'] = phase2b_analysis
        
        # Generate comprehensive report
        self.generate_comprehensive_report(comparison_results)
        
        return comparison_results
    
    def analyze_system_capabilities(self):
        """Analyze system capabilities for Phase 2B features."""
        print("\n🔧 System Capability Analysis:")
        
        # Basic system info
        print(f"   • Platform: {platform.system()} {platform.release()}")
        print(f"   • CPU Cores: {multiprocessing.cpu_count()}")
        
        # Memory analysis
        try:
            import psutil
            memory = psutil.virtual_memory()
            print(f"   • Total Memory: {memory.total / (1024**3):.1f} GB")
            print(f"   • Available Memory: {memory.available / (1024**3):.1f} GB")
        except ImportError:
            print("   • Memory info: Not available (psutil not installed)")
        
        # Phase 2B component availability
        if PHASE2B_AVAILABLE:
            print("\n✅ Phase 2B Component Status:")
            
            # FAISS availability
            try:
                import faiss
                print(f"   • FAISS: Available (version info)")
                if hasattr(faiss, 'get_num_gpus'):
                    gpu_count = faiss.get_num_gpus()
                    print(f"   • FAISS GPU Support: {gpu_count} GPUs detected")
                else:
                    print("   • FAISS GPU Support: Not available")
            except ImportError:
                print("   • FAISS: Not available")
            
            # ML dependencies
            try:
                import sklearn
                import numpy as np
                print(f"   • ML Dependencies: Available")
            except ImportError:
                print("   • ML Dependencies: Not available")
            
            # Cache directory
            cache_dir = Path.home() / ".epubs" / "phase2b_cache"
            print(f"   • Cache Directory: {cache_dir}")
            
        else:
            print("\n❌ Phase 2B Components: Not Available")
            print("   Install with: pip install epubs-accessibility[ml]")
    
    def run_sequential_processing(self) -> Dict[str, Any]:
        """Run sequential processing for baseline."""
        if not PHASE2B_AVAILABLE:
            return {'error': 'Components not available'}
        
        try:
            config = BatchProcessingConfiguration()
            processor = AdvancedBatchProcessor(config)
            
            start_time = time.time()
            metrics = processor.process_files(self.pdf_files, self.sequential_output)
            processing_time = time.time() - start_time
            
            result = {
                'mode': 'sequential',
                'total_time': processing_time,
                'files_processed': metrics.successful_files,
                'files_failed': metrics.failed_files,
                'avg_time_per_file': metrics.average_processing_time,
                'throughput': metrics.throughput_files_per_second,
                'memory_usage': metrics.memory_usage_mb
            }
            
            print(f"   ✅ Sequential: {result['files_processed']} files in {result['total_time']:.2f}s")
            print(f"      Throughput: {result['throughput']:.2f} files/sec")
            
            return result
            
        except Exception as e:
            logger.error(f"Sequential processing failed: {e}")
            return {'error': str(e)}
    
    def run_parallel_processing(self) -> Dict[str, Any]:
        """Run Phase 1 parallel processing."""
        if not PHASE2B_AVAILABLE:
            return {'error': 'Components not available'}
        
        try:
            config = BatchProcessingConfiguration()
            processor = ParallelBatchProcessor(config)
            
            start_time = time.time()
            metrics = processor.process_files_parallel(self.pdf_files, self.parallel_output)
            processing_time = time.time() - start_time
            
            result = {
                'mode': 'parallel',
                'total_time': processing_time,
                'files_processed': metrics.successful_files,
                'files_failed': metrics.failed_files,
                'avg_time_per_file': metrics.average_processing_time,
                'throughput': metrics.throughput_files_per_second,
                'memory_usage': metrics.memory_usage_mb,
                'parallel_workers': getattr(metrics, 'parallel_workers', 'unknown')
            }
            
            print(f"   ⚡ Parallel: {result['files_processed']} files in {result['total_time']:.2f}s")
            print(f"      Throughput: {result['throughput']:.2f} files/sec")
            print(f"      Workers: {result['parallel_workers']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Parallel processing failed: {e}")
            return {'error': str(e)}
    
    def run_phase2b_processing(self) -> Dict[str, Any]:
        """Run Phase 2B enhanced processing."""
        if not PHASE2B_AVAILABLE:
            return {'error': 'Phase 2B components not available'}
        
        try:
            config = BatchProcessingConfiguration()
            processor = create_phase2b_batch_processor(config)
            
            start_time = time.time()
            metrics = processor.process_files_parallel(self.pdf_files, self.phase2b_output)
            processing_time = time.time() - start_time
            
            # Get Phase 2B specific metrics
            phase2b_report = processor.get_phase2b_performance_report()
            
            result = {
                'mode': 'phase2b',
                'total_time': processing_time,
                'files_processed': metrics.successful_files,
                'files_failed': metrics.failed_files,
                'avg_time_per_file': metrics.average_processing_time,
                'throughput': metrics.throughput_files_per_second,
                'memory_usage': metrics.memory_usage_mb,
                'phase2b_metrics': getattr(metrics, 'phase2b_enhancements', {}),
                'phase2b_report': phase2b_report
            }
            
            print(f"   🎯 Phase 2B: {result['files_processed']} files in {result['total_time']:.2f}s")
            print(f"      Throughput: {result['throughput']:.2f} files/sec")
            
            # Show Phase 2B specific metrics
            phase2b_metrics = result['phase2b_metrics']
            if phase2b_metrics:
                cache_hit_rate = phase2b_metrics.get('cache_hit_rate', 0) * 100
                vector_search_time = phase2b_metrics.get('vector_search_time_ms', 0)
                similarity_matches = phase2b_metrics.get('similarity_matches_found', 0)
                
                print(f"      Cache Hit Rate: {cache_hit_rate:.1f}%")
                print(f"      Vector Search: {vector_search_time:.1f}ms total")
                print(f"      Similarity Matches: {similarity_matches}")
            
            return result
            
        except Exception as e:
            logger.error(f"Phase 2B processing failed: {e}")
            return {'error': str(e)}
    
    def analyze_performance_comparison(self, sequential: Dict[str, Any], 
                                     parallel: Dict[str, Any], 
                                     phase2b: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance comparison between all modes."""
        
        comparison = {
            'baseline_time': sequential.get('total_time', 0),
            'parallel_time': parallel.get('total_time', 0),
            'phase2b_time': phase2b.get('total_time', 0) if phase2b else 0,
            'speedup_improvements': {}
        }
        
        baseline_time = comparison['baseline_time']
        
        if baseline_time > 0:
            # Calculate speedups
            if parallel.get('total_time', 0) > 0:
                parallel_speedup = baseline_time / parallel['total_time']
                comparison['speedup_improvements']['phase1_parallel'] = f"{parallel_speedup:.1f}x"
            
            if phase2b and phase2b.get('total_time', 0) > 0:
                phase2b_speedup = baseline_time / phase2b['total_time']
                comparison['speedup_improvements']['phase2b_total'] = f"{phase2b_speedup:.1f}x"
                
                # Additional Phase 2B vs Phase 1 improvement
                if parallel.get('total_time', 0) > 0:
                    phase2b_vs_parallel = parallel['total_time'] / phase2b['total_time']
                    comparison['speedup_improvements']['phase2b_vs_phase1'] = f"{phase2b_vs_parallel:.1f}x"
        
        # Throughput comparison
        comparison['throughput_comparison'] = {
            'sequential': sequential.get('throughput', 0),
            'parallel': parallel.get('throughput', 0),
            'phase2b': phase2b.get('throughput', 0) if phase2b else 0
        }
        
        return comparison
    
    def analyze_phase2b_enhancements(self, phase2b_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Phase 2B specific enhancements."""
        phase2b_report = phase2b_result.get('phase2b_report', {})
        phase2b_metrics = phase2b_result.get('phase2b_metrics', {})
        
        analysis = {
            'faiss_performance': {},
            'cache_performance': {},
            'ml_optimization': {},
            'overall_efficiency': {}
        }
        
        # FAISS Analysis
        faiss_stats = phase2b_report.get('faiss_statistics', {})
        if faiss_stats:
            analysis['faiss_performance'] = {
                'vector_database_size': faiss_stats.get('index_info', {}).get('size', 0),
                'average_search_time_ms': faiss_stats.get('search_performance', {}).get('avg_search_time_ms', 0),
                'searches_per_second': faiss_stats.get('search_performance', {}).get('searches_per_second', 0),
                'gpu_acceleration': faiss_stats.get('index_info', {}).get('gpu_enabled', False)
            }
        
        # Cache Analysis
        cache_stats = phase2b_report.get('cache_statistics', {})
        if cache_stats:
            overall_cache = cache_stats.get('overall', {})
            analysis['cache_performance'] = {
                'total_cache_requests': overall_cache.get('total_requests', 0),
                'cache_hit_rate': overall_cache.get('overall_hit_rate', 0) * 100,
                'memory_cache_hit_rate': cache_stats.get('memory', {}).get('hit_rate', 0) * 100,
                'ssd_cache_hit_rate': cache_stats.get('ssd', {}).get('hit_rate', 0) * 100,
                'disk_cache_hit_rate': cache_stats.get('disk', {}).get('hit_rate', 0) * 100
            }
        
        # ML Optimization Analysis
        ml_stats = phase2b_report.get('ml_statistics', {})
        if ml_stats:
            analysis['ml_optimization'] = {
                'document_profiles': ml_stats.get('total_document_profiles', 0),
                'average_confidence': ml_stats.get('average_confidence', 0) * 100,
                'pattern_recognition_success': ml_stats.get('average_success_rate', 0) * 100
            }
        
        # Overall efficiency calculation
        estimated_speedup = phase2b_report.get('estimated_phase2b_speedup', '1.0x')
        analysis['overall_efficiency'] = {
            'estimated_total_speedup': estimated_speedup,
            'vector_search_improvement': phase2b_metrics.get('faiss_performance_improvement', 0) * 100,
            'cache_efficiency': phase2b_metrics.get('hierarchical_cache_efficiency', 0)
        }
        
        return analysis
    
    def generate_comprehensive_report(self, results: Dict[str, Any]):
        """Generate comprehensive performance report."""
        print("\n" + "="*80)
        print("📊 PHASE 2B PERFORMANCE VALIDATION REPORT")
        print("="*80)
        
        # Performance Summary
        print(f"\n🏆 Performance Summary:")
        speedups = results.get('speedup_improvements', {})
        
        if 'phase1_parallel' in speedups:
            print(f"   • Phase 1 Parallel Speedup: {speedups['phase1_parallel']}")
        
        if 'phase2b_total' in speedups:
            print(f"   • Phase 2B Total Speedup: {speedups['phase2b_total']}")
            
        if 'phase2b_vs_phase1' in speedups:
            print(f"   • Phase 2B vs Phase 1 Improvement: {speedups['phase2b_vs_phase1']}")
        
        # Throughput Comparison
        throughput = results.get('throughput_comparison', {})
        print(f"\n⚡ Throughput Comparison (files/second):")
        print(f"   • Sequential: {throughput.get('sequential', 0):.2f}")
        print(f"   • Phase 1 Parallel: {throughput.get('parallel', 0):.2f}")
        if throughput.get('phase2b', 0) > 0:
            print(f"   • Phase 2B Enhanced: {throughput.get('phase2b', 0):.2f}")
        
        # Phase 2B Detailed Analysis
        if 'phase2b_analysis' in results:
            phase2b = results['phase2b_analysis']
            
            print(f"\n🎯 Phase 2B Enhancement Details:")
            
            # FAISS Performance
            faiss_perf = phase2b.get('faiss_performance', {})
            if faiss_perf:
                print(f"   📈 FAISS Vector Database:")
                print(f"      • Vector Database Size: {faiss_perf.get('vector_database_size', 0)} documents")
                print(f"      • Average Search Time: {faiss_perf.get('average_search_time_ms', 0):.2f}ms")
                print(f"      • Search Throughput: {faiss_perf.get('searches_per_second', 0):.1f} searches/sec")
                print(f"      • GPU Acceleration: {'Yes' if faiss_perf.get('gpu_acceleration') else 'No'}")
            
            # Cache Performance
            cache_perf = phase2b.get('cache_performance', {})
            if cache_perf:
                print(f"   💾 Hierarchical Cache Performance:")
                print(f"      • Overall Hit Rate: {cache_perf.get('cache_hit_rate', 0):.1f}%")
                print(f"      • Memory Cache Hit Rate: {cache_perf.get('memory_cache_hit_rate', 0):.1f}%")
                print(f"      • SSD Cache Hit Rate: {cache_perf.get('ssd_cache_hit_rate', 0):.1f}%")
                print(f"      • Disk Cache Hit Rate: {cache_perf.get('disk_cache_hit_rate', 0):.1f}%")
            
            # ML Optimization
            ml_opt = phase2b.get('ml_optimization', {})
            if ml_opt:
                print(f"   🧠 ML Pattern Recognition:")
                print(f"      • Document Profiles Learned: {ml_opt.get('document_profiles', 0)}")
                print(f"      • Average Confidence: {ml_opt.get('average_confidence', 0):.1f}%")
                print(f"      • Pattern Recognition Success: {ml_opt.get('pattern_recognition_success', 0):.1f}%")
            
            # Overall Efficiency
            efficiency = phase2b.get('overall_efficiency', {})
            if efficiency:
                print(f"   ⚡ Overall Efficiency:")
                print(f"      • Estimated Total Speedup: {efficiency.get('estimated_total_speedup', 'N/A')}")
                print(f"      • Vector Search Improvement: {efficiency.get('vector_search_improvement', 0):.1f}%")
                print(f"      • Cache Efficiency: {efficiency.get('cache_efficiency', 0):.1f}%")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if 'phase2b_analysis' in results:
            cache_hit_rate = results['phase2b_analysis'].get('cache_performance', {}).get('cache_hit_rate', 0)
            if cache_hit_rate < 30:
                print("   • Cache hit rate is low - consider processing similar document types in batches")
            elif cache_hit_rate > 70:
                print("   • Excellent cache performance - Phase 2B is highly effective for your workflow")
            
            faiss_search_time = results['phase2b_analysis'].get('faiss_performance', {}).get('average_search_time_ms', 0)
            if faiss_search_time < 1.0:
                print("   • FAISS performance is excellent - vector database is highly optimized")
            elif faiss_search_time > 10.0:
                print("   • Consider GPU acceleration for FAISS if available")
        
        print("\n🎉 Phase 2B validation completed successfully!")
        
        # Save detailed results
        report_file = self.output_dir / "phase2b_performance_report.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📄 Detailed report saved to: {report_file}")


def main():
    """Main function for Phase 2B performance validation."""
    
    # Parse command line arguments
    if len(sys.argv) >= 2:
        input_directory = Path(sys.argv[1])
    else:
        # Default to data/input directory
        input_directory = Path(__file__).parent.parent.parent.parent.parent / "data" / "input"
    
    if len(sys.argv) >= 3:
        output_directory = Path(sys.argv[2])
    else:
        # Default to data/output/phase2b_validation
        output_directory = Path(__file__).parent.parent.parent.parent.parent / "data" / "output" / "phase2b_validation"
    
    # Validate directories
    if not input_directory.exists():
        print(f"❌ Error: Input directory does not exist: {input_directory}")
        print("Usage: python phase2b_demo.py [input_directory] [output_directory]")
        sys.exit(1)
    
    # Create output directory
    output_directory.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Phase 2B Performance Validation Demo")
    print(f"Input Directory: {input_directory}")
    print(f"Output Directory: {output_directory}")
    
    try:
        # Run validation
        validator = Phase2BPerformanceValidator(input_directory, output_directory)
        results = validator.run_comprehensive_validation()
        
        print(f"\n✅ Validation completed successfully!")
        print(f"Results saved to: {output_directory}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        logger.exception("Phase 2B validation error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
