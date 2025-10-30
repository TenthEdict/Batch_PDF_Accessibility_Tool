#!/usr/bin/env python3
"""
Health Check System for ePubs Accessibility Enhancement Project.

This module provides comprehensive health monitoring capabilities including:
- Basic system health checks
- Detailed health status reporting
- Readiness and liveness probes
- Dependency availability checks
- Performance metrics collection
"""

import logging
import time
import psutil
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class HealthCheckResult:
    """Represents the result of a health check."""
    
    def __init__(self, name: str, status: str, message: str = "", details: Optional[Dict] = None):
        self.name = name
        self.status = status  # "healthy", "unhealthy", "degraded"
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class SystemHealthChecker:
    """Comprehensive system health checker."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.health_history: List[HealthCheckResult] = []
        
    def check_system_resources(self) -> HealthCheckResult:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
            
            # Determine status based on thresholds
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 95:
                status = "unhealthy"
                message = "System resources critically low"
            elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 85:
                status = "degraded"
                message = "System resources elevated"
            else:
                status = "healthy"
                message = "System resources normal"
            
            return HealthCheckResult("system_resources", status, message, details)
            
        except Exception as e:
            self.logger.error(f"System resource check failed: {e}")
            return HealthCheckResult("system_resources", "unhealthy", f"Check failed: {e}")
    
    def check_dependencies(self) -> HealthCheckResult:
        """Check critical dependencies."""
        try:
            missing_deps = []
            available_deps = []
            
            # Check Python packages
            required_packages = ['PyMuPDF', 'pikepdf', 'ocrmypdf', 'PIL', 'typer', 'yaml']
            for package in required_packages:
                try:
                    if package == 'PIL':
                        import PIL
                    else:
                        __import__(package.lower().replace('-', '_'))
                    available_deps.append(package)
                except ImportError:
                    missing_deps.append(package)
            
            # Check system dependencies
            try:
                import subprocess
                result = subprocess.run(['tesseract', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    available_deps.append('tesseract')
                else:
                    missing_deps.append('tesseract')
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing_deps.append('tesseract')
            
            details = {
                "available_dependencies": available_deps,
                "missing_dependencies": missing_deps,
                "total_required": len(required_packages) + 1,  # +1 for tesseract
                "total_available": len(available_deps)
            }
            
            if missing_deps:
                status = "unhealthy"
                message = f"Missing dependencies: {', '.join(missing_deps)}"
            else:
                status = "healthy"
                message = "All dependencies available"
            
            return HealthCheckResult("dependencies", status, message, details)
            
        except Exception as e:
            self.logger.error(f"Dependency check failed: {e}")
            return HealthCheckResult("dependencies", "unhealthy", f"Check failed: {e}")
    
    def check_file_system(self) -> HealthCheckResult:
        """Check file system accessibility and permissions."""
        try:
            required_dirs = ['data/input', 'data/output', 'logs', 'cache']
            accessible_dirs = []
            inaccessible_dirs = []
            
            for dir_path in required_dirs:
                path = Path(dir_path)
                if path.exists() and path.is_dir():
                    # Check if writable
                    test_file = path / '.health_check_test'
                    try:
                        test_file.touch()
                        test_file.unlink()
                        accessible_dirs.append(dir_path)
                    except (PermissionError, OSError):
                        inaccessible_dirs.append(f"{dir_path} (not writable)")
                else:
                    inaccessible_dirs.append(f"{dir_path} (does not exist)")
            
            details = {
                "accessible_directories": accessible_dirs,
                "inaccessible_directories": inaccessible_dirs,
                "total_required": len(required_dirs),
                "total_accessible": len(accessible_dirs)
            }
            
            if inaccessible_dirs:
                status = "unhealthy"
                message = f"Inaccessible directories: {', '.join(inaccessible_dirs)}"
            else:
                status = "healthy"
                message = "All required directories accessible"
            
            return HealthCheckResult("file_system", status, message, details)
            
        except Exception as e:
            self.logger.error(f"File system check failed: {e}")
            return HealthCheckResult("file_system", "unhealthy", f"Check failed: {e}")
    
    def check_processing_capability(self) -> HealthCheckResult:
        """Check if the system can process documents."""
        try:
            # Try to initialize key components
            from ..services.enhancement_service import EnhancementService
            from ..enhancers.ocr_enhancer import OCREnhancer
            
            # Test enhancement service initialization
            enhancement_service = EnhancementService()
            capabilities = enhancement_service.get_available_enhancers()
            
            # Test OCR enhancer
            ocr_enhancer = OCREnhancer()
            ocr_capabilities = ocr_enhancer.get_capabilities()
            
            details = {
                "enhancement_service_available": True,
                "ocr_enhancer_available": True,
                "available_enhancers": capabilities,
                "ocr_capabilities": ocr_capabilities
            }
            
            status = "healthy"
            message = "Processing components available"
            
            return HealthCheckResult("processing_capability", status, message, details)
            
        except Exception as e:
            self.logger.error(f"Processing capability check failed: {e}")
            return HealthCheckResult("processing_capability", "unhealthy", f"Check failed: {e}")
    
    def check_performance_metrics(self) -> HealthCheckResult:
        """Check performance metrics and thresholds."""
        try:
            # Get system performance data
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Get process-specific metrics
            current_process = psutil.Process()
            process_memory = current_process.memory_info()
            
            details = {
                "system_cpu_percent": cpu_percent,
                "system_memory_percent": memory.percent,
                "process_memory_mb": round(process_memory.rss / (1024**2), 2),
                "process_cpu_percent": current_process.cpu_percent(),
                "process_threads": current_process.num_threads(),
                "process_open_files": len(current_process.open_files()),
                "process_connections": len(current_process.connections())
            }
            
            # Performance thresholds
            if cpu_percent > 80 or memory.percent > 80:
                status = "degraded"
                message = "Performance metrics elevated"
            else:
                status = "healthy"
                message = "Performance metrics normal"
            
            return HealthCheckResult("performance_metrics", status, message, details)
            
        except Exception as e:
            self.logger.error(f"Performance metrics check failed: {e}")
            return HealthCheckResult("performance_metrics", "unhealthy", f"Check failed: {e}")
    
    def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status."""
        checks = [
            self.check_system_resources(),
            self.check_dependencies(),
            self.check_file_system(),
            self.check_processing_capability(),
            self.check_performance_metrics()
        ]
        
        # Store in history
        self.health_history.extend(checks)
        
        # Determine overall status
        unhealthy_count = sum(1 for check in checks if check.status == "unhealthy")
        degraded_count = sum(1 for check in checks if check.status == "degraded")
        
        if unhealthy_count > 0:
            overall_status = "unhealthy"
        elif degraded_count > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Calculate success rate
        total_checks = len(checks)
        healthy_checks = sum(1 for check in checks if check.status == "healthy")
        success_rate = (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
        
        return {
            "status": overall_status,
            "success_rate": round(success_rate, 2),
            "timestamp": datetime.now().isoformat(),
            "checks": [check.to_dict() for check in checks],
            "summary": {
                "total_checks": total_checks,
                "healthy": healthy_checks,
                "degraded": degraded_count,
                "unhealthy": unhealthy_count
            }
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of recent health checks."""
        if not self.health_history:
            return {"status": "unknown", "message": "No health checks performed"}
        
        recent_checks = self.health_history[-10:]  # Last 10 checks
        overall_statuses = [check.status for check in recent_checks]
        
        if "unhealthy" in overall_statuses:
            overall_status = "unhealthy"
        elif "degraded" in overall_statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "last_check": recent_checks[-1].timestamp if recent_checks else None,
            "checks_performed": len(self.health_history),
            "recent_statuses": overall_statuses[-5:]  # Last 5 statuses
        }


# Global health checker instance
_health_checker = None

def get_health_checker() -> SystemHealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = SystemHealthChecker()
    return _health_checker


def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    checker = get_health_checker()
    return checker.run_comprehensive_health_check()


def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with full information."""
    checker = get_health_checker()
    return checker.run_comprehensive_health_check()


def readiness_probe() -> Dict[str, Any]:
    """Readiness probe for Kubernetes/container orchestration."""
    checker = get_health_checker()
    result = checker.run_comprehensive_health_check()
    
    # For readiness, we only care if the system is ready to accept requests
    is_ready = result["status"] in ["healthy", "degraded"]
    
    return {
        "ready": is_ready,
        "status": result["status"],
        "timestamp": result["timestamp"]
    }


def liveness_probe() -> Dict[str, Any]:
    """Liveness probe for Kubernetes/container orchestration."""
    checker = get_health_checker()
    result = checker.run_comprehensive_health_check()
    
    # For liveness, we only care if the system is alive (not unhealthy)
    is_alive = result["status"] != "unhealthy"
    
    return {
        "alive": is_alive,
        "status": result["status"],
        "timestamp": result["timestamp"]
    }


def get_health_status() -> Dict[str, Any]:
    """Get current health status summary."""
    checker = get_health_checker()
    return checker.get_health_summary()


if __name__ == "__main__":
    # CLI interface for health checks
    import argparse
    
    parser = argparse.ArgumentParser(description="ePubs Health Check System")
    parser.add_argument("--type", choices=["basic", "detailed", "readiness", "liveness"], 
                       default="basic", help="Type of health check to perform")
    parser.add_argument("--format", choices=["json", "text"], default="json", 
                       help="Output format")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Perform health check
    if args.type == "basic":
        result = health_check()
    elif args.type == "detailed":
        result = detailed_health_check()
    elif args.type == "readiness":
        result = readiness_probe()
    elif args.type == "liveness":
        result = liveness_probe()
    
    # Output result
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Status: {result.get('status', 'unknown')}")
        if 'summary' in result:
            summary = result['summary']
            print(f"Total Checks: {summary['total_checks']}")
            print(f"Healthy: {summary['healthy']}")
            print(f"Degraded: {summary['degraded']}")
            print(f"Unhealthy: {summary['unhealthy']}")
        print(f"Success Rate: {result.get('success_rate', 0)}%")
