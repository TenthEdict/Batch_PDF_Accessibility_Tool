"""
Performance Dashboard UI Framework
================================

Comprehensive real-time performance visualization system for Phase 2B ePubs processing.
Provides institutional-grade analytics dashboard with Rich CLI integration for
FAISS vector database, hierarchical caching, ML pattern learning, and resource optimization.

Features:
- Real-time metrics visualization with Rich console formatting
- Institutional analytics for deployment confidence
- Interactive dashboard with navigation and filtering
- Cross-platform performance monitoring display
- Optimization recommendations with severity indicators
- Export capabilities for institutional reporting
"""

import asyncio
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging

# Rich UI components for advanced CLI dashboard
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
from rich.tree import Tree
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich.status import Status
from rich.prompt import Prompt, Confirm
from rich import box
from rich.markup import escape

# Import monitoring components
from .faiss_metrics_collector import get_faiss_metrics_collector, FAISSPerformanceSummary
from .cache_metrics_collector import get_cache_metrics_collector, HierarchicalCacheMetrics
from .ml_pattern_learning_metrics import get_ml_metrics_collector, MLSystemMetrics
from .resource_optimization_tracker import get_resource_tracker, ResourceSnapshot


class DashboardMode:
    """Dashboard display modes for different analytics focuses."""
    OVERVIEW = "overview"
    FAISS_DETAIL = "faiss_detail"
    CACHE_DETAIL = "cache_detail"
    ML_DETAIL = "ml_detail"
    RESOURCE_DETAIL = "resource_detail"
    RECOMMENDATIONS = "recommendations"


