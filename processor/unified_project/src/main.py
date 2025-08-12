#!/usr/bin/env python3
"""
Unified CLI interface for the ePubs Accessibility Enhancement Project.
"""

import logging
import typer
from pathlib import Path
from typing import Optional

from processor.unified_project.src.services.enhancement_service import EnhancementService
from processor.unified_project.src.batch.advanced_batch_processor import (
    AdvancedBatchProcessor, 
    BatchProcessingConfiguration
)
from processor.unified_project.src.caching.cache_service import CacheService

app = typer.Typer(
    help="ePubs Accessibility Enhancement Tool: A unified CLI for enhancing document accessibility."
)

def setup_logging(verbose: bool):
    """Sets up logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Reduce verbosity of noisy libraries
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("ocrmypdf").setLevel(logging.WARNING)


@app.command()
def process(
    input_path: Path = typer.Argument(
        ..., help="Path to the input PDF file.", exists=True, file_okay=True, dir_okay=False
    ),
    output_path: Path = typer.Argument(
        ..., help="Path to the output PDF file.", writable=True
    ),
    mode: str = typer.Option(
        "academic", help="Processing mode ('academic', 'basic', etc.)."
    ),
    title: str = typer.Option(None, help="Set the document title."),
    author: str = typer.Option(None, help="Set the document author."),
    language: str = typer.Option("en-US", help="Set the document language."),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """
    Process a single PDF file to perform OCR and enhance its accessibility.
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting processing for: {input_path}")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    enhancement_service = EnhancementService()

    # Prepare keyword arguments for the service
    enhancement_kwargs = {
        "title": title,
        "author": author,
        "language": language,
    }

    success = enhancement_service.enhance_document(
        input_path, output_path, mode=mode, **enhancement_kwargs
    )

    if success:
        logger.info(f"Successfully processed file and saved to: {output_path}")
        raise typer.Exit(code=0)
    else:
        logger.error(f"Failed to process file: {input_path}")
        raise typer.Exit(code=1)


