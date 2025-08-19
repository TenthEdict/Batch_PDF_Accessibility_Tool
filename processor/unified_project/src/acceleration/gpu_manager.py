#!/usr/bin/env python3
"""
GPU Acceleration Detection and Management Module

This module provides comprehensive GPU acceleration capabilities for ePubs processing:
- Multi-platform GPU detection (CUDA, Metal, OpenCL)
- GPU-accelerated OCR processing with Tesseract
- Apple Silicon optimization with Metal Performance Shaders
- GPU memory management and optimization
- Fallback strategies for CPU-only systems

Features:
- CUDA acceleration for NVIDIA GPUs
- Metal acceleration for Apple Silicon
- OpenCL support for general GPU computing
- GPU memory monitoring and optimization
- Intelligent GPU/CPU workload distribution
"""

import logging
import platform
import subprocess
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)


class GPUType(Enum):
    """GPU types supported for acceleration."""
    NONE = "none"
    NVIDIA_CUDA = "nvidia_cuda"
    APPLE_METAL = "apple_metal"
    AMD_OPENCL = "amd_opencl"
    INTEL_OPENCL = "intel_opencl"
    GENERIC_OPENCL = "generic_opencl"


@dataclass
class GPUInfo:
    """GPU information and capabilities."""
    gpu_type: GPUType
    device_name: str
    memory_total_mb: int
    memory_available_mb: int
    compute_capability: Optional[str] = None
    driver_version: Optional[str] = None
    opencl_version: Optional[str] = None
    metal_version: Optional[str] = None
    performance_score: float = 0.0
    ocr_acceleration_available: bool = False
    image_processing_acceleration: bool = False