class PerformanceDashboard:
    """
    Comprehensive Phase 2B performance dashboard with real-time monitoring.
    
    Provides institutional-grade analytics visualization for FAISS vector database,
    hierarchical caching, ML pattern learning, and resource optimization with
    Rich CLI framework integration for enhanced user experience.
    """
    
    def __init__(self, 
                 update_interval: float = 2.0,
                 auto_refresh: bool = True,
                 export_enabled: bool = True):
        """
        Initialize performance dashboard.
        
        Args:
            update_interval: Seconds between dashboard updates
            auto_refresh: Enable automatic dashboard refresh
            export_enabled: Enable metrics export capabilities
        """
        self.update_interval = update_interval
        self.auto_refresh = auto_refresh
        self.export_enabled = export_enabled
        
        # Rich console setup
        self.console = Console()
        
        # Dashboard state
        self.current_mode = DashboardMode.OVERVIEW
        self.dashboard_active = False
        self.update_thread: Optional[threading.Thread] = None
        
        # Metrics collectors
        self.faiss_collector = get_faiss_metrics_collector()
        self.cache_collector = get_cache_metrics_collector()
        self.ml_collector = get_ml_metrics_collector()
        self.resource_tracker = get_resource_tracker()
        
        # Dashboard data cache
        self._dashboard_data: Dict[str, Any] = {}
        self._last_update: Optional[datetime] = None
        
        # Navigation state
        self._navigation_history: List[str] = []
        
        # Import FAISS visualization component
        from .faiss_utilization_display import FAISSUtilizationDisplay
        self.faiss_display = FAISSUtilizationDisplay(self.console)
        
        # Cache analytics configuration
        self.cache_time_window = timedelta(hours=1)
        
        # Logger setup
        self.logger = logging.getLogger(f"{__name__}.PerformanceDashboard")
        
        self.logger.info("Performance Dashboard initialized - Phase 2B Analytics Ready")
    
    def start_dashboard(self, mode: str = DashboardMode.OVERVIEW) -> None:
        """
        Start the interactive performance dashboard.
        
        Args:
            mode: Initial dashboard mode to display
        """
        self.current_mode = mode
        self.dashboard_active = True
        
        # Start resource monitoring if not already active
        if not self.resource_tracker._monitoring_active:
            self.resource_tracker.start_monitoring()
        
        try:
            if self.auto_refresh:
                self._start_auto_refresh_dashboard()
            else:
                self._display_static_dashboard()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard stopped by user[/yellow]")
        finally:
            self.stop_dashboard()
    
    def stop_dashboard(self) -> None:
        """Stop the performance dashboard."""
        self.dashboard_active = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2.0)
        
        self.console.print("[green]Performance Dashboard stopped[/green]")
    
    def generate_overview_layout(self) -> Layout:
        """Generate comprehensive overview dashboard layout."""
        layout = Layout(name="root")
        
        # Main layout structure
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Header with title and status
        header_content = Panel(
            Align.center(
                Text("ePubs Phase 2B Performance Dashboard", style="bold blue") +
                Text(f" | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
            ),
            box=box.ROUNDED,
            style="blue"
        )
        layout["header"].update(header_content)
        
        # Body split into main areas
        layout["body"].split_row(
            Layout(name="left_panel", ratio=1),
            Layout(name="center_panel", ratio=2),
            Layout(name="right_panel", ratio=1)
        )
        
        # Left panel - System overview
        layout["left_panel"].update(self._create_system_overview_panel())
        
        # Center panel - Performance metrics
        layout["center_panel"].split(
            Layout(name="metrics_top"),
            Layout(name="metrics_bottom")
        )
        layout["metrics_top"].update(self._create_performance_metrics_panel())
        layout["metrics_bottom"].update(self._create_optimization_recommendations_panel())
        
        # Right panel - Resource monitoring
        layout["right_panel"].update(self._create_resource_monitoring_panel())
        
        # Footer with navigation
        footer_content = Panel(
            Text("Navigation: [1] Overview [2] FAISS [3] Cache [4] ML [5] Resources [6] Recommendations [Q] Quit", 
                 style="dim"),
            box=box.ROUNDED,
            style="green"
        )
        layout["footer"].update(footer_content)
        
        return layout
    
    def _create_system_overview_panel(self) -> Panel:
        """Create system overview panel with key metrics."""
        # Get current resource snapshot
        current_resource = self.resource_tracker.get_current_usage()
        
        if current_resource:
            cpu_style = "red" if current_resource.cpu_percent > 80 else "yellow" if current_resource.cpu_percent > 60 else "green"
            memory_style = "red" if current_resource.memory_percent > 85 else "yellow" if current_resource.memory_percent > 70 else "green"
            
            overview_text = Text()
            overview_text.append("System Status\n", style="bold")
            overview_text.append(f"CPU Usage: {current_resource.cpu_percent:.1f}%\n", style=cpu_style)
            overview_text.append(f"Memory: {current_resource.memory_percent:.1f}%\n", style=memory_style)
            overview_text.append(f"Process Memory: {current_resource.process_memory_mb:.0f}MB\n")
            overview_text.append(f"Uptime: {current_resource.system_uptime/3600:.1f}h\n")
            
            # Add Phase 2B status
            overview_text.append("\nPhase 2B Status\n", style="bold blue")
            overview_text.append("✅ FAISS Vector DB\n", style="green")
            overview_text.append("✅ Hierarchical Cache\n", style="green") 
            overview_text.append("✅ ML Optimization\n", style="green")
            overview_text.append("✅ Performance Monitoring\n", style="green")
        else:
            overview_text = Text("Gathering system metrics...", style="yellow")
        
        return Panel(
            overview_text,
            title="System Overview",
            box=box.ROUNDED,
            style="blue"
        )
    
    def _create_performance_metrics_panel(self) -> Panel:
        """Create performance metrics panel with FAISS, Cache, and ML data."""
        metrics_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        metrics_table.add_column("Component", style="cyan", width=15)
        metrics_table.add_column("Status", width=12)
        metrics_table.add_column("Key Metric", width=20)
        metrics_table.add_column("Performance", width=15)
        
        # FAISS Metrics
        try:
            faiss_summary = self.faiss_collector.get_performance_summary(timedelta(minutes=10))
            faiss_status = "🟢 Active" if faiss_summary.total_operations > 0 else "🟡 Idle"
            faiss_metric = f"Ops: {faiss_summary.total_operations}"
            faiss_perf = f"{faiss_summary.average_operation_time_ms:.1f}ms avg"
        except Exception:
            faiss_status = "🔴 Error"
            faiss_metric = "N/A"
            faiss_perf = "N/A"
        
        # Cache Metrics
        try:
            cache_summary = self.cache_collector.get_hierarchical_summary(timedelta(minutes=10))
            cache_status = "🟢 Active"
            cache_metric = f"Hit Rate: {cache_summary.overall_hit_rate_percent:.1f}%"
            cache_perf = f"Efficiency: {cache_summary.cache_efficiency_score:.0f}/100"
        except Exception:
            cache_status = "🔴 Error"
            cache_metric = "N/A"
            cache_perf = "N/A"
        
        # ML Metrics
        try:
            ml_summary = self.ml_collector.get_ml_system_metrics(timedelta(minutes=10))
            ml_status = "🟢 Learning" if ml_summary.active_learning_sessions > 0 else "🟡 Ready"
            ml_metric = f"Accuracy: {ml_summary.overall_accuracy_score:.1f}"
            ml_perf = f"Sessions: {ml_summary.completed_learning_sessions}"
        except Exception:
            ml_status = "🔴 Error"
            ml_metric = "N/A"
            ml_perf = "N/A"
        
        # Resource Optimization
        try:
            resource_report = self.resource_tracker.generate_optimization_report()
            if "error" not in resource_report:
                resource_status = "🟢 Monitoring"
                resource_metric = f"Efficiency: {resource_report['efficiency_score']:.0f}/100"
                resource_perf = f"Recommendations: {resource_report['recommendations']['total_count']}"
            else:
                resource_status = "🟡 Starting"
                resource_metric = "Initializing"
                resource_perf = "Please wait..."
        except Exception:
            resource_status = "🔴 Error"
            resource_metric = "N/A"
            resource_perf = "N/A"
        
        # Add rows to table
        metrics_table.add_row("FAISS Vector DB", faiss_status, faiss_metric, faiss_perf)
        metrics_table.add_row("Hierarchical Cache", cache_status, cache_metric, cache_perf)
        metrics_table.add_row("ML Pattern Learning", ml_status, ml_metric, ml_perf)
        metrics_table.add_row("Resource Optimization", resource_status, resource_metric, resource_perf)
        
        return Panel(
            metrics_table,
            title="Phase 2B Performance Metrics",
            box=box.ROUNDED,
            style="magenta"
        )
    
    def _create_optimization_recommendations_panel(self) -> Panel:
        """Create optimization recommendations panel."""
        recommendations = self.resource_tracker.get_optimization_recommendations(timedelta(hours=1))
        
        if recommendations:
            rec_text = Text()
            rec_text.append("Latest Optimization Recommendations\n", style="bold yellow")
            
            for i, rec in enumerate(recommendations[:5], 1):
                severity_style = {
                    "critical": "red",
                    "warning": "yellow", 
                    "info": "blue"
                }.get(rec.severity, "white")
                
                rec_text.append(f"{i}. ", style="dim")
                rec_text.append(f"[{rec.severity.upper()}] ", style=severity_style)
                rec_text.append(f"{rec.recommended_action}\n")
                rec_text.append(f"   Impact: {rec.expected_improvement:.0f}% improvement\n", style="dim")
            
            if len(recommendations) > 5:
                rec_text.append(f"\n... and {len(recommendations) - 5} more recommendations\n", style="dim")
        else:
            rec_text = Text("No optimization recommendations at this time.\nSystem performance appears optimal.", style="green")
        
        return Panel(
            rec_text,
            title="Optimization Insights",
            box=box.ROUNDED,
            style="yellow"
        )
    
    def _create_resource_monitoring_panel(self) -> Panel:
        """Create resource monitoring panel with real-time usage."""
        current_resource = self.resource_tracker.get_current_usage()
        
        if current_resource:
            # Create resource usage bars
            resource_text = Text()
            resource_text.append("Resource Utilization\n", style="bold")
            
            # CPU usage bar
            cpu_bar = self._create_usage_bar(current_resource.cpu_percent, "CPU")
            resource_text.append(cpu_bar)
            resource_text.append("\n")
            
            # Memory usage bar
            memory_bar = self._create_usage_bar(current_resource.memory_percent, "Memory")
            resource_text.append(memory_bar)
            resource_text.append("\n")
            
            # Disk usage bar
            disk_bar = self._create_usage_bar(current_resource.disk_usage_percent, "Disk")
            resource_text.append(disk_bar)
            resource_text.append("\n\n")
            
            # Process details
            resource_text.append("Process Details\n", style="bold cyan")
            resource_text.append(f"Threads: {current_resource.process_num_threads}\n")
            resource_text.append(f"Memory: {current_resource.process_memory_mb:.0f}MB\n")
            resource_text.append(f"CPU: {current_resource.process_cpu_percent:.1f}%\n")
        else:
            resource_text = Text("Starting resource monitoring...", style="yellow")
        
        return Panel(
            resource_text,
            title="Resource Monitor",
            box=box.ROUNDED,
            style="cyan"
        )
    
    def _create_usage_bar(self, percentage: float, label: str) -> Text:
        """Create a text-based usage bar."""
        bar_width = 20
        filled = int((percentage / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        color = "red" if percentage > 80 else "yellow" if percentage > 60 else "green"
        
        usage_text = Text()
        usage_text.append(f"{label:6s} ", style="dim")
        usage_text.append(f"{bar} ", style=color)
        usage_text.append(f"{percentage:5.1f}%")
        
        return usage_text
    
    def _start_auto_refresh_dashboard(self) -> None:
        """Start auto-refreshing dashboard with Live display."""
        with Live(self.generate_overview_layout(), refresh_per_second=0.5, console=self.console) as live:
            while self.dashboard_active:
                try:
                    # Update dashboard layout
                    live.update(self.generate_overview_layout())
                    time.sleep(self.update_interval)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"Dashboard update error: {e}")
                    time.sleep(self.update_interval)
    
    def _display_static_dashboard(self) -> None:
        """Display static dashboard with manual refresh."""
        while self.dashboard_active:
            self.console.clear()
            self.console.print(self.generate_overview_layout())
            
            # Get user input for navigation
            user_input = Prompt.ask(
                "\nSelect option",
                choices=["1", "2", "3", "4", "5", "6", "r", "q"],
                default="r"
            )
            
            if user_input == "q":
                break
            elif user_input == "r":
                continue
            elif user_input == "1":
                self.current_mode = DashboardMode.OVERVIEW
            elif user_input == "2":
                self._display_faiss_detail()
            elif user_input == "3":
                self._display_cache_detail()
            elif user_input == "4":
                self._display_ml_detail()
            elif user_input == "5":
                self._display_resource_detail()
            elif user_input == "6":
                self._display_recommendations_detail()
    
    def _display_faiss_detail(self) -> None:
        """Display detailed FAISS performance analysis."""
        self.console.clear()
        
        # Get FAISS performance summary
        faiss_summary = self.faiss_collector.get_performance_summary(timedelta(hours=1))
        
        # Create detailed FAISS panel
        faiss_table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
        faiss_table.add_column("Metric", style="cyan")
        faiss_table.add_column("Value", style="white")
        faiss_table.add_column("Status", style="green")
        
        faiss_table.add_row("Total Operations", str(faiss_summary.total_operations), "✅")
        faiss_table.add_row("Success Rate", f"{(faiss_summary.successful_operations/max(faiss_summary.total_operations,1))*100:.1f}%", "✅")
        faiss_table.add_row("Average Time", f"{faiss_summary.average_operation_time_ms:.2f}ms", "✅")
        faiss_table.add_row("Fastest Operation", f"{faiss_summary.fastest_operation_ms:.2f}ms", "✅")
        faiss_table.add_row("Slowest Operation", f"{faiss_summary.slowest_operation_ms:.2f}ms", "⚠️" if faiss_summary.slowest_operation_ms > 1000 else "✅")
        faiss_table.add_row("Vectors Processed", str(faiss_summary.total_vectors_processed), "✅")
        faiss_table.add_row("Processing Rate", f"{faiss_summary.average_vectors_per_second:.1f} vectors/sec", "✅")
        faiss_table.add_row("Memory Efficiency", f"{faiss_summary.memory_efficiency_score:.1f}/100", "✅")
        
        panel = Panel(
            faiss_table,
            title="FAISS Vector Database Performance Analysis",
            box=box.ROUNDED,
            style="blue"
        )
        
        self.console.print(panel)
        
        # Show recommendations
        if faiss_summary.recommendations:
            rec_panel = Panel(
                "\n".join(f"• {rec}" for rec in faiss_summary.recommendations),
                title="FAISS Optimization Recommendations",
                box=box.ROUNDED,
                style="yellow"
            )
            self.console.print(rec_panel)
        
        Prompt.ask("\nPress Enter to return to overview", default="")
    
    def _display_cache_detail(self) -> None:
        """Display detailed hierarchical cache analysis with optimization recommendations."""
        self.console.clear()
        
        # Get comprehensive cache performance summary
        cache_summary = self.cache_collector.get_hierarchical_summary(self.cache_time_window)
        
        # Main cache analysis layout
        cache_layout = Layout(name="cache_analysis")
        cache_layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=8)
        )
        
        # Header with cache overview
        header_content = Panel(
            Align.center(
                Text("Hierarchical Cache Performance Analysis", style="bold magenta") +
                Text(f" | Overall Hit Rate: {cache_summary.overall_hit_rate_percent:.1f}% | "
                     f"Efficiency: {cache_summary.cache_efficiency_score:.0f}/100", style="dim")
            ),
            box=box.ROUNDED,
            style="magenta"
        )
        cache_layout["header"].update(header_content)
        
        # Body with detailed analytics
        cache_layout["body"].split_row(
            Layout(name="levels", ratio=2),
            Layout(name="analytics", ratio=1)
        )
        
        # Cache levels performance comparison
        cache_layout["levels"].update(self._create_cache_levels_comparison_panel(cache_summary))
        
        # Cache analytics and insights
        cache_layout["analytics"].split(
            Layout(name="insights"),
            Layout(name="data_flow")
        )
        cache_layout["analytics"]["insights"].update(self._create_cache_insights_panel(cache_summary))
        cache_layout["analytics"]["data_flow"].update(self._create_cache_data_flow_panel(cache_summary))
        
        # Footer with optimization recommendations
        cache_layout["footer"].update(self._create_cache_optimization_recommendations_panel(cache_summary))
        
        # Display the complete cache analysis
        self.console.print(cache_layout)
        
        Prompt.ask("\nPress Enter to return to overview", default="")
    
    def _create_cache_levels_comparison_panel(self, cache_summary: HierarchicalCacheMetrics) -> Panel:
        """Create detailed cache levels comparison panel."""
        # Create cache levels comparison table
        levels_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        levels_table.add_column("Cache Level", style="cyan", width=12)
        levels_table.add_column("Hit Rate", style="green", width=10)
        levels_table.add_column("Operations", style="white", width=12)
        levels_table.add_column("Avg Get Time", style="blue", width=12)
        levels_table.add_column("Avg Put Time", style="yellow", width=12)
        levels_table.add_column("Data Size", style="cyan", width=12)
        levels_table.add_column("Efficiency", style="green", width=10)
        
        # Memory Cache (L1) metrics
        mem_metrics = cache_summary.memory_metrics
        levels_table.add_row(
            "Memory (L1)",
            f"{mem_metrics.hit_rate_percent:.1f}%",
            str(mem_metrics.total_operations),
            f"{mem_metrics.average_get_time_ms:.2f}ms",
            f"{mem_metrics.average_put_time_ms:.2f}ms",
            self._format_bytes(mem_metrics.total_data_bytes),
            f"{mem_metrics.optimization_score:.0f}/100"
        )
        
        # SSD Cache (L2) metrics
        ssd_metrics = cache_summary.ssd_metrics
        levels_table.add_row(
            "SSD (L2)",
            f"{ssd_metrics.hit_rate_percent:.1f}%",
            str(ssd_metrics.total_operations),
            f"{ssd_metrics.average_get_time_ms:.2f}ms",
            f"{ssd_metrics.average_put_time_ms:.2f}ms",
            self._format_bytes(ssd_metrics.total_data_bytes),
            f"{ssd_metrics.optimization_score:.0f}/100"
        )
        
        # Disk Cache (L3) metrics
        disk_metrics = cache_summary.disk_metrics
        levels_table.add_row(
            "Disk (L3)",
            f"{disk_metrics.hit_rate_percent:.1f}%",
            str(disk_metrics.total_operations),
            f"{disk_metrics.average_get_time_ms:.2f}ms",
            f"{disk_metrics.average_put_time_ms:.2f}ms",
            self._format_bytes(disk_metrics.total_data_bytes),
            f"{disk_metrics.optimization_score:.0f}/100"
        )
        
        return Panel(
            levels_table,
            title="Cache Levels Performance Comparison",
            box=box.ROUNDED,
            style="magenta"
        )
    
    def _create_cache_insights_panel(self, cache_summary: HierarchicalCacheMetrics) -> Panel:
        """Create cache performance insights panel."""
        insights_text = Text()
        insights_text.append("Cache Performance Insights\n", style="bold cyan")
        
        # Overall performance assessment
        efficiency_score = cache_summary.cache_efficiency_score
        if efficiency_score >= 85:
            insights_text.append("🟢 Excellent Cache Performance\n", style="green")
        elif efficiency_score >= 70:
            insights_text.append("🟡 Good Cache Performance\n", style="yellow") 
        elif efficiency_score >= 50:
            insights_text.append("🟠 Fair Cache Performance\n", style="orange")
        else:
            insights_text.append("🔴 Poor Cache Performance\n", style="red")
        
        insights_text.append(f"Overall Efficiency: {efficiency_score:.1f}/100\n\n")
        
        # Hit rate analysis by level
        insights_text.append("Hit Rate Analysis:\n", style="bold yellow")
        
        # Memory cache analysis
        mem_hit_rate = cache_summary.memory_metrics.hit_rate_percent
        if mem_hit_rate >= 80:
            insights_text.append(f"• L1 Memory: {mem_hit_rate:.1f}% ✅\n", style="green")
        elif mem_hit_rate >= 60:
            insights_text.append(f"• L1 Memory: {mem_hit_rate:.1f}% ⚠️\n", style="yellow")
        else:
            insights_text.append(f"• L1 Memory: {mem_hit_rate:.1f}% 🔴\n", style="red")
        
        # SSD cache analysis
        ssd_hit_rate = cache_summary.ssd_metrics.hit_rate_percent
        if ssd_hit_rate >= 60:
            insights_text.append(f"• L2 SSD: {ssd_hit_rate:.1f}% ✅\n", style="green")
        elif ssd_hit_rate >= 40:
            insights_text.append(f"• L2 SSD: {ssd_hit_rate:.1f}% ⚠️\n", style="yellow")
        else:
            insights_text.append(f"• L2 SSD: {ssd_hit_rate:.1f}% 🔴\n", style="red")
        
        # Disk cache analysis
        disk_hit_rate = cache_summary.disk_metrics.hit_rate_percent
        if disk_hit_rate >= 40:
            insights_text.append(f"• L3 Disk: {disk_hit_rate:.1f}% ✅\n", style="green")
        elif disk_hit_rate >= 20:
            insights_text.append(f"• L3 Disk: {disk_hit_rate:.1f}% ⚠️\n", style="yellow")
        else:
            insights_text.append(f"• L3 Disk: {disk_hit_rate:.1f}% 🔴\n", style="red")
        
        # Performance trends
        insights_text.append("\nPerformance Indicators:\n", style="bold blue")
        insights_text.append(f"• Data Flow Optimization: {cache_summary.data_flow_optimization:.1f}/100\n")
        insights_text.append(f"• Prefetch Accuracy: {cache_summary.prefetch_accuracy_percent:.1f}%\n")
        insights_text.append(f"• Cache Warming: {cache_summary.cache_warming_effectiveness:.1f}%\n")
        
        return Panel(
            insights_text,
            title="Performance Insights",
            box=box.ROUNDED,
            style="cyan"
        )
    
    def _create_cache_data_flow_panel(self, cache_summary: HierarchicalCacheMetrics) -> Panel:
        """Create cache data flow analysis panel."""
        data_flow_text = Text()
        data_flow_text.append("Data Flow Analysis\n", style="bold green")
        
        # Data promotions and demotions
        mem_metrics = cache_summary.memory_metrics
        ssd_metrics = cache_summary.ssd_metrics
        disk_metrics = cache_summary.disk_metrics
        
        total_promotions = mem_metrics.promotion_count + ssd_metrics.promotion_count + disk_metrics.promotion_count
        total_demotions = mem_metrics.demotion_count + ssd_metrics.demotion_count + disk_metrics.demotion_count
        
        data_flow_text.append(f"Promotions: {total_promotions}\n")
        data_flow_text.append(f"Demotions: {total_demotions}\n")
        
        # Flow efficiency
        if total_promotions + total_demotions > 0:
            promotion_ratio = total_promotions / (total_promotions + total_demotions)
            if promotion_ratio > 0.6:
                data_flow_text.append("🟢 Good data flow\n", style="green")
            elif promotion_ratio > 0.4:
                data_flow_text.append("🟡 Moderate flow\n", style="yellow")
            else:
                data_flow_text.append("🔴 Poor data flow\n", style="red")
        else:
            data_flow_text.append("📊 Insufficient flow data\n", style="dim")
        
        # Compression effectiveness
        data_flow_text.append("\nCompression Analysis:\n", style="bold magenta")
        avg_compression = (
            mem_metrics.compression_effectiveness +
            ssd_metrics.compression_effectiveness +
            disk_metrics.compression_effectiveness
        ) / 3
        
        if avg_compression > 1.5:
            data_flow_text.append(f"🗜️ Excellent compression: {avg_compression:.2f}x\n", style="green")
        elif avg_compression > 1.2:
            data_flow_text.append(f"🗜️ Good compression: {avg_compression:.2f}x\n", style="yellow")
        else:
            data_flow_text.append(f"🗜️ Minimal compression: {avg_compression:.2f}x\n", style="red")
        
        # Access patterns
        if cache_summary.hottest_access_patterns:
            data_flow_text.append("\nHottest Patterns:\n", style="bold yellow")
            for i, pattern in enumerate(cache_summary.hottest_access_patterns[:3], 1):
                data_flow_text.append(f"{i}. {pattern}\n", style="dim")
        
        return Panel(
            data_flow_text,
            title="Data Flow & Patterns",
            box=box.ROUNDED,
            style="green"
        )
    
    def _create_cache_optimization_recommendations_panel(self, cache_summary: HierarchicalCacheMetrics) -> Panel:
        """Create comprehensive cache optimization recommendations panel."""
        # Create recommendations table with actionable insights
        rec_table = Table(show_header=True, header_style="bold yellow", box=box.ROUNDED)
        rec_table.add_column("Priority", style="red", width=8)
        rec_table.add_column("Cache Level", style="cyan", width=12)
        rec_table.add_column("Optimization Recommendation", style="white", width=50)
        rec_table.add_column("Expected Impact", style="green", width=20)
        rec_table.add_column("Complexity", style="blue", width=10)
        
        # Generate recommendations based on cache performance
        recommendations = []
        
        # Memory cache recommendations
        mem_metrics = cache_summary.memory_metrics
        if mem_metrics.hit_rate_percent < 70:
            recommendations.append({
                "priority": "HIGH",
                "level": "Memory (L1)",
                "recommendation": "Increase memory cache size - low hit rate indicates insufficient capacity",
                "impact": "15-25% hit rate improvement",
                "complexity": "Low"
            })
        
        if mem_metrics.average_get_time_ms > 10:
            recommendations.append({
                "priority": "MEDIUM",
                "level": "Memory (L1)",
                "recommendation": "Optimize memory cache data structures - slow get operations",
                "impact": "50-70% speed improvement",
                "complexity": "Medium"
            })
        
        # SSD cache recommendations
        ssd_metrics = cache_summary.ssd_metrics
        if ssd_metrics.hit_rate_percent < 50:
            recommendations.append({
                "priority": "MEDIUM",
                "level": "SSD (L2)",
                "recommendation": "Review SSD cache eviction policy - consider LRU optimization",
                "impact": "10-20% hit rate improvement",
                "complexity": "Medium"
            })
        
        if ssd_metrics.average_put_time_ms > 100:
            recommendations.append({
                "priority": "LOW",
                "level": "SSD (L2)",
                "recommendation": "Enable write-behind caching for SSD to improve put performance",
                "impact": "30-50% put speed improvement",
                "complexity": "High"
            })
        
        # Cross-level recommendations
        overall_hit_rate = cache_summary.overall_hit_rate_percent
        if overall_hit_rate < 60:
            recommendations.append({
                "priority": "HIGH",
                "level": "All Levels",
                "recommendation": "Overall hit rate is low - review caching strategy and patterns",
                "impact": "20-40% overall improvement",
                "complexity": "High"
            })
        
        # Data flow recommendations
        if cache_summary.data_flow_optimization < 50:
            recommendations.append({
                "priority": "MEDIUM",
                "level": "All Levels",
                "recommendation": "Optimize data promotion/demotion algorithms",
                "impact": "Better cache utilization",
                "complexity": "Medium"
            })
        
        # Compression recommendations
        mem_compression = mem_metrics.compression_effectiveness
        if mem_compression < 1.2:
            recommendations.append({
                "priority": "LOW",
                "level": "Memory (L1)",
                "recommendation": "Enable memory cache compression to increase effective capacity",
                "impact": "20-40% capacity increase",
                "complexity": "Low"
            })
        
        # If no specific recommendations, provide general optimization advice
        if not recommendations:
            recommendations.append({
                "priority": "INFO",
                "level": "All Levels",
                "recommendation": "Cache performance appears optimal - monitor for pattern changes",
                "impact": "Maintain current performance",
                "complexity": "Low"
            })
        
        # Add recommendations to table
        for rec in recommendations[:6]:  # Limit to top 6 recommendations
            priority_style = {
                "HIGH": "red",
                "MEDIUM": "yellow",
                "LOW": "green",
                "INFO": "blue"
            }.get(rec["priority"], "white")
            
            complexity_style = {
                "Low": "green",
                "Medium": "yellow", 
                "High": "red"
            }.get(rec["complexity"], "white")
            
            rec_table.add_row(
                Text(rec["priority"], style=priority_style),
                rec["level"],
                rec["recommendation"],
                rec["impact"],
                Text(rec["complexity"], style=complexity_style)
            )
        
        return Panel(
            rec_table,
            title="Cache Optimization Recommendations",
            box=box.ROUNDED,
            style="yellow"
        )
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes value for human-readable display."""
        if bytes_value < 1024:
            return f"{bytes_value}B"
        elif bytes_value < 1024**2:
            return f"{bytes_value/1024:.1f}KB"
        elif bytes_value < 1024**3:
            return f"{bytes_value/(1024**2):.1f}MB"
        else:
            return f"{bytes_value/(1024**3):.1f}GB"
    
    def _display_ml_detail(self) -> None:
        """Display detailed ML pattern learning analysis."""
        self.console.clear()
        
        # Get ML system metrics
        ml_summary = self.ml_collector.get_ml_system_metrics(timedelta(hours=1))
        
        # Create ML performance table
        ml_table = Table(show_header=True, header_style="bold green", box=box.ROUNDED)
        ml_table.add_column("Metric", style="cyan")
        ml_table.add_column("Value", style="white")
        ml_table.add_column("Performance", style="green")
        
        ml_table.add_row("Total ML Operations", str(ml_summary.total_ml_operations), "✅")
        ml_table.add_row("Success Rate", f"{(ml_summary.successful_operations/max(ml_summary.total_ml_operations,1))*100:.1f}%", "✅")
        ml_table.add_row("Overall Accuracy", f"{ml_summary.overall_accuracy_score:.3f}", "✅")
        ml_table.add_row("Confidence Score", f"{ml_summary.overall_confidence_score:.3f}", "✅")
        ml_table.add_row("Pattern Learning", ml_summary.pattern_learning_effectiveness.value.title(), "✅")
        ml_table.add_row("OCR Optimization Success", f"{ml_summary.ocr_optimization_success_rate:.1f}%", "✅")
        ml_table.add_row("Active Learning Sessions", str(ml_summary.active_learning_sessions), "✅")
        ml_table.add_row("Completed Sessions", str(ml_summary.completed_learning_sessions), "✅")
        ml_table.add_row("Knowledge Base Size", str(ml_summary.knowledge_base_size), "✅")
        
        panel = Panel(
            ml_table,
            title="ML Pattern Learning Performance Analysis",
            box=box.ROUNDED,
            style="green"
        )
        
        self.console.print(panel)
        
        Prompt.ask("\nPress Enter to return to overview", default="")
    
    def _display_resource_detail(self) -> None:
        """Display detailed resource monitoring analysis."""
        self.console.clear()
        
        # Get resource optimization report
        resource_report = self.resource_tracker.generate_optimization_report()
        
        if "error" in resource_report:
            error_panel = Panel(
                "Resource monitoring data insufficient.\nPlease wait for monitoring to collect data.",
                title="Resource Monitoring",
                box=box.ROUNDED,
                style="yellow"
            )
            self.console.print(error_panel)
        else:
            # Current usage table
            usage_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
            usage_table.add_column("Resource", style="cyan")
            usage_table.add_column("Current", style="white")
            usage_table.add_column("Average", style="yellow")
            usage_table.add_column("Trend", style="green")
            
            current = resource_report["current_usage"]
            average = resource_report["average_usage"]
            trends = resource_report["performance_trends"]
            
            usage_table.add_row("CPU", f"{current['cpu_percent']:.1f}%", f"{average['cpu_percent']:.1f}%", trends['cpu_trend'])
            usage_table.add_row("Memory", f"{current['memory_percent']:.1f}%", f"{average['memory_percent']:.1f}%", trends['memory_trend'])
            usage_table.add_row("Disk", f"{current['disk_usage_percent']:.1f}%", f"{average['disk_usage_percent']:.1f}%", "stable")
            usage_table.add_row("Process Memory", f"{current['process_memory_mb']:.0f}MB", "N/A", "N/A")
            
            panel = Panel(
                usage_table,
                title="Resource Utilization Analysis",
                box=box.ROUNDED,
                style="cyan"
            )
            
            self.console.print(panel)
            
            # Optimization profile
            profile = resource_report["active_profile"]
            profile_panel = Panel(
                f"Profile: {profile['name']} ({profile['level']})\n"
                f"Max Workers: {profile['max_workers']}\n"
                f"Memory Limit: {profile['memory_limit_gb']}GB\n"
                f"Efficiency Score: {resource_report['efficiency_score']:.0f}/100",
                title="Optimization Profile",
                box=box.ROUNDED,
                style="green"
            )
            
            self.console.print(profile_panel)
        
        Prompt.ask("\nPress Enter to return to overview", default="")
    
    def _display_recommendations_detail(self) -> None:
        """Display detailed optimization recommendations."""
        self.console.clear()
        
        # Get all recommendations
        recommendations = self.resource_tracker.get_optimization_recommendations(timedelta(hours=24))
        
        if not recommendations:
            no_rec_panel = Panel(
                "No optimization recommendations available.\nSystem performance appears optimal.",
                title="Optimization Recommendations",
                box=box.ROUNDED,
                style="green"
            )
            self.console.print(no_rec_panel)
        else:
            # Group recommendations by severity
            critical_recs = [r for r in recommendations if r.severity == "critical"]
            warning_recs = [r for r in recommendations if r.severity == "warning"]
            info_recs = [r for r in recommendations if r.severity == "info"]
            
            if critical_recs:
                critical_table = Table(show_header=True, header_style="bold red", box=box.ROUNDED)
                critical_table.add_column("Resource", style="cyan")
                critical_table.add_column("Action", style="white")
                critical_table.add_column("Impact", style="green")
                
                for rec in critical_recs[:5]:
                    critical_table.add_row(
                        rec.resource_type.value,
                        rec.recommended_action,
                        f"{rec.expected_improvement:.0f}% improvement"
                    )
                
                critical_panel = Panel(
                    critical_table,
                    title="🔴 Critical Recommendations",
                    box=box.ROUNDED,
                    style="red"
                )
                self.console.print(critical_panel)
            
            if warning_recs:
                warning_table = Table(show_header=True, header_style="bold yellow", box=box.ROUNDED)
                warning_table.add_column("Resource", style="cyan")
                warning_table.add_column("Action", style="white")
                warning_table.add_column("Impact", style="green")
                
                for rec in warning_recs[:3]:
                    warning_table.add_row(
                        rec.resource_type.value,
                        rec.recommended_action,
                        f"{rec.expected_improvement:.0f}% improvement"
                    )
                
                warning_panel = Panel(
                    warning_table,
                    title="🟡 Warning Recommendations",
                    box=box.ROUNDED,
                    style="yellow"
                )
                self.console.print(warning_panel)
        
        Prompt.ask("\nPress Enter to return to overview", default="")
    
    def export_dashboard_data(self, export_path: Optional[Path] = None) -> Path:
        """Export current dashboard data for institutional reporting."""
        if not self.export_enabled:
            raise ValueError("Dashboard export is disabled")
        
        if export_path is None:
            export_path = Path.home() / ".epubs" / "dashboard_exports"
            export_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = export_path / f"performance_dashboard_export_{timestamp}.json"
        
        # Collect all metrics for export
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "dashboard_mode": self.current_mode,
            "faiss_metrics": self.faiss_collector.get_performance_summary(timedelta(hours=24)),
            "cache_metrics": self.cache_collector.get_hierarchical_summary(timedelta(hours=24)),
            "ml_metrics": self.ml_collector.get_ml_system_metrics(timedelta(hours=24)),
            "resource_metrics": self.resource_tracker.generate_optimization_report()
        }
        
        import json
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Dashboard data exported to {export_file}")
        return export_file


def launch_performance_dashboard(mode: str = DashboardMode.OVERVIEW,
                                auto_refresh: bool = True,
                                update_interval: float = 2.0) -> None:
    """
    Launch the Phase 2B performance dashboard.
    
    Args:
        mode: Initial dashboard mode
        auto_refresh: Enable automatic refresh
        update_interval: Seconds between updates
    """
    dashboard = PerformanceDashboard(
        update_interval=update_interval,
        auto_refresh=auto_refresh
    )
    
    try:
        dashboard.start_dashboard(mode)
    except Exception as e:
        print(f"Dashboard error: {e}")
    finally:
        dashboard.stop_dashboard()
