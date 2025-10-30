"""
GPU Acceleration Module for ePubs Accessibility Enhancement.

This module provides comprehensive GPU acceleration capabilities including:
- Multi-platform GPU detection (CUDA, Metal, OpenCL)
- GPU-accelerated OCR and image processing
- Apple Silicon optimization
- Memory management and performance monitoring

Features:
- Cross-platform GPU support
- Intelligent workload optimization
- Resource monitoring and management
- Fallback strategies for CPU-only systems
"""

from .gpu_manager import (
    GPUAccelerationManager,
    GPUType,
    GPUInfo,
    get_gpu_manager,
    is_gpu_acceleration_available,
    get_gpu_optimized_settings
)

__all__ = [
    'GPUAccelerationManager',
    'GPUType',
    'GPUInfo',
    'get_gpu_manager',
    'is_gpu_acceleration_available',
    'get_gpu_optimized_settings'
]
