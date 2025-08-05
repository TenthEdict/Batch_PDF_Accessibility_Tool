#!/usr/bin/env python3
"""
Platform Detection Utilities

This module provides utilities for detecting the current platform and hardware
capabilities, with special focus on Apple Silicon chips (M1, M2, M3, M4, etc.)
for optimization purposes.
"""

import platform
import subprocess
import logging
from typing import Dict, Optional, Tuple, List
import sys

logger = logging.getLogger(__name__)


def is_apple_silicon() -> bool:
    """
    Detect if running on Apple Silicon (M1, M2, M3, M4, etc.).
    
    Returns:
        bool: True if running on Apple Silicon, False otherwise
    """
    try:
        # Check if we're on macOS first
        if platform.system() != 'Darwin':
            return False
            
        # Check processor architecture
        machine = platform.machine()
        
        # Apple Silicon uses arm64 architecture
        if machine == 'arm64':
            return True
            
        # Additional check using subprocess for more detailed info
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'machdep.cpu.brand_string'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                cpu_brand = result.stdout.strip()
                # Apple Silicon chips have "Apple" in their brand string
                return 'Apple' in cpu_brand
                
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            # sysctl might not be available, fall back to machine check
            pass
            
        return False
        
    except Exception as e:
        logger.warning(f"Could not detect Apple Silicon: {e}")
        return False