@app.command()
def batch_process(
    input_dir: Path = typer.Argument(
        ..., help="Directory containing PDF files to process.", exists=True, file_okay=False, dir_okay=True
    ),
    output_dir: Path = typer.Argument(
        ..., help="Directory where enhanced PDF files will be saved."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """
    Process multiple PDF files in a directory to perform OCR and enhance accessibility.
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting batch processing for directory: {input_dir}")
    
    # Create batch processing configuration
    config = BatchProcessingConfiguration(
        input_dir=str(input_dir),
        output_dir=str(output_dir)
    )
    
    # Initialize and run batch processor
    processor = AdvancedBatchProcessor(config)
    success = processor.process_batch()
    
    if success:
        logger.info("Batch processing completed successfully")
        raise typer.Exit(code=0)
    else:
        logger.error("Batch processing failed")
        raise typer.Exit(code=1)


# Cache management commands
cache_app = typer.Typer(help="Cache management commands")

# Stats subcommand group
stats_app = typer.Typer(help="Performance statistics and reporting")


@stats_app.command()
def show(
    days: int = typer.Option(
        7, "--days", "-d", help="Number of days to include in statistics."
    ),
    format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json, csv"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path (optional)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """Show performance statistics and metrics."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        from ..monitoring.performance_tracker import get_performance_tracker
        
        tracker = get_performance_tracker()
        summary = tracker.get_performance_summary(days)
        
        if format.lower() == "json":
            import json
            output_text = json.dumps(summary, indent=2)
        elif format.lower() == "csv":
            # Simple CSV format for basic metrics
            output_text = "metric,value\n"
            output_text += f"total_operations,{summary['total_operations']}\n"
            output_text += f"success_rate_percent,{summary['success_rate_percent']}\n"
            output_text += f"avg_processing_time_seconds,{summary['avg_processing_time_seconds']}\n"
            output_text += f"cache_hit_rate_percent,{summary['cache_hit_rate_percent']}\n"
        else:  # text format
            output_text = f"""📊 ePubs Performance Statistics ({days} days)
{'=' * 50}

📈 Processing Metrics:
   Total operations: {summary['total_operations']}
   Success rate: {summary['success_rate_percent']}%
   Average processing time: {summary['avg_processing_time_seconds']}s
   Total data processed: {summary['total_bytes_processed']:,} bytes

💾 Cache Performance:
   Cache operations: {summary['cache_operations']}
   Cache hit rate: {summary['cache_hit_rate_percent']}%
   Average response time: {summary['avg_cache_response_time_ms']}ms

🖥️  System Utilization:
   Average memory usage: {summary['avg_memory_usage_mb']} MB
   Average CPU usage: {summary['avg_cpu_usage_percent']}%

🔥 Most Common Operations:"""
            
            for op in summary['common_operations']:
                output_text += f"\n   {op['operation']}: {op['count']} ops ({op['avg_time']}s avg)"
            
            if summary['platform_performance']:
                output_text += f"\n\n🍎 Platform Performance:"
                for perf in summary['platform_performance']:
                    output_text += f"\n   {perf['chip']}: {perf['operations']} ops ({perf['avg_time']}s avg)"
        
        # Output to file or console
        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            print(f"📋 Statistics saved to: {output}")
        else:
            print(output_text)
            
        logger.info(f"Generated performance statistics for {days} days")
        
    except ImportError:
        print("❌ Performance tracking not available")
        logger.error("Performance tracking module not found")
    except Exception as e:
        print(f"❌ Failed to generate statistics: {e}")
        logger.error(f"Statistics generation failed: {e}")


@stats_app.command()
def recent(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Number of recent operations to show."
    ),
    operation: Optional[str] = typer.Option(
        None, "--operation", "-o", help="Filter by operation type."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """Show recent processing operations."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        from ..monitoring.performance_tracker import get_performance_tracker
        
        tracker = get_performance_tracker()
        metrics = tracker.get_recent_metrics(limit * 2)  # Get more in case we need to filter
        
        # Filter by operation if specified
        if operation:
            metrics = [m for m in metrics if m['operation_type'] == operation]
        
        # Limit results
        metrics = metrics[:limit]
        
        if not metrics:
            print("📭 No recent operations found")
            return
        
        print(f"📋 Recent Operations (last {len(metrics)}):")
        print("=" * 80)
        
        for metric in metrics:
            timestamp = metric['timestamp'][:19]  # Remove microseconds
            status = "✅" if metric['success'] else "❌"
            file_path = metric['file_path'] or "N/A"
            if len(file_path) > 40:
                file_path = "..." + file_path[-37:]
            
            enhancers = metric['enhancers_used'] or []
            enhancer_list = ", ".join(enhancers) if enhancers else "None"
            
            print(f"{timestamp} {status} {metric['operation_type']}")
            print(f"   File: {file_path}")
            print(f"   Time: {metric['processing_time_seconds']:.3f}s")
            print(f"   Enhancers: {enhancer_list}")
            if metric['memory_usage_mb']:
                print(f"   Memory: {metric['memory_usage_mb']:.1f} MB")
            print()
            
        logger.info(f"Displayed {len(metrics)} recent operations")
        
    except ImportError:
        print("❌ Performance tracking not available")
        logger.error("Performance tracking module not found")
    except Exception as e:
        print(f"❌ Failed to get recent operations: {e}")
        logger.error(f"Recent operations query failed: {e}")


@stats_app.command()
def cleanup(
    days: int = typer.Option(
        30, "--days", "-d", help="Remove metrics older than this many days."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """Clean up old performance metrics."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        from ..monitoring.performance_tracker import get_performance_tracker
        
        tracker = get_performance_tracker()
        tracker.cleanup_old_metrics(days)
        
        print(f"✅ Cleaned up performance metrics older than {days} days")
        logger.info(f"Performance metrics cleanup completed")
        
    except ImportError:
        print("❌ Performance tracking not available")
        logger.error("Performance tracking module not found")
    except Exception as e:
        print(f"❌ Failed to cleanup metrics: {e}")
        logger.error(f"Metrics cleanup failed: {e}")


# Health check subcommand group
health_app = typer.Typer(help="Health check and system monitoring commands")


@health_app.command()
def check(
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed health information."
    ),
    format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """Perform comprehensive system health check."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        from processor.unified_project.src.monitoring.health_checks import health_check, detailed_health_check
        
        if detailed:
            result = detailed_health_check()
        else:
            result = health_check()
        
        if format.lower() == "json":
            import json
            print(json.dumps(result, indent=2))
        else:
            # Text format
            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unhealthy": "❌"
            }
            
            print(f"{status_emoji.get(result['status'], '❓')} System Health: {result['status'].upper()}")
            print(f"Success Rate: {result['success_rate']}%")
            print(f"Timestamp: {result['timestamp']}")
            
            if 'summary' in result:
                summary = result['summary']
                print(f"\n📊 Summary:")
                print(f"   Total Checks: {summary['total_checks']}")
                print(f"   Healthy: {summary['healthy']}")
                print(f"   Degraded: {summary['degraded']}")
                print(f"   Unhealthy: {summary['unhealthy']}")
            
            if 'checks' in result:
                print(f"\n🔍 Individual Checks:")
                for check in result['checks']:
                    check_emoji = status_emoji.get(check['status'], '❓')
                    print(f"   {check_emoji} {check['name']}: {check['status']}")
                    if check['message']:
                        print(f"      {check['message']}")
        
        logger.info(f"Health check completed: {result['status']}")
        
    except ImportError:
        print("❌ Health check system not available")
        logger.error("Health check module not found")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        logger.error(f"Health check failed: {e}")


@health_app.command()
def status(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """Show current system health status."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        from processor.unified_project.src.monitoring.health_checks import get_health_status
        
        status = get_health_status()
        
        status_emoji = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌",
            "unknown": "❓"
        }
        
        print(f"{status_emoji.get(status['status'], '❓')} Current Status: {status['status'].upper()}")
        
        if status.get('last_check'):
            print(f"Last Check: {status['last_check']}")
        if status.get('checks_performed'):
            print(f"Checks Performed: {status['checks_performed']}")
        if status.get('recent_statuses'):
            recent = status['recent_statuses']
            print(f"Recent Statuses: {', '.join(recent)}")
        
        logger.info(f"Health status retrieved: {status['status']}")
        
    except ImportError:
        print("❌ Health check system not available")
        logger.error("Health check module not found")
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        logger.error(f"Status check failed: {e}")


@health_app.command()
def diagnose(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """Run diagnostic health checks and provide recommendations."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        from processor.unified_project.src.monitoring.health_checks import get_health_checker
        
        checker = get_health_checker()
        result = checker.run_comprehensive_health_check()
        
        print("🔍 ePubs System Diagnostics")
        print("=" * 50)
        
        # Overall status
        status_emoji = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌"
        }
        
        print(f"\n{status_emoji.get(result['status'], '❓')} Overall Status: {result['status'].upper()}")
        print(f"Success Rate: {result['success_rate']}%")
        
        # Individual check details
        print(f"\n📋 Detailed Analysis:")
        for check in result['checks']:
            check_emoji = status_emoji.get(check['status'], '❓')
            print(f"\n{check_emoji} {check['name'].replace('_', ' ').title()}")
            print(f"   Status: {check['status']}")
            if check['message']:
                print(f"   Message: {check['message']}")
            
            # Show key details
            if check['details']:
                details = check['details']
                if 'cpu_percent' in details:
                    print(f"   CPU: {details['cpu_percent']}%")
                if 'memory_percent' in details:
                    print(f"   Memory: {details['memory_percent']}%")
                if 'disk_percent' in details:
                    print(f"   Disk: {details['disk_percent']}%")
                if 'missing_dependencies' in details and details['missing_dependencies']:
                    print(f"   Missing: {', '.join(details['missing_dependencies'])}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if result['status'] == 'unhealthy':
            print("   • Address critical issues before processing documents")
            print("   • Check system resources and dependencies")
            print("   • Verify file system permissions")
        elif result['status'] == 'degraded':
            print("   • Monitor system resources closely")
            print("   • Consider optimizing performance")
            print("   • Review recent changes that may have caused degradation")
        else:
            print("   • System is healthy and ready for production use")
            print("   • Continue regular monitoring")
        
        logger.info(f"Diagnostic completed: {result['status']}")
        
    except ImportError:
        print("❌ Health check system not available")
        logger.error("Health check module not found")
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        logger.error(f"Diagnostic failed: {e}")


# Add subcommands to main app
app.add_typer(cache_app, name="cache", help="Cache management commands")
app.add_typer(stats_app, name="stats", help="Performance statistics and reporting")
app.add_typer(health_app, name="health", help="Health check and system monitoring commands")


@cache_app.command()
def clear(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """Clear all cached data."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    cache_service = CacheService()
    deleted_count = cache_service.clear_cache()
    
    print(f"✅ Cleared {deleted_count} cache entries")
    logger.info(f"Cache cleared: {deleted_count} entries removed")


@cache_app.command()
def stats(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """Show cache statistics and usage information."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    cache_service = CacheService()
    stats = cache_service.get_cache_stats()
    
    if 'error' in stats:
        print(f"❌ Error getting cache stats: {stats['error']}")
        raise typer.Exit(code=1)
    
    print("📊 Cache Statistics")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Total size: {stats['total_size_mb']} MB")
    print(f"   Hit rate: {stats['hit_rate_percent']}%")
    print(f"   Recent access: {stats['recent_access_count']} entries")
    print(f"   Cache directory: {stats['cache_directory']}")
    
    if stats['by_type']:
        print("\n📋 By Data Type:")
        for data_type, info in stats['by_type'].items():
            size_mb = round(info['size'] / (1024 * 1024), 2)
            print(f"   {data_type}: {info['count']} entries, {size_mb} MB")
    
    # Health check
    health = cache_service.is_cache_healthy()
    if health['healthy']:
        print("\n✅ Cache is healthy")
    else:
        print(f"\n⚠️  Cache issues detected:")
        for issue in health['issues']:
            print(f"   • {issue}")
        if health['recommendations']:
            print("   Recommendations:")
            for rec in health['recommendations']:
                print(f"   • {rec}")


@cache_app.command()
def prune(
    days: int = typer.Option(
        30, "--days", "-d", help="Remove entries older than this many days."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """Remove expired and old cache entries."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    cache_service = CacheService()
    
    # Remove expired entries
    expired_count = cache_service.prune_cache()
    
    # Remove old entries
    old_count = cache_service.cleanup_old_cache(days)
    
    total_removed = expired_count + old_count
    
    print(f"✅ Pruned cache:")
    print(f"   Expired entries: {expired_count}")
    print(f"   Old entries (>{days} days): {old_count}")
    print(f"   Total removed: {total_removed}")
    
    logger.info(f"Cache pruned: {total_removed} entries removed")


if __name__ == "__main__":
    app()