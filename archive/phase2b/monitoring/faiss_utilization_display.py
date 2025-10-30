"""
FAISS Vector Database Utilization Visualization
=============================================

Specialized visualization module for FAISS vector database performance analytics.
Provides institutional-grade insights into vector database operations, similarity search
performance, index utilization, and optimization recommendations for Phase 2B deployment.

Features:
- Real-time FAISS operation monitoring with Rich CLI visualization
- Vector similarity search performance analytics
- Index type utilization and optimization insights
- Memory usage patterns for vector operations
- Academic document processing optimization recommendations
- Integration with Phase 2B performance dashboard framework
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict

# Rich UI components for FAISS visualization
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.text import Text
from rich.tree import Tree
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich.live import Live
from rich import box
from rich.layout import Layout

# Import FAISS metrics components
from .faiss_metrics_collector import (
    get_faiss_metrics_collector, 
    FAISSPerformanceSummary, 
    FAISSOperationMetric
)


class FAISSVisualizationMode:
    """FAISS visualization display modes."""
    OVERVIEW = "overview"
    OPERATIONS_DETAIL = "operations_detail"
    PERFORMANCE_TRENDS = "performance_trends"
    INDEX_ANALYSIS = "index_analysis"
    OPTIMIZATION_INSIGHTS = "optimization_insights"


class FAISSUtilizationDisplay:
    """
    Comprehensive FAISS vector database utilization visualization system.
    
    Provides institutional-grade analytics visualization for FAISS vector database
    operations with detailed performance insights, optimization recommendations,
    and real-time monitoring capabilities for Phase 2B academic document processing.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize FAISS utilization display.
        
        Args:
            console: Rich console instance for display output
        """
        self.console = console or Console()
        self.faiss_collector = get_faiss_metrics_collector()
        
        # Display configuration
        self.current_mode = FAISSVisualizationMode.OVERVIEW
        self.time_window = timedelta(hours=1)
        
        # Performance thresholds for visualization
        self.performance_thresholds = {
            "excellent_time_ms": 100,
            "good_time_ms": 500,
            "warning_time_ms": 1000,
            "critical_time_ms": 2000
        }
        
        # Index type display preferences
        self.index_type_colors = {
            "Flat": "green",
            "IVF": "blue", 
            "HNSW": "magenta",
            "Unknown": "dim"
        }
    
    def create_faiss_overview_panel(self) -> Panel:
        """Create comprehensive FAISS overview panel for dashboard integration."""
        # Get performance summary
        summary = self.faiss_collector.get_performance_summary(self.time_window)
        
        # Create main overview layout
        overview_layout = Layout(name="faiss_overview")
        overview_layout.split_row(
            Layout(name="metrics", ratio=2),
            Layout(name="status", ratio=1)
        )
        
        # Metrics section
        metrics_table = self._create_metrics_summary_table(summary)
        overview_layout["metrics"].update(metrics_table)
        
        # Status section
        status_panel = self._create_status_indicator_panel(summary)
        overview_layout["status"].update(status_panel)
        
        return Panel(
            overview_layout,
            title="FAISS Vector Database Performance",
            box=box.ROUNDED,
            style="blue"
        )
    
    def create_faiss_detailed_analysis(self) -> Layout:
        """Create detailed FAISS analysis layout with multiple views."""
        main_layout = Layout(name="faiss_detail")
        
        # Split into sections
        main_layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=8)
        )
        
        # Header with title and time window
        header_content = Panel(
            Align.center(
                Text("FAISS Vector Database Detailed Analysis", style="bold blue") +
                Text(f" | Time Window: {self._format_time_window()}", style="dim")
            ),
            box=box.ROUNDED,
            style="blue"
        )
        main_layout["header"].update(header_content)
        
        # Body split into main analysis areas
        main_layout["body"].split_row(
            Layout(name="operations", ratio=1),
            Layout(name="performance", ratio=1),
            Layout(name="optimization", ratio=1)
        )
        
        # Operations analysis
        operations_panel = self._create_operations_analysis_panel()
        main_layout["body"]["operations"].update(operations_panel)
        
        # Performance trends
        performance_panel = self._create_performance_trends_panel()
        main_layout["body"]["performance"].update(performance_panel)
        
        # Optimization insights
        optimization_panel = self._create_optimization_insights_panel()
        main_layout["body"]["optimization"].update(optimization_panel)
        
        # Footer with recommendations
        recommendations_panel = self._create_recommendations_panel()
        main_layout["footer"].update(recommendations_panel)
        
        return main_layout
    
    def _create_metrics_summary_table(self, summary: FAISSPerformanceSummary) -> Table:
        """Create metrics summary table for overview display."""
        table = Table(show_header=True, header_style="bold blue", box=box.SIMPLE)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="white", width=15)
        table.add_column("Status", width=10)
        
        # Total operations with status indicator
        ops_status = "🟢" if summary.total_operations > 0 else "🟡"
        table.add_row("Total Operations", str(summary.total_operations), ops_status)
        
        # Success rate with color coding
        success_rate = (summary.successful_operations / max(summary.total_operations, 1)) * 100
        success_status = "🟢" if success_rate > 95 else "🟡" if success_rate > 85 else "🔴"
        table.add_row("Success Rate", f"{success_rate:.1f}%", success_status)
        
        # Average operation time with performance indicator
        avg_time = summary.average_operation_time_ms
        time_status = self._get_performance_status_indicator(avg_time)
        table.add_row("Avg Operation Time", f"{avg_time:.2f}ms", time_status)
        
        # Vector processing rate
        vector_rate = summary.average_vectors_per_second
        rate_status = "🟢" if vector_rate > 100 else "🟡" if vector_rate > 10 else "🔴"
        table.add_row("Processing Rate", f"{vector_rate:.1f} vec/sec", rate_status)
        
        # Memory efficiency
        memory_eff = summary.memory_efficiency_score
        memory_status = "🟢" if memory_eff > 70 else "🟡" if memory_eff > 50 else "🔴"
        table.add_row("Memory Efficiency", f"{memory_eff:.1f}/100", memory_status)
        
        # Error rate
        error_rate = summary.error_rate_percent
        error_status = "🟢" if error_rate < 1 else "🟡" if error_rate < 5 else "🔴"
        table.add_row("Error Rate", f"{error_rate:.1f}%", error_status)
        
        return table
    
    def _create_status_indicator_panel(self, summary: FAISSPerformanceSummary) -> Panel:
        """Create status indicator panel with overall health assessment."""
        status_text = Text()
        
        # Overall status assessment
        overall_score = self._calculate_overall_performance_score(summary)
        
        if overall_score >= 85:
            status_text.append("🟢 EXCELLENT\n", style="bold green")
            status_text.append("FAISS performance optimal\n")
        elif overall_score >= 70:
            status_text.append("🟡 GOOD\n", style="bold yellow")
            status_text.append("FAISS performance acceptable\n")
        elif overall_score >= 50:
            status_text.append("🟠 FAIR\n", style="bold orange")
            status_text.append("FAISS needs optimization\n")
        else:
            status_text.append("🔴 POOR\n", style="bold red")
            status_text.append("FAISS requires attention\n")
        
        status_text.append(f"\nPerformance Score: {overall_score:.0f}/100\n", style="bold")
        
        # Key indicators
        status_text.append("\nKey Indicators:\n", style="bold cyan")
        
        # Index type distribution
        if summary.index_type_distribution:
            dominant_index = max(summary.index_type_distribution.items(), key=lambda x: x[1])
            status_text.append(f"• Index Type: {dominant_index[0]}\n")
        
        # Processing efficiency
        if summary.total_operations > 0:
            efficiency = (summary.successful_operations / summary.total_operations) * 100
            status_text.append(f"• Efficiency: {efficiency:.1f}%\n")
        
        # Recent activity
        if summary.total_operations > 0:
            status_text.append("• Activity: Active\n", style="green")
        else:
            status_text.append("• Activity: Idle\n", style="yellow")
        
        return Panel(
            status_text,
            title="FAISS Status",
            box=box.ROUNDED,
            style="cyan"
        )
    
    def _create_operations_analysis_panel(self) -> Panel:
        """Create operations analysis panel with operation type breakdown."""
        summary = self.faiss_collector.get_performance_summary(self.time_window)
        
        ops_table = Table(show_header=True, header_style="bold green", box=box.ROUNDED)
        ops_table.add_column("Operation Type", style="cyan")
        ops_table.add_column("Count", style="white")
        ops_table.add_column("Percentage", style="yellow")
        ops_table.add_column("Avg Time", style="blue")
        
        total_ops = summary.total_operations
        
        if total_ops > 0 and summary.operation_type_distribution:
            for op_type, count in summary.operation_type_distribution.items():
                percentage = (count / total_ops) * 100
                # Note: We don't have per-operation-type timing in the summary
                # This would need to be enhanced in the metrics collector
                avg_time = "N/A"  # Placeholder for per-type timing
                
                ops_table.add_row(
                    op_type.title(),
                    str(count),
                    f"{percentage:.1f}%",
                    avg_time
                )
        else:
            ops_table.add_row("No operations", "0", "0%", "N/A")
        
        return Panel(
            ops_table,
            title="Operations Analysis",
            box=box.ROUNDED,
            style="green"
        )
    
    def _create_performance_trends_panel(self) -> Panel:
        """Create performance trends panel with timing analysis."""
        summary = self.faiss_collector.get_performance_summary(self.time_window)
        
        trends_text = Text()
        trends_text.append("Performance Trends\n", style="bold magenta")
        
        # Timing statistics
        if summary.total_operations > 0:
            trends_text.append(f"Fastest Operation: {summary.fastest_operation_ms:.2f}ms\n")
            trends_text.append(f"Average Operation: {summary.average_operation_time_ms:.2f}ms\n")
            trends_text.append(f"Slowest Operation: {summary.slowest_operation_ms:.2f}ms\n")
            
            # Performance variance analysis
            time_variance = summary.slowest_operation_ms - summary.fastest_operation_ms
            trends_text.append(f"Time Variance: {time_variance:.2f}ms\n\n")
            
            # Performance consistency assessment
            consistency_ratio = summary.fastest_operation_ms / max(summary.average_operation_time_ms, 1)
            if consistency_ratio > 0.8:
                trends_text.append("✅ Consistent Performance\n", style="green")
            elif consistency_ratio > 0.5:
                trends_text.append("⚠️ Moderate Variance\n", style="yellow")
            else:
                trends_text.append("🔴 High Variance\n", style="red")
            
            # Vector processing efficiency
            vector_efficiency = summary.average_vectors_per_second
            if vector_efficiency > 1000:
                trends_text.append("🚀 Excellent Throughput\n", style="green")
            elif vector_efficiency > 100:
                trends_text.append("✅ Good Throughput\n", style="green")
            elif vector_efficiency > 10:
                trends_text.append("⚠️ Moderate Throughput\n", style="yellow")
            else:
                trends_text.append("🔴 Low Throughput\n", style="red")
        else:
            trends_text.append("No performance data available\n", style="dim")
            trends_text.append("Start FAISS operations to see trends\n", style="dim")
        
        return Panel(
            trends_text,
            title="Performance Trends",
            box=box.ROUNDED,
            style="magenta"
        )
    
    def _create_optimization_insights_panel(self) -> Panel:
        """Create optimization insights panel with actionable recommendations."""
        summary = self.faiss_collector.get_performance_summary(self.time_window)
        
        insights_text = Text()
        insights_text.append("Optimization Insights\n", style="bold yellow")
        
        # Index type analysis
        if summary.index_type_distribution:
            insights_text.append("\nIndex Type Usage:\n", style="bold cyan")
            
            for index_type, count in summary.index_type_distribution.items():
                percentage = (count / max(summary.total_operations, 1)) * 100
                color = self.index_type_colors.get(index_type, "white")
                insights_text.append(f"• {index_type}: {count} ops ({percentage:.1f}%)\n", style=color)
            
            # Index optimization recommendations
            dominant_index = max(summary.index_type_distribution.items(), key=lambda x: x[1])[0]
            
            if dominant_index == "Flat" and summary.total_operations > 100:
                insights_text.append("\n💡 Consider IVF or HNSW for better performance\n", style="yellow")
            elif summary.average_operation_time_ms > 1000:
                insights_text.append("\n💡 Operations are slow - optimize index configuration\n", style="yellow")
        
        # Memory efficiency insights
        if summary.memory_efficiency_score < 50:
            insights_text.append("\n🔧 Memory usage is high - consider compression\n", style="yellow")
        elif summary.memory_efficiency_score > 80:
            insights_text.append("\n✅ Excellent memory efficiency\n", style="green")
        
        # Error rate insights
        if summary.error_rate_percent > 5:
            insights_text.append("\n⚠️ High error rate detected - check configuration\n", style="red")
        elif summary.error_rate_percent == 0:
            insights_text.append("\n✅ No errors detected\n", style="green")
        
        return Panel(
            insights_text,
            title="Optimization Insights",
            box=box.ROUNDED,
            style="yellow"
        )
    
    def _create_recommendations_panel(self) -> Panel:
        """Create detailed recommendations panel with actionable suggestions."""
        summary = self.faiss_collector.get_performance_summary(self.time_window)
        
        # Create recommendations table
        rec_table = Table(show_header=True, header_style="bold yellow", box=box.ROUNDED)
        rec_table.add_column("Priority", style="red", width=8)
        rec_table.add_column("Recommendation", style="white", width=50)
        rec_table.add_column("Expected Impact", style="green", width=15)
        
        if summary.recommendations:
            for i, rec in enumerate(summary.recommendations[:5], 1):
                # Determine priority based on recommendation content
                if "critical" in rec.lower() or "error" in rec.lower():
                    priority = "HIGH"
                    priority_style = "red"
                elif "slow" in rec.lower() or "optimize" in rec.lower():
                    priority = "MEDIUM"
                    priority_style = "yellow"
                else:
                    priority = "LOW"
                    priority_style = "green"
                
                # Estimate impact based on recommendation type
                if "index" in rec.lower():
                    impact = "10-50% speedup"
                elif "memory" in rec.lower():
                    impact = "20-40% less RAM"
                elif "configuration" in rec.lower():
                    impact = "5-25% improvement"
                else:
                    impact = "Variable"
                
                rec_table.add_row(
                    Text(priority, style=priority_style),
                    rec,
                    impact
                )
        else:
            rec_table.add_row(
                Text("INFO", style="green"),
                "No specific recommendations - FAISS performance appears optimal",
                "Maintain current"
            )
        
        return Panel(
            rec_table,
            title="FAISS Optimization Recommendations",
            box=box.ROUNDED,
            style="yellow"
        )
    
    def create_index_utilization_analysis(self) -> Panel:
        """Create detailed index utilization analysis panel."""
        summary = self.faiss_collector.get_performance_summary(self.time_window)
        
        # Create index analysis layout
        index_layout = Layout(name="index_analysis")
        index_layout.split_row(
            Layout(name="distribution", ratio=1),
            Layout(name="performance", ratio=1)
        )
        
        # Index type distribution
        if summary.index_type_distribution:
            dist_table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
            dist_table.add_column("Index Type", style="cyan")
            dist_table.add_column("Operations", style="white")
            dist_table.add_column("Percentage", style="yellow")
            dist_table.add_column("Recommendation", style="green")
            
            total_ops = summary.total_operations
            
            for index_type, count in summary.index_type_distribution.items():
                percentage = (count / max(total_ops, 1)) * 100
                
                # Generate recommendations based on index type usage
                if index_type == "Flat" and percentage > 80:
                    recommendation = "Consider IVF/HNSW"
                elif index_type == "IVF" and summary.average_operation_time_ms > 500:
                    recommendation = "Optimize parameters"
                elif index_type == "HNSW":
                    recommendation = "Good choice"
                else:
                    recommendation = "Monitor performance"
                
                dist_table.add_row(
                    index_type,
                    str(count),
                    f"{percentage:.1f}%",
                    recommendation
                )
            
            index_layout["distribution"].update(Panel(
                dist_table,
                title="Index Type Distribution",
                box=box.ROUNDED,
                style="blue"
            ))
        else:
            index_layout["distribution"].update(Panel(
                "No index usage data available",
                title="Index Type Distribution",
                box=box.ROUNDED,
                style="dim"
            ))
        
        # Performance by index type (placeholder - would need enhanced metrics)
        perf_text = Text()
        perf_text.append("Index Performance Analysis\n", style="bold magenta")
        perf_text.append("(Detailed per-index metrics)\n\n", style="dim")
        
        if summary.index_type_distribution:
            perf_text.append("Performance by Index Type:\n", style="cyan")
            for index_type in summary.index_type_distribution.keys():
                # This would require enhanced metrics collection
                perf_text.append(f"• {index_type}: Analysis pending\n")
        else:
            perf_text.append("No performance data available\n", style="dim")
        
        index_layout["performance"].update(Panel(
            perf_text,
            title="Performance Analysis",
            box=box.ROUNDED,
            style="magenta"
        ))
        
        return Panel(
            index_layout,
            title="FAISS Index Utilization Analysis",
            box=box.ROUNDED,
            style="blue"
        )
    
    def _get_performance_status_indicator(self, time_ms: float) -> str:
        """Get performance status indicator based on operation time."""
        if time_ms <= self.performance_thresholds["excellent_time_ms"]:
            return "🟢"
        elif time_ms <= self.performance_thresholds["good_time_ms"]:
            return "🟡"
        elif time_ms <= self.performance_thresholds["warning_time_ms"]:
            return "🟠"
        else:
            return "🔴"
    
    def _calculate_overall_performance_score(self, summary: FAISSPerformanceSummary) -> float:
        """Calculate overall FAISS performance score (0-100)."""
        if summary.total_operations == 0:
            return 0.0
        
        # Success rate component (0-30 points)
        success_rate = (summary.successful_operations / summary.total_operations) * 100
        success_score = min(30, success_rate * 0.3)
        
        # Speed component (0-40 points)
        # Excellent: <100ms, Good: <500ms, Fair: <1000ms, Poor: >1000ms
        avg_time = summary.average_operation_time_ms
        if avg_time <= 100:
            speed_score = 40
        elif avg_time <= 500:
            speed_score = 30
        elif avg_time <= 1000:
            speed_score = 20
        else:
            speed_score = max(0, 20 - (avg_time - 1000) / 100)
        
        # Memory efficiency component (0-20 points)
        memory_score = summary.memory_efficiency_score * 0.2
        
        # Error rate component (0-10 points)
        error_score = max(0, 10 - summary.error_rate_percent)
        
        return min(100, success_score + speed_score + memory_score + error_score)
    
    def _format_time_window(self) -> str:
        """Format time window for display."""
        if self.time_window.total_seconds() < 3600:
            minutes = int(self.time_window.total_seconds() / 60)
            return f"Last {minutes} minutes"
        elif self.time_window.total_seconds() < 86400:
            hours = int(self.time_window.total_seconds() / 3600)
            return f"Last {hours} hours"
        else:
            days = int(self.time_window.total_seconds() / 86400)
            return f"Last {days} days"
    
    def set_time_window(self, hours: int) -> None:
        """Set analysis time window."""
        self.time_window = timedelta(hours=hours)
    
    def export_faiss_analytics(self, export_path: Optional[str] = None) -> Dict[str, Any]:
        """Export FAISS analytics data for institutional reporting."""
        summary = self.faiss_collector.get_performance_summary(self.time_window)
        
        analytics_data = {
            "export_timestamp": datetime.now().isoformat(),
            "time_window_hours": self.time_window.total_seconds() / 3600,
            "performance_summary": asdict(summary),
            "overall_performance_score": self._calculate_overall_performance_score(summary),
            "status_assessment": self._get_status_assessment(summary),
            "optimization_recommendations": summary.recommendations
        }
        
        if export_path:
            import json
            with open(export_path, 'w') as f:
                json.dump(analytics_data, f, indent=2, default=str)
        
        return analytics_data
    
    def _get_status_assessment(self, summary: FAISSPerformanceSummary) -> Dict[str, str]:
        """Get comprehensive status assessment."""
        overall_score = self._calculate_overall_performance_score(summary)
        
        if overall_score >= 85:
            status = "excellent"
            description = "FAISS performance is optimal for institutional deployment"
        elif overall_score >= 70:
            status = "good"
            description = "FAISS performance is acceptable with minor optimization opportunities"
        elif overall_score >= 50:
            status = "fair"
            description = "FAISS performance needs optimization for production use"
        else:
            status = "poor"
            description = "FAISS performance requires immediate attention"
        
        return {
            "status": status,
            "score": overall_score,
            "description": description
        }


def create_faiss_dashboard_component(console: Console, time_window_hours: int = 1) -> FAISSUtilizationDisplay:
    """
    Create FAISS dashboard component for integration with main performance dashboard.
    
    Args:
        console: Rich console instance
        time_window_hours: Analysis time window in hours
        
    Returns:
        Configured FAISS utilization display instance
    """
    display = FAISSUtilizationDisplay(console)
    display.set_time_window(time_window_hours)
    return display