def get_apple_chip() -> Optional[str]:
    """
    Get the specific Apple chip model (M1, M2, M3, M4, etc.).
    
    Returns:
        Optional[str]: Apple chip model (e.g., "M1", "M2", "M3", "M4") or None if not Apple Silicon
    """
    if not is_apple_silicon():
        return None
        
    try:
        # Try to get detailed CPU info
        result = subprocess.run(
            ['sysctl', '-n', 'machdep.cpu.brand_string'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            cpu_brand = result.stdout.strip()
            
            # Extract chip model from brand string
            # Examples: "Apple M1", "Apple M1 Pro", "Apple M1 Max", "Apple M2", "Apple M4"
            if 'Apple M4' in cpu_brand:
                if 'Pro' in cpu_brand:
                    return 'M4 Pro'
                elif 'Max' in cpu_brand:
                    return 'M4 Max'
                else:
                    return 'M4'
            elif 'Apple M3' in cpu_brand:
                if 'Pro' in cpu_brand:
                    return 'M3 Pro'
                elif 'Max' in cpu_brand:
                    return 'M3 Max'
                else:
                    return 'M3'
            elif 'Apple M2' in cpu_brand:
                if 'Pro' in cpu_brand:
                    return 'M2 Pro'
                elif 'Max' in cpu_brand:
                    return 'M2 Max'
                elif 'Ultra' in cpu_brand:
                    return 'M2 Ultra'
                else:
                    return 'M2'
            elif 'Apple M1' in cpu_brand:
                if 'Pro' in cpu_brand:
                    return 'M1 Pro'
                elif 'Max' in cpu_brand:
                    return 'M1 Max'
                elif 'Ultra' in cpu_brand:
                    return 'M1 Ultra'
                else:
                    return 'M1'
            else:
                # Generic Apple Silicon detection
                return 'Apple Silicon'
                
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.warning(f"Could not get detailed Apple chip info: {e}")
        
    # If we can't get specific model but know it's Apple Silicon
    return 'Apple Silicon' if is_apple_silicon() else None


def get_platform_info() -> Dict[str, any]:
    """
    Get comprehensive platform information.
    
    Returns:
        Dict containing platform details
    """
    info = {
        'system': platform.system(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': sys.version,
        'is_apple_silicon': is_apple_silicon(),
        'apple_chip': get_apple_chip(),
    }
    
    # Add macOS specific information
    if platform.system() == 'Darwin':
        try:
            # Get macOS version
            info['macos_version'] = platform.mac_ver()[0]
            
            # Get number of CPU cores
            result = subprocess.run(
                ['sysctl', '-n', 'hw.ncpu'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info['cpu_cores'] = int(result.stdout.strip())
                
            # Get memory size
            result = subprocess.run(
                ['sysctl', '-n', 'hw.memsize'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                memory_bytes = int(result.stdout.strip())
                info['memory_gb'] = round(memory_bytes / (1024**3), 1)
                
        except (subprocess.SubprocessError, ValueError, subprocess.TimeoutExpired):
            pass
    
    return info


def get_optimization_recommendations() -> Dict[str, any]:
    """
    Get optimization recommendations based on current platform.
    
    Returns:
        Dict containing optimization recommendations
    """
    recommendations = {
        'use_apple_optimizations': False,
        'recommended_enhancers': ['ocr_enhancer', 'pdf_enhancer'],
        'performance_tips': [],
        'memory_recommendations': {}
    }
    
    platform_info = get_platform_info()
    
    # Apple Silicon specific recommendations
    if platform_info['is_apple_silicon']:
        recommendations['use_apple_optimizations'] = True
        recommendations['recommended_enhancers'].append('apple_optimized_enhancer')
        
        chip = platform_info.get('apple_chip', '')
        
        if 'M4' in chip:
            recommendations['performance_tips'].extend([
                'M4 chips have excellent ML performance - enable ML enhancer',
                'Use mlx-vlm for optimal Apple Silicon acceleration',
                'Consider larger batch sizes for better throughput'
            ])
            recommendations['recommended_enhancers'].append('ml_enhancer')
            
        elif 'M3' in chip:
            recommendations['performance_tips'].extend([
                'M3 chips support hardware-accelerated ML inference',
                'Enable Apple Silicon optimizations for best performance'
            ])
            recommendations['recommended_enhancers'].append('ml_enhancer')
            
        elif 'M2' in chip:
            recommendations['performance_tips'].extend([
                'M2 chips offer good ML performance',
                'Enable Apple Silicon optimizations'
            ])
            
        elif 'M1' in chip:
            recommendations['performance_tips'].extend([
                'M1 chips benefit from Apple Silicon optimizations',
                'Consider enabling ML features for supported tasks'
            ])
    
    # Memory recommendations
    memory_gb = platform_info.get('memory_gb', 8)
    if memory_gb >= 16:
        recommendations['memory_recommendations']['enable_large_models'] = True
        recommendations['memory_recommendations']['batch_size'] = 'large'
    elif memory_gb >= 8:
        recommendations['memory_recommendations']['enable_large_models'] = False
        recommendations['memory_recommendations']['batch_size'] = 'medium'
    else:
        recommendations['memory_recommendations']['enable_large_models'] = False
        recommendations['memory_recommendations']['batch_size'] = 'small'
        recommendations['performance_tips'].append('Consider upgrading RAM for better performance')
    
    return recommendations


def check_mlx_compatibility() -> bool:
    """
    Check if MLX (Apple's ML framework) is available and compatible.
    
    Returns:
        bool: True if MLX can be used, False otherwise
    """
    if not is_apple_silicon():
        return False
        
    try:
        # Try to import mlx-vlm
        import mlx
        return True
    except ImportError:
        return False


def get_optimal_worker_count() -> int:
    """
    Get optimal number of worker processes based on platform.
    
    Returns:
        int: Recommended number of worker processes
    """
    try:
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        
        # For Apple Silicon, use fewer workers due to efficiency cores
        if is_apple_silicon():
            chip = get_apple_chip()
            if chip and ('M4' in chip or 'M3' in chip):
                # M3/M4 have good multi-core performance
                return min(cpu_count - 1, 6)
            else:
                # M1/M2 benefit from fewer concurrent tasks
                return min(cpu_count - 1, 4)
        else:
            # For other platforms, use more conservative approach
            return min(cpu_count - 1, 4)
            
    except Exception:
        # Safe fallback
        return 2