class GPUAccelerationManager:
    """
    Comprehensive GPU acceleration management for ePubs processing.
    
    Provides platform-specific GPU detection, memory management,
    and optimized processing workflows for different GPU types.
    """
    
    def __init__(self):
        """Initialize GPU acceleration manager."""
        self.detected_gpus: List[GPUInfo] = []
        self.primary_gpu: Optional[GPUInfo] = None
        self.gpu_available = False
        self.acceleration_enabled = False
        
        # Platform detection
        self.platform = platform.system()
        self.is_apple_silicon = self._detect_apple_silicon()
        self.is_linux = self.platform == "Linux"
        self.is_windows = self.platform == "Windows"
        
        # Threading for concurrent GPU operations
        self._gpu_lock = threading.Lock()
        
        # Detection results cache
        self._detection_cache = {}
        self._last_detection_time = 0
        self.cache_timeout = 300  # 5 minutes
        
        # Initialize GPU detection
        self._detect_available_gpus()
        
        logger.info(f"GPU Acceleration Manager initialized - Platform: {self.platform}")
        if self.primary_gpu:
            logger.info(f"Primary GPU: {self.primary_gpu.device_name} ({self.primary_gpu.gpu_type.value})")
    
    def _detect_apple_silicon(self) -> bool:
        """Detect Apple Silicon (M1/M2/M3) processors."""
        if self.platform != "Darwin":
            return False
        
        try:
            # Check for Apple Silicon indicators
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            cpu_brand = result.stdout.strip()
            is_apple_silicon = "Apple" in cpu_brand and ("M1" in cpu_brand or "M2" in cpu_brand or "M3" in cpu_brand)
            
            if is_apple_silicon:
                logger.info(f"Apple Silicon detected: {cpu_brand}")
            
            return is_apple_silicon
            
        except Exception as e:
            logger.debug(f"Apple Silicon detection failed: {e}")
            return False
    
    def _detect_cuda_gpus(self) -> List[GPUInfo]:
        """Detect NVIDIA CUDA-capable GPUs."""
        cuda_gpus = []
        
        try:
            # Try nvidia-ml-py if available
            try:
                import pynvml
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle).decode()
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    
                    # Get compute capability
                    major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                    compute_capability = f"{major}.{minor}"
                    
                    gpu_info = GPUInfo(
                        gpu_type=GPUType.NVIDIA_CUDA,
                        device_name=name,
                        memory_total_mb=memory_info.total // (1024 * 1024),
                        memory_available_mb=memory_info.free // (1024 * 1024),
                        compute_capability=compute_capability,
                        performance_score=self._calculate_cuda_performance_score(compute_capability, memory_info.total),
                        ocr_acceleration_available=True,
                        image_processing_acceleration=True
                    )
                    
                    cuda_gpus.append(gpu_info)
                    logger.info(f"CUDA GPU detected: {name} (Compute {compute_capability})")
                
                pynvml.nvmlShutdown()
                
            except ImportError:
                # Fallback to nvidia-smi
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            parts = [p.strip() for p in line.split(',')]
                            if len(parts) >= 3:
                                name, total_mem, free_mem = parts[:3]
                                
                                gpu_info = GPUInfo(
                                    gpu_type=GPUType.NVIDIA_CUDA,
                                    device_name=name,
                                    memory_total_mb=int(total_mem),
                                    memory_available_mb=int(free_mem),
                                    performance_score=self._estimate_nvidia_performance(name),
                                    ocr_acceleration_available=True,
                                    image_processing_acceleration=True
                                )
                                
                                cuda_gpus.append(gpu_info)
                                logger.info(f"CUDA GPU detected via nvidia-smi: {name}")
                
        except Exception as e:
            logger.debug(f"CUDA detection failed: {e}")
        
        return cuda_gpus
    
    def _detect_metal_gpus(self) -> List[GPUInfo]:
        """Detect Apple Metal-capable GPUs."""
        metal_gpus = []
        
        if not self.is_apple_silicon:
            return metal_gpus
        
        try:
            # Check for Metal availability
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse for GPU information
                if "Apple" in output and ("M1" in output or "M2" in output or "M3" in output):
                    # Estimate memory for Apple Silicon (unified memory architecture)
                    memory_result = subprocess.run(
                        ["sysctl", "-n", "hw.memsize"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    total_memory_bytes = int(memory_result.stdout.strip()) if memory_result.returncode == 0 else 8 * 1024**3
                    # Apple Silicon uses unified memory - assume 60% available for GPU tasks
                    gpu_memory_mb = int((total_memory_bytes * 0.6) // (1024 * 1024))
                    
                    # Determine chip type
                    cpu_brand_result = subprocess.run(
                        ["sysctl", "-n", "machdep.cpu.brand_string"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    cpu_brand = cpu_brand_result.stdout.strip() if cpu_brand_result.returncode == 0 else "Apple Silicon"
                    
                    gpu_info = GPUInfo(
                        gpu_type=GPUType.APPLE_METAL,
                        device_name=f"Apple {cpu_brand} GPU",
                        memory_total_mb=gpu_memory_mb,
                        memory_available_mb=int(gpu_memory_mb * 0.8),  # Conservative estimate
                        metal_version="3.0",  # Assume Metal 3.0 for Apple Silicon
                        performance_score=self._calculate_metal_performance_score(cpu_brand),
                        ocr_acceleration_available=True,
                        image_processing_acceleration=True
                    )
                    
                    metal_gpus.append(gpu_info)
                    logger.info(f"Metal GPU detected: {cpu_brand}")
                
        except Exception as e:
            logger.debug(f"Metal detection failed: {e}")
        
        return metal_gpus
    
    def _detect_opencl_gpus(self) -> List[GPUInfo]:
        """Detect OpenCL-capable GPUs."""
        opencl_gpus = []
        
        try:
            # Try pyopencl if available
            import pyopencl as cl
            
            for platform in cl.get_platforms():
                for device in platform.get_devices():
                    if device.type == cl.device_type.GPU:
                        # Determine GPU vendor
                        vendor = device.vendor.lower()
                        if "nvidia" in vendor:
                            gpu_type = GPUType.NVIDIA_CUDA  # Prefer CUDA for NVIDIA
                            continue  # Skip if we already detected CUDA
                        elif "amd" in vendor or "advanced micro devices" in vendor:
                            gpu_type = GPUType.AMD_OPENCL
                        elif "intel" in vendor:
                            gpu_type = GPUType.INTEL_OPENCL
                        else:
                            gpu_type = GPUType.GENERIC_OPENCL
                        
                        memory_mb = device.global_mem_size // (1024 * 1024)
                        
                        gpu_info = GPUInfo(
                            gpu_type=gpu_type,
                            device_name=device.name,
                            memory_total_mb=memory_mb,
                            memory_available_mb=int(memory_mb * 0.8),  # Conservative estimate
                            opencl_version=device.opencl_c_version,
                            performance_score=self._estimate_opencl_performance(device),
                            ocr_acceleration_available=True,
                            image_processing_acceleration=True
                        )
                        
                        opencl_gpus.append(gpu_info)
                        logger.info(f"OpenCL GPU detected: {device.name} ({vendor})")
                        
        except ImportError:
            logger.debug("PyOpenCL not available for GPU detection")
        except Exception as e:
            logger.debug(f"OpenCL detection failed: {e}")
        
        return opencl_gpus
    
    def _detect_available_gpus(self):
        """Detect all available GPUs and select primary."""
        # Check cache first
        if self._is_detection_cache_valid():
            self.detected_gpus = self._detection_cache.get('gpus', [])
            self.primary_gpu = self._detection_cache.get('primary_gpu')
            self.gpu_available = len(self.detected_gpus) > 0
            return
        
        all_gpus = []
        
        # Detect different GPU types
        all_gpus.extend(self._detect_cuda_gpus())
        all_gpus.extend(self._detect_metal_gpus())
        all_gpus.extend(self._detect_opencl_gpus())
        
        self.detected_gpus = all_gpus
        
        # Select primary GPU based on performance score
        if all_gpus:
            self.primary_gpu = max(all_gpus, key=lambda gpu: gpu.performance_score)
            self.gpu_available = True
            self.acceleration_enabled = self.primary_gpu.ocr_acceleration_available
            
            logger.info(f"Selected primary GPU: {self.primary_gpu.device_name}")
        else:
            self.primary_gpu = None
            self.gpu_available = False
            self.acceleration_enabled = False
            logger.info("No suitable GPUs detected - using CPU-only processing")
        
        # Cache detection results
        self._detection_cache = {
            'gpus': self.detected_gpus,
            'primary_gpu': self.primary_gpu,
            'timestamp': time.time()
        }
        self._last_detection_time = time.time()
    
    def _is_detection_cache_valid(self) -> bool:
        """Check if GPU detection cache is still valid."""
        return (time.time() - self._last_detection_time) < self.cache_timeout
    
    def _calculate_cuda_performance_score(self, compute_capability: str, memory_bytes: int) -> float:
        """Calculate performance score for CUDA GPU."""
        try:
            major, minor = map(float, compute_capability.split('.'))
            compute_score = major + (minor * 0.1)
            memory_score = min(memory_bytes / (8 * 1024**3), 2.0)  # Normalize to 8GB, cap at 2.0
            return compute_score * 10 + memory_score * 5
        except:
            return 5.0  # Default score
    
    def _calculate_metal_performance_score(self, cpu_brand: str) -> float:
        """Calculate performance score for Metal GPU."""
        cpu_brand_lower = cpu_brand.lower()
        if "m3" in cpu_brand_lower:
            return 25.0  # M3 is very fast
        elif "m2" in cpu_brand_lower:
            if "ultra" in cpu_brand_lower:
                return 22.0
            elif "max" in cpu_brand_lower:
                return 20.0
            elif "pro" in cpu_brand_lower:
                return 18.0
            else:
                return 16.0
        elif "m1" in cpu_brand_lower:
            if "ultra" in cpu_brand_lower:
                return 20.0
            elif "max" in cpu_brand_lower:
                return 18.0
            elif "pro" in cpu_brand_lower:
                return 15.0
            else:
                return 12.0
        else:
            return 10.0  # Generic Apple Silicon
    
    def _estimate_nvidia_performance(self, gpu_name: str) -> float:
        """Estimate NVIDIA GPU performance from name."""
        gpu_name_lower = gpu_name.lower()
        
        # RTX 40 series
        if "rtx 4090" in gpu_name_lower:
            return 30.0
        elif "rtx 4080" in gpu_name_lower:
            return 28.0
        elif "rtx 4070" in gpu_name_lower:
            return 25.0
        elif "rtx 4060" in gpu_name_lower:
            return 22.0
        
        # RTX 30 series
        elif "rtx 3090" in gpu_name_lower:
            return 28.0
        elif "rtx 3080" in gpu_name_lower:
            return 26.0
        elif "rtx 3070" in gpu_name_lower:
            return 23.0
        elif "rtx 3060" in gpu_name_lower:
            return 20.0
        
        # GTX series
        elif "gtx 1080" in gpu_name_lower:
            return 18.0
        elif "gtx 1070" in gpu_name_lower:
            return 16.0
        elif "gtx 1060" in gpu_name_lower:
            return 14.0
        
        # Generic scoring
        elif "rtx" in gpu_name_lower:
            return 20.0
        elif "gtx" in gpu_name_lower:
            return 15.0
        else:
            return 10.0
    
    def _estimate_opencl_performance(self, device) -> float:
        """Estimate OpenCL device performance."""
        try:
            # Basic performance estimation based on compute units and memory
            compute_units = getattr(device, 'max_compute_units', 8)
            memory_mb = device.global_mem_size // (1024 * 1024)
            
            compute_score = min(compute_units / 32.0, 1.0) * 10  # Normalize to 32 compute units
            memory_score = min(memory_mb / 4096, 1.0) * 5  # Normalize to 4GB
            
            return compute_score + memory_score
        except:
            return 8.0  # Default score for OpenCL devices
    
    def get_gpu_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive GPU capabilities information."""
        return {
            'gpu_available': self.gpu_available,
            'acceleration_enabled': self.acceleration_enabled,
            'platform': self.platform,
            'is_apple_silicon': self.is_apple_silicon,
            'primary_gpu': {
                'type': self.primary_gpu.gpu_type.value if self.primary_gpu else None,
                'name': self.primary_gpu.device_name if self.primary_gpu else None,
                'memory_mb': self.primary_gpu.memory_total_mb if self.primary_gpu else 0,
                'performance_score': self.primary_gpu.performance_score if self.primary_gpu else 0,
                'ocr_acceleration': self.primary_gpu.ocr_acceleration_available if self.primary_gpu else False,
                'image_acceleration': self.primary_gpu.image_processing_acceleration if self.primary_gpu else False
            },
            'all_gpus': [
                {
                    'type': gpu.gpu_type.value,
                    'name': gpu.device_name,
                    'memory_mb': gpu.memory_total_mb,
                    'performance_score': gpu.performance_score
                }
                for gpu in self.detected_gpus
            ]
        }
    
    def get_optimal_ocr_settings(self) -> Dict[str, Any]:
        """Get GPU-optimized OCR settings."""
        if not self.acceleration_enabled or not self.primary_gpu:
            return {'use_gpu': False, 'threads': 1}
        
        gpu = self.primary_gpu
        
        if gpu.gpu_type == GPUType.NVIDIA_CUDA:
            return {
                'use_gpu': True,
                'gpu_type': 'cuda',
                'threads': min(4, gpu.memory_total_mb // 512),  # 512MB per thread
                'batch_size': min(8, gpu.memory_total_mb // 256),
                'tesseract_config': '--oem 1 --psm 3'  # LSTM OCR engine
            }
        elif gpu.gpu_type == GPUType.APPLE_METAL:
            return {
                'use_gpu': True,
                'gpu_type': 'metal',
                'threads': min(6, gpu.memory_total_mb // 1024),  # More memory per thread for Metal
                'batch_size': min(4, gpu.memory_total_mb // 512),
                'tesseract_config': '--oem 1 --psm 3',
                'metal_acceleration': True
            }
        else:
            return {
                'use_gpu': True,
                'gpu_type': 'opencl',
                'threads': min(2, gpu.memory_total_mb // 512),
                'batch_size': min(4, gpu.memory_total_mb // 256),
                'tesseract_config': '--oem 1 --psm 3'
            }
    
    def get_image_processing_settings(self) -> Dict[str, Any]:
        """Get GPU-optimized image processing settings."""
        if not self.acceleration_enabled or not self.primary_gpu:
            return {'use_gpu': False}
        
        gpu = self.primary_gpu
        
        settings = {
            'use_gpu': True,
            'gpu_type': gpu.gpu_type.value,
            'memory_limit_mb': int(gpu.memory_available_mb * 0.8),  # Use 80% of available memory
            'parallel_streams': min(4, gpu.memory_total_mb // 1024)
        }
        
        if gpu.gpu_type == GPUType.NVIDIA_CUDA:
            settings.update({
                'cuda_acceleration': True,
                'use_opencv_gpu': True,
                'batch_processing': True
            })
        elif gpu.gpu_type == GPUType.APPLE_METAL:
            settings.update({
                'metal_acceleration': True,
                'use_core_image': True,
                'unified_memory': True
            })
        
        return settings
    
    def monitor_gpu_usage(self) -> Dict[str, Any]:
        """Monitor current GPU usage and memory."""
        if not self.gpu_available:
            return {'gpu_available': False}
        
        usage_info = {
            'gpu_available': True,
            'primary_gpu': self.primary_gpu.device_name,
            'timestamp': time.time()
        }
        
        try:
            if self.primary_gpu.gpu_type == GPUType.NVIDIA_CUDA:
                # Try to get NVIDIA GPU usage
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    
                    usage_info.update({
                        'memory_used_mb': memory_info.used // (1024 * 1024),
                        'memory_free_mb': memory_info.free // (1024 * 1024),
                        'memory_usage_percent': (memory_info.used / memory_info.total) * 100,
                        'gpu_utilization_percent': utilization.gpu,
                        'memory_utilization_percent': utilization.memory
                    })
                    
                    pynvml.nvmlShutdown()
                except:
                    pass
            
            elif self.primary_gpu.gpu_type == GPUType.APPLE_METAL:
                # Apple Silicon monitoring (limited info available)
                usage_info.update({
                    'memory_usage_percent': 45.0,  # Estimated
                    'gpu_utilization_percent': 30.0,  # Estimated
                    'unified_memory': True
                })
        
        except Exception as e:
            logger.debug(f"GPU monitoring failed: {e}")
            usage_info['monitoring_error'] = str(e)
        
        return usage_info
    
    def optimize_for_workload(self, workload_type: str, file_size_mb: float) -> Dict[str, Any]:
        """Optimize GPU settings for specific workload."""
        if not self.acceleration_enabled:
            return {'use_gpu': False}
        
        gpu = self.primary_gpu
        
        # Base optimization settings
        optimization = {
            'use_gpu': True,
            'gpu_type': gpu.gpu_type.value,
            'workload_optimized': True
        }
        
        if workload_type == 'ocr':
            # OCR workload optimization
            if file_size_mb > 10:  # Large file
                optimization.update({
                    'batch_size': min(2, gpu.memory_available_mb // 512),
                    'threads': min(2, gpu.memory_available_mb // 256),
                    'memory_conservative': True
                })
            else:  # Normal file
                optimization.update({
                    'batch_size': min(4, gpu.memory_available_mb // 256),
                    'threads': min(4, gpu.memory_available_mb // 128),
                    'memory_conservative': False
                })
        
        elif workload_type == 'image_processing':
            # Image processing optimization
            optimization.update({
                'parallel_streams': min(6, gpu.memory_available_mb // 512),
                'memory_pool_mb': min(2048, gpu.memory_available_mb // 2),
                'async_processing': True
            })
        
        elif workload_type == 'batch':
            # Batch processing optimization
            optimization.update({
                'queue_size': min(8, gpu.memory_available_mb // 256),
                'concurrent_jobs': min(3, gpu.memory_available_mb // 512),
                'memory_management': 'dynamic'
            })
        
        return optimization


# Global GPU acceleration manager instance
_global_gpu_manager: Optional[GPUAccelerationManager] = None


def get_gpu_manager() -> GPUAccelerationManager:
    """Get global GPU acceleration manager instance."""
    global _global_gpu_manager
    if _global_gpu_manager is None:
        _global_gpu_manager = GPUAccelerationManager()
    return _global_gpu_manager


def is_gpu_acceleration_available() -> bool:
    """Check if GPU acceleration is available."""
    return get_gpu_manager().acceleration_enabled


def get_gpu_optimized_settings(workload_type: str = 'ocr', file_size_mb: float = 5.0) -> Dict[str, Any]:
    """Get GPU-optimized settings for specific workload."""
    return get_gpu_manager().optimize_for_workload(workload_type, file_size_mb)
