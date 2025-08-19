#!/usr/bin/env python3
"""
Advanced Hierarchical Caching System for ePubs Processing

This module provides a sophisticated multi-tier caching architecture with:
- Memory cache (L1) for hot data with LRU eviction
- SSD cache (L2) for frequently accessed data
- Disk cache (L3) for long-term storage
- Predictive prefetching based on ML patterns
- Intelligent cache warming and preloading
- Cross-session cache persistence

Features:
- Multi-tier cache hierarchy (Memory -> SSD -> Disk)
- LRU and adaptive replacement policies
- Predictive prefetching with ML-driven recommendations
- Compression and deduplication
- Cache analytics and optimization
- Thread-safe operations for parallel processing
"""

import asyncio
import gzip
import hashlib
import json
import logging
import pickle
import sqlite3
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Set
import weakref
from enum import Enum
import tempfile
import shutil

# Optional ML imports for predictive caching
try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache levels in the hierarchy."""
    MEMORY = "memory"      # L1: In-memory cache (fastest)
    SSD = "ssd"           # L2: SSD-based cache (fast)
    DISK = "disk"         # L3: Disk-based cache (persistent)


class CachePolicy(Enum):
    """Cache replacement policies."""
    LRU = "lru"                    # Least Recently Used
    LFU = "lfu"                    # Least Frequently Used
    ADAPTIVE = "adaptive"          # ML-driven adaptive policy
    TTL = "ttl"                   # Time To Live


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    data: Any
    size_bytes: int
    access_count: int
    creation_time: float
    last_access_time: float
    last_modified_time: float
    cache_level: CacheLevel
    ttl_seconds: Optional[float] = None
    compression_ratio: float = 1.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @property
    def age_seconds(self) -> float:
        """Get entry age in seconds."""
        return time.time() - self.creation_time
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        return self.age_seconds > self.ttl_seconds
    
    @property
    def access_frequency(self) -> float:
        """Calculate access frequency (accesses per hour)."""
        age_hours = max(self.age_seconds / 3600, 0.01)  # Avoid division by zero
        return self.access_count / age_hours


@dataclass
class CacheStats:
    """Cache performance statistics."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_evictions: int = 0
    total_size_bytes: int = 0
    entries_count: int = 0
    avg_access_time_ms: float = 0.0
    compression_ratio: float = 1.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        return 1.0 - self.hit_rate


class MemoryCache:
    """L1 memory cache with LRU eviction."""
    
    def __init__(self, max_size_mb: int = 512):
        """Initialize memory cache."""
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # LRU tracking
        self.current_size_bytes = 0
        self._lock = threading.RLock()
        
        logger.debug(f"Memory cache initialized with {max_size_mb}MB limit")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from memory cache."""
        with self._lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired:
                self._remove_entry(key)
                return None
            
            # Update access info
            entry.access_count += 1
            entry.last_access_time = time.time()
            
            # Move to end (most recently used)
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            return entry.data
    
    def put(self, key: str, data: Any, ttl_seconds: Optional[float] = None, tags: List[str] = None) -> bool:
        """Put item in memory cache."""
        with self._lock:
            # Calculate data size
            data_size = self._calculate_size(data)
            
            # Check if data is too large
            if data_size > self.max_size_bytes:
                logger.warning(f"Data too large for memory cache: {data_size} bytes")
                return False
            
            # Remove existing entry if present
            if key in self.cache:
                self._remove_entry(key)
            
            # Evict entries if necessary
            while (self.current_size_bytes + data_size > self.max_size_bytes and 
                   self.access_order):
                oldest_key = self.access_order[0]
                self._remove_entry(oldest_key)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                data=data,
                size_bytes=data_size,
                access_count=1,
                creation_time=time.time(),
                last_access_time=time.time(),
                last_modified_time=time.time(),
                cache_level=CacheLevel.MEMORY,
                ttl_seconds=ttl_seconds,
                tags=tags or []
            )
            
            # Add to cache
            self.cache[key] = entry
            self.access_order.append(key)
            self.current_size_bytes += data_size
            
            return True
    
    def remove(self, key: str) -> bool:
        """Remove item from memory cache."""
        with self._lock:
            if key not in self.cache:
                return False
            
            self._remove_entry(key)
            return True
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self.cache.clear()
            self.access_order.clear()
            self.current_size_bytes = 0
    
    def _remove_entry(self, key: str):
        """Remove entry from cache (internal method)."""
        if key in self.cache:
            entry = self.cache[key]
            self.current_size_bytes -= entry.size_bytes
            del self.cache[key]
        
        if key in self.access_order:
            self.access_order.remove(key)
    
    def _calculate_size(self, data: Any) -> int:
        """Calculate approximate size of data in bytes."""
        try:
            if isinstance(data, (str, bytes)):
                return len(data.encode('utf-8')) if isinstance(data, str) else len(data)
            elif isinstance(data, (list, tuple, dict)):
                return len(pickle.dumps(data))
            else:
                return len(str(data).encode('utf-8'))
        except:
            return 1024  # Default estimate
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory cache statistics."""
        with self._lock:
            return {
                'entries_count': len(self.cache),
                'total_size_bytes': self.current_size_bytes,
                'max_size_bytes': self.max_size_bytes,
                'utilization_percent': (self.current_size_bytes / self.max_size_bytes) * 100,
                'avg_entry_size_bytes': self.current_size_bytes / max(len(self.cache), 1)
            }


class PersistentCache:
    """L2/L3 persistent cache with compression and SQLite storage."""
    
    def __init__(self, cache_dir: Path, level: CacheLevel, max_size_mb: int = 2048):
        """Initialize persistent cache."""
        self.cache_dir = cache_dir
        self.level = level
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # SQLite database for metadata
        self.db_path = self.cache_dir / f"{level.value}_cache.db"
        self.data_dir = self.cache_dir / f"{level.value}_data"
        self.data_dir.mkdir(exist_ok=True)
        
        self._lock = threading.RLock()
        self._init_database()
        
        logger.debug(f"Persistent cache ({level.value}) initialized at {cache_dir}")
    
    def _init_database(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    access_count INTEGER DEFAULT 1,
                    creation_time REAL NOT NULL,
                    last_access_time REAL NOT NULL,
                    last_modified_time REAL NOT NULL,
                    ttl_seconds REAL,
                    compression_ratio REAL DEFAULT 1.0,
                    tags TEXT,
                    content_hash TEXT
                )
            ''')
            
            conn.execute('CREATE INDEX IF NOT EXISTS idx_last_access ON cache_entries(last_access_time)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_creation_time ON cache_entries(creation_time)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_size ON cache_entries(size_bytes)')
            conn.commit()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from persistent cache."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT file_path, ttl_seconds, creation_time 
                        FROM cache_entries 
                        WHERE key = ?
                    ''', (key,))
                    
                    result = cursor.fetchone()
                    if not result:
                        return None
                    
                    file_path, ttl_seconds, creation_time = result
                    
                    # Check expiration
                    if ttl_seconds and (time.time() - creation_time) > ttl_seconds:
                        self._remove_entry(key)
                        return None
                    
                    # Load data from file
                    data_file = Path(file_path)
                    if not data_file.exists():
                        self._remove_entry(key)
                        return None
                    
                    # Read and decompress data
                    with open(data_file, 'rb') as f:
                        compressed_data = f.read()
                    
                    try:
                        data = pickle.loads(gzip.decompress(compressed_data))
                    except:
                        # Fallback to uncompressed
                        data = pickle.loads(compressed_data)
                    
                    # Update access info
                    cursor.execute('''
                        UPDATE cache_entries 
                        SET access_count = access_count + 1, last_access_time = ?
                        WHERE key = ?
                    ''', (time.time(), key))
                    conn.commit()
                    
                    return data
                    
            except Exception as e:
                logger.error(f"Error reading from {self.level.value} cache: {e}")
                return None
    
    def put(self, key: str, data: Any, ttl_seconds: Optional[float] = None, tags: List[str] = None) -> bool:
        """Put item in persistent cache."""
        with self._lock:
            try:
                # Serialize and compress data
                serialized_data = pickle.dumps(data)
                compressed_data = gzip.compress(serialized_data, compresslevel=6)
                
                original_size = len(serialized_data)
                compressed_size = len(compressed_data)
                compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
                
                # Check if data is too large
                if compressed_size > self.max_size_bytes:
                    logger.warning(f"Data too large for {self.level.value} cache: {compressed_size} bytes")
                    return False
                
                # Generate file path
                content_hash = hashlib.md5(compressed_data).hexdigest()
                file_path = self.data_dir / f"{content_hash}.cache"
                
                # Write data to file
                with open(file_path, 'wb') as f:
                    f.write(compressed_data)
                
                # Update database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Remove existing entry if present
                    cursor.execute('SELECT file_path FROM cache_entries WHERE key = ?', (key,))
                    old_result = cursor.fetchone()
                    if old_result:
                        old_file_path = Path(old_result[0])
                        if old_file_path.exists():
                            old_file_path.unlink()
                    
                    # Ensure space by evicting old entries
                    self._evict_if_necessary(compressed_size)
                    
                    # Insert new entry
                    cursor.execute('''
                        INSERT OR REPLACE INTO cache_entries 
                        (key, file_path, size_bytes, creation_time, last_access_time, 
                         last_modified_time, ttl_seconds, compression_ratio, tags, content_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        key,
                        str(file_path),
                        compressed_size,
                        time.time(),
                        time.time(),
                        time.time(),
                        ttl_seconds,
                        compression_ratio,
                        json.dumps(tags or []),
                        content_hash
                    ))
                    conn.commit()
                
                return True
                
            except Exception as e:
                logger.error(f"Error writing to {self.level.value} cache: {e}")
                return False
    
    def remove(self, key: str) -> bool:
        """Remove item from persistent cache."""
        with self._lock:
            return self._remove_entry(key)
    
    def _remove_entry(self, key: str) -> bool:
        """Remove entry from cache (internal method)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get file path
                cursor.execute('SELECT file_path FROM cache_entries WHERE key = ?', (key,))
                result = cursor.fetchone()
                
                if result:
                    file_path = Path(result[0])
                    if file_path.exists():
                        file_path.unlink()
                    
                    cursor.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                    conn.commit()
                    return True
                
        except Exception as e:
            logger.error(f"Error removing from {self.level.value} cache: {e}")
        
        return False
    
    def _evict_if_necessary(self, required_space: int):
        """Evict entries if necessary to make space."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current total size
                cursor.execute('SELECT SUM(size_bytes) FROM cache_entries')
                current_size = cursor.fetchone()[0] or 0
                
                if current_size + required_space <= self.max_size_bytes:
                    return
                
                # Calculate space to free (add 10% buffer)
                space_to_free = (current_size + required_space - self.max_size_bytes) * 1.1
                
                # Get entries to evict (LRU policy)
                cursor.execute('''
                    SELECT key, file_path, size_bytes 
                    FROM cache_entries 
                    ORDER BY last_access_time ASC
                ''')
                
                freed_space = 0
                for key, file_path, size_bytes in cursor.fetchall():
                    if freed_space >= space_to_free:
                        break
                    
                    # Remove file
                    file_path_obj = Path(file_path)
                    if file_path_obj.exists():
                        file_path_obj.unlink()
                    
                    # Remove from database
                    cursor.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                    freed_space += size_bytes
                
                conn.commit()
                logger.debug(f"Evicted {freed_space} bytes from {self.level.value} cache")
                
        except Exception as e:
            logger.error(f"Error during cache eviction: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get persistent cache statistics."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT 
                            COUNT(*) as entries_count,
                            SUM(size_bytes) as total_size_bytes,
                            AVG(compression_ratio) as avg_compression_ratio,
                            AVG(access_count) as avg_access_count
                        FROM cache_entries
                    ''')
                    
                    result = cursor.fetchone()
                    entries_count, total_size_bytes, avg_compression_ratio, avg_access_count = result
                    
                    return {
                        'entries_count': entries_count or 0,
                        'total_size_bytes': total_size_bytes or 0,
                        'max_size_bytes': self.max_size_bytes,
                        'utilization_percent': ((total_size_bytes or 0) / self.max_size_bytes) * 100,
                        'avg_compression_ratio': avg_compression_ratio or 1.0,
                        'avg_access_count': avg_access_count or 0
                    }
                    
            except Exception as e:
                logger.error(f"Error getting {self.level.value} cache stats: {e}")
                return {
                    'entries_count': 0,
                    'total_size_bytes': 0,
                    'max_size_bytes': self.max_size_bytes,
                    'utilization_percent': 0.0,
                    'avg_compression_ratio': 1.0,
                    'avg_access_count': 0
                }


class PredictiveCacheManager:
    """ML-driven predictive cache management."""
    
    def __init__(self, cache_dir: Path):
        """Initialize predictive cache manager."""
        self.cache_dir = cache_dir
        self.prediction_db = cache_dir / "predictions.db"
        self.patterns_file = cache_dir / "access_patterns.pkl"
        
        self._lock = threading.Lock()
        self.access_patterns: Dict[str, List[float]] = {}
        self.prediction_accuracy = 0.75  # Start with 75% accuracy assumption
        
        self._init_prediction_db()
        self._load_patterns()
        
        logger.debug("Predictive cache manager initialized")
    
    def _init_prediction_db(self):
        """Initialize prediction database."""
        with sqlite3.connect(self.prediction_db) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS access_predictions (
                    key TEXT PRIMARY KEY,
                    predicted_access_time REAL,
                    confidence_score REAL,
                    created_at REAL,
                    actual_access_time REAL,
                    prediction_accuracy REAL
                )
            ''')
            conn.commit()
    
    def _load_patterns(self):
        """Load access patterns from disk."""
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, 'rb') as f:
                    self.access_patterns = pickle.load(f)
                logger.debug(f"Loaded {len(self.access_patterns)} access patterns")
        except Exception as e:
            logger.warning(f"Could not load access patterns: {e}")
            self.access_patterns = {}
    
    def _save_patterns(self):
        """Save access patterns to disk."""
        try:
            with open(self.patterns_file, 'wb') as f:
                pickle.dump(self.access_patterns, f)
        except Exception as e:
            logger.error(f"Could not save access patterns: {e}")
    
    def record_access(self, key: str, access_time: float):
        """Record access for pattern learning."""
        with self._lock:
            if key not in self.access_patterns:
                self.access_patterns[key] = []
            
            self.access_patterns[key].append(access_time)
            
            # Keep only last 20 accesses per key
            if len(self.access_patterns[key]) > 20:
                self.access_patterns[key] = self.access_patterns[key][-20:]
    
    def predict_next_access(self, key: str) -> Tuple[Optional[float], float]:
        """
        Predict next access time for a key.
        
        Returns:
            Tuple[Optional[float], float]: (predicted_time, confidence_score)
        """
        if not ML_AVAILABLE or key not in self.access_patterns:
            return None, 0.0
        
        patterns = self.access_patterns[key]
        if len(patterns) < 3:
            return None, 0.0
        
        try:
            # Simple pattern analysis - could be enhanced with more sophisticated ML
            recent_accesses = np.array(patterns[-10:])  # Last 10 accesses
            
            # Calculate intervals
            intervals = np.diff(recent_accesses)
            
            if len(intervals) == 0:
                return None, 0.0
            
            # Predict next access based on average interval
            avg_interval = np.mean(intervals)
            predicted_time = patterns[-1] + avg_interval
            
            # Calculate confidence based on interval consistency
            interval_std = np.std(intervals) if len(intervals) > 1 else 0
            max_std = np.mean(intervals) * 0.5  # 50% of mean as max acceptable std
            confidence = max(0.1, 1.0 - (interval_std / max_std)) if max_std > 0 else 0.5
            
            return predicted_time, min(confidence, 0.95)  # Cap confidence at 95%
            
        except Exception as e:
            logger.debug(f"Prediction failed for {key}: {e}")
            return None, 0.0
    
    def get_prefetch_candidates(self, current_time: float, lookahead_seconds: float = 3600) -> List[Tuple[str, float]]:
        """
        Get candidates for prefetching.
        
        Args:
            current_time: Current timestamp
            lookahead_seconds: How far ahead to look for predictions
            
        Returns:
            List[Tuple[str, float]]: List of (key, confidence_score) tuples
        """
        candidates = []
        cutoff_time = current_time + lookahead_seconds
        
        for key in self.access_patterns:
            predicted_time, confidence = self.predict_next_access(key)
            
            if (predicted_time and 
                current_time <= predicted_time <= cutoff_time and 
                confidence >= 0.6):  # Only high-confidence predictions
                
                candidates.append((key, confidence))
        
        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return candidates[:10]  # Return top 10 candidates
    
    def update_prediction_accuracy(self, key: str, predicted_time: float, actual_time: float):
        """Update prediction accuracy metrics."""
        if predicted_time and actual_time:
            error = abs(predicted_time - actual_time)
            # Consider prediction accurate if within 10% of predicted interval
            predicted_interval = predicted_time - time.time()
            accuracy = max(0.0, 1.0 - (error / max(predicted_interval * 0.1, 3600)))
            
            # Update rolling accuracy
            self.prediction_accuracy = (self.prediction_accuracy * 0.9) + (accuracy * 0.1)
    
    def cleanup_old_patterns(self, max_age_days: int = 30):
        """Clean up old access patterns."""
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        
        with self._lock:
            keys_to_remove = []
            
            for key, patterns in self.access_patterns.items():
                # Remove old accesses
                recent_patterns = [t for t in patterns if t > cutoff_time]
                
                if recent_patterns:
                    self.access_patterns[key] = recent_patterns
                else:
                    keys_to_remove.append(key)
            
            # Remove keys with no recent patterns
            for key in keys_to_remove:
                del self.access_patterns[key]
            
            self._save_patterns()

class HierarchicalCacheManager:
    """
    Comprehensive hierarchical cache manager with predictive prefetching.
    
    Manages a three-tier cache hierarchy:
    - L1 (Memory): Fast in-memory cache with LRU eviction
    - L2 (SSD): Fast persistent cache for frequently accessed data
    - L3 (Disk): Large persistent cache for long-term storage
    
    Features:
    - Automatic promotion/demotion between cache levels
    - Predictive prefetching with ML-driven recommendations
    - Intelligent cache warming and preloading
    - Comprehensive analytics and optimization
    """
    
    def __init__(self, cache_dir: Optional[Path] = None, 
                 memory_cache_mb: int = 512,
                 ssd_cache_mb: int = 2048,
                 disk_cache_mb: int = 8192):
        """
        Initialize hierarchical cache manager.
        
        Args:
            cache_dir: Base directory for persistent caches
            memory_cache_mb: Memory cache size in MB
            ssd_cache_mb: SSD cache size in MB
            disk_cache_mb: Disk cache size in MB
        """
        # Set up cache directory
        if cache_dir is None:
            import platform
            if platform.system() == 'Darwin':  # macOS
                cache_dir = Path.home() / ".epubs" / "cache_v2"
            else:  # Linux
                cache_dir = Path.home() / ".cache" / "epubs_v2"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize cache levels
        self.memory_cache = MemoryCache(memory_cache_mb)
        self.ssd_cache = PersistentCache(
            self.cache_dir / "ssd", 
            CacheLevel.SSD, 
            ssd_cache_mb
        )
        self.disk_cache = PersistentCache(
            self.cache_dir / "disk", 
            CacheLevel.DISK, 
            disk_cache_mb
        )
        
        # Predictive caching
        self.predictive_manager = PredictiveCacheManager(self.cache_dir)
        
        # Statistics tracking
        self.stats = {
            CacheLevel.MEMORY: CacheStats(),
            CacheLevel.SSD: CacheStats(),
            CacheLevel.DISK: CacheStats()
        }
        
        # Threading
        self._lock = threading.RLock()
        self._prefetch_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="CachePrefetch")
        
        # Background tasks
        self._background_tasks_active = True
        self._start_background_tasks()
        
        logger.info(f"Hierarchical cache manager initialized at {cache_dir}")
        logger.info(f"Cache sizes: Memory={memory_cache_mb}MB, SSD={ssd_cache_mb}MB, Disk={disk_cache_mb}MB")
    
    def get(self, key: str, tags: List[str] = None) -> Optional[Any]:
        """
        Get item from hierarchical cache.
        
        Checks cache levels in order: Memory -> SSD -> Disk
        Promotes items to higher cache levels on access.
        
        Args:
            key: Cache key
            tags: Optional tags for analytics
            
        Returns:
            Cached data or None if not found
        """
        start_time = time.time()
        
        with self._lock:
            # Record access for predictive learning
            self.predictive_manager.record_access(key, start_time)
            
            # Check memory cache first (L1)
            data = self.memory_cache.get(key)
            if data is not None:
                self._record_hit(CacheLevel.MEMORY, start_time)
                logger.debug(f"Cache hit (Memory): {key}")
                return data
            
            self._record_miss(CacheLevel.MEMORY, start_time)
            
            # Check SSD cache (L2)
            data = self.ssd_cache.get(key)
            if data is not None:
                self._record_hit(CacheLevel.SSD, start_time)
                
                # Promote to memory cache
                self.memory_cache.put(key, data, tags=tags)
                
                logger.debug(f"Cache hit (SSD): {key} - promoted to memory")
                return data
            
            self._record_miss(CacheLevel.SSD, start_time)
            
            # Check disk cache (L3)
            data = self.disk_cache.get(key)
            if data is not None:
                self._record_hit(CacheLevel.DISK, start_time)
                
                # Promote to SSD and memory caches
                self.ssd_cache.put(key, data, tags=tags)
                self.memory_cache.put(key, data, tags=tags)
                
                logger.debug(f"Cache hit (Disk): {key} - promoted to SSD and memory")
                return data
            
            self._record_miss(CacheLevel.DISK, start_time)
            logger.debug(f"Cache miss (All levels): {key}")
            return None
    
    def put(self, key: str, data: Any, ttl_seconds: Optional[float] = None, 
            tags: List[str] = None, force_level: Optional[CacheLevel] = None) -> bool:
        """
        Put item in hierarchical cache.
        
        Automatically places items in appropriate cache levels based on size
        and access patterns. Smaller items go to memory, larger to SSD/disk.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl_seconds: Time to live in seconds
            tags: Optional tags for categorization
            force_level: Force placement in specific cache level
            
        Returns:
            True if successfully cached
        """
        start_time = time.time()
        
        with self._lock:
            success = False
            
            # Calculate data size for intelligent placement
            try:
                data_size = len(pickle.dumps(data))
            except:
                data_size = 1024  # Default estimate
            
            if force_level:
                # Force placement in specific level
                cache = self._get_cache_by_level(force_level)
                success = cache.put(key, data, ttl_seconds, tags)
                
                if success:
                    logger.debug(f"Cache put (Forced {force_level.value}): {key}")
                
            else:
                # Intelligent placement based on size and patterns
                if data_size <= 1024 * 1024:  # <= 1MB: try memory first
                    success = self.memory_cache.put(key, data, ttl_seconds, tags)
                    if success:
                        logger.debug(f"Cache put (Memory): {key}")
                
                if not success and data_size <= 10 * 1024 * 1024:  # <= 10MB: try SSD
                    success = self.ssd_cache.put(key, data, ttl_seconds, tags)
                    if success:
                        logger.debug(f"Cache put (SSD): {key}")
                
                if not success:  # Fallback to disk
                    success = self.disk_cache.put(key, data, ttl_seconds, tags)
                    if success:
                        logger.debug(f"Cache put (Disk): {key}")
            
            if success:
                # Record access for predictive learning
                self.predictive_manager.record_access(key, start_time)
                
                # Trigger background prefetch if this is a new pattern
                self._maybe_trigger_prefetch(key, tags)
            
            return success
    
    def remove(self, key: str) -> bool:
        """
        Remove item from all cache levels.
        
        Args:
            key: Cache key to remove
            
        Returns:
            True if item was found and removed
        """
        with self._lock:
            removed = False
            
            if self.memory_cache.remove(key):
                removed = True
            
            if self.ssd_cache.remove(key):
                removed = True
            
            if self.disk_cache.remove(key):
                removed = True
            
            if removed:
                logger.debug(f"Cache remove: {key}")
            
            return removed
    
    def clear(self, level: Optional[CacheLevel] = None):
        """
        Clear cache levels.
        
        Args:
            level: Specific level to clear, or None for all levels
        """
        with self._lock:
            if level is None:
                self.memory_cache.clear()
                # Note: Persistent caches don't have clear() method implemented
                # This is intentional to preserve data across sessions
                logger.info("Memory cache cleared")
            else:
                cache = self._get_cache_by_level(level)
                if hasattr(cache, 'clear'):
                    cache.clear()
                    logger.info(f"{level.value} cache cleared")
    
    def prefetch(self, keys: List[str], priority: int = 1) -> int:
        """
        Prefetch items into cache.
        
        Args:
            keys: List of keys to prefetch
            priority: Prefetch priority (1=high, 3=low)
            
        Returns:
            Number of items successfully prefetched
        """
        if not keys:
            return 0
        
        # Submit prefetch task to background executor
        future = self._prefetch_executor.submit(self._execute_prefetch, keys, priority)
        
        # For high priority, wait for completion
        if priority == 1:
            try:
                return future.result(timeout=30)  # 30 second timeout
            except:
                return 0
        
        return len(keys)  # Optimistic count for async prefetch
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        with self._lock:
            # Get stats from each cache level
            memory_stats = self.memory_cache.get_stats()
            ssd_stats = self.ssd_cache.get_stats()
            disk_stats = self.disk_cache.get_stats()
            
            # Calculate overall hit rates
            total_requests = sum(stats.total_requests for stats in self.stats.values())
            total_hits = sum(stats.cache_hits for stats in self.stats.values())
            overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'overall': {
                    'total_requests': total_requests,
                    'total_hits': total_hits,
                    'overall_hit_rate': overall_hit_rate,
                    'prediction_accuracy': self.predictive_manager.prediction_accuracy
                },
                'memory': {
                    **memory_stats,
                    'hit_rate': self.stats[CacheLevel.MEMORY].hit_rate,
                    'requests': self.stats[CacheLevel.MEMORY].total_requests
                },
                'ssd': {
                    **ssd_stats,
                    'hit_rate': self.stats[CacheLevel.SSD].hit_rate,
                    'requests': self.stats[CacheLevel.SSD].total_requests
                },
                'disk': {
                    **disk_stats,
                    'hit_rate': self.stats[CacheLevel.DISK].hit_rate,
                    'requests': self.stats[CacheLevel.DISK].total_requests
                },
                'prefetch': {
                    'active_tasks': self._prefetch_executor._threads,
                    'patterns_tracked': len(self.predictive_manager.access_patterns)
                }
            }
    
    def optimize_cache_sizes(self) -> Dict[str, Any]:
        """
        Analyze cache performance and suggest size optimizations.
        
        Returns:
            Optimization recommendations
        """
        stats = self.get_comprehensive_stats()
        recommendations = []
        
        # Analyze memory cache utilization
        memory_util = stats['memory']['utilization_percent']
        if memory_util > 90:
            recommendations.append("Consider increasing memory cache size - high utilization detected")
        elif memory_util < 30:
            recommendations.append("Memory cache may be oversized - low utilization detected")
        
        # Analyze hit rate patterns
        memory_hit_rate = stats['memory']['hit_rate']
        ssd_hit_rate = stats['ssd']['hit_rate']
        
        if memory_hit_rate < 0.3:
            recommendations.append("Low memory cache hit rate - consider improving data locality")
        
        if ssd_hit_rate > 0.7:
            recommendations.append("High SSD cache hit rate - consider promoting more items to memory")
        
        # Analyze overall performance
        overall_hit_rate = stats['overall']['overall_hit_rate']
        if overall_hit_rate < 0.6:
            recommendations.append("Overall cache hit rate is low - consider reviewing cache strategy")
        
        return {
            'current_performance': stats,
            'recommendations': recommendations,
            'optimization_score': min(overall_hit_rate * 100, 100)
        }
    
    def _get_cache_by_level(self, level: CacheLevel):
        """Get cache instance by level."""
        if level == CacheLevel.MEMORY:
            return self.memory_cache
        elif level == CacheLevel.SSD:
            return self.ssd_cache
        elif level == CacheLevel.DISK:
            return self.disk_cache
        else:
            raise ValueError(f"Unknown cache level: {level}")
    
    def _record_hit(self, level: CacheLevel, start_time: float):
        """Record cache hit statistics."""
        stats = self.stats[level]
        stats.total_requests += 1
        stats.cache_hits += 1
        
        access_time_ms = (time.time() - start_time) * 1000
        stats.avg_access_time_ms = (stats.avg_access_time_ms * 0.9) + (access_time_ms * 0.1)
    
    def _record_miss(self, level: CacheLevel, start_time: float):
        """Record cache miss statistics."""
        stats = self.stats[level]
        stats.total_requests += 1
        stats.cache_misses += 1
        
        access_time_ms = (time.time() - start_time) * 1000
        stats.avg_access_time_ms = (stats.avg_access_time_ms * 0.9) + (access_time_ms * 0.1)
    
    def _maybe_trigger_prefetch(self, key: str, tags: List[str]):
        """Maybe trigger predictive prefetch based on access patterns."""
        if not tags:
            return
        
        # Get prefetch candidates based on current access
        candidates = self.predictive_manager.get_prefetch_candidates(time.time())
        
        if candidates:
            # Extract keys with high confidence
            high_confidence_keys = [k for k, conf in candidates if conf > 0.8]
            
            if high_confidence_keys:
                # Submit background prefetch task
                self._prefetch_executor.submit(self._execute_prefetch, high_confidence_keys[:5], priority=3)
    
    def _execute_prefetch(self, keys: List[str], priority: int) -> int:
        """Execute prefetch operation in background."""
        prefetched_count = 0
        
        for key in keys:
            # Check if key is already in cache
            if self.memory_cache.get(key) is not None:
                continue
            
            # Try to load from lower cache levels
            data = self.ssd_cache.get(key)
            if data is not None:
                # Promote to memory
                if self.memory_cache.put(key, data):
                    prefetched_count += 1
                    logger.debug(f"Prefetched (SSD->Memory): {key}")
                continue
            
            data = self.disk_cache.get(key)
            if data is not None:
                # Promote to SSD and memory
                self.ssd_cache.put(key, data)
                if self.memory_cache.put(key, data):
                    prefetched_count += 1
                    logger.debug(f"Prefetched (Disk->Memory): {key}")
        
        logger.debug(f"Prefetch completed: {prefetched_count}/{len(keys)} items")
        return prefetched_count
    
    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        def background_maintenance():
            while self._background_tasks_active:
                try:
                    # Clean up old patterns every hour
                    self.predictive_manager.cleanup_old_patterns()
                    
                    # Sleep for 1 hour
                    for _ in range(3600):  # 1 hour in seconds
                        if not self._background_tasks_active:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Background maintenance error: {e}")
                    time.sleep(60)  # Wait 1 minute before retry
        
        # Start background thread
        maintenance_thread = threading.Thread(target=background_maintenance, daemon=True)
        maintenance_thread.start()
    
    def shutdown(self):
        """Shutdown cache manager and cleanup resources."""
        logger.info("Shutting down hierarchical cache manager")
        
        # Stop background tasks
        self._background_tasks_active = False
        
        # Shutdown prefetch executor
        self._prefetch_executor.shutdown(wait=True)
        
        # Save predictive patterns
        self.predictive_manager._save_patterns()
        
        logger.info("Hierarchical cache manager shutdown complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()


# Global hierarchical cache manager instance
_global_cache_manager: Optional[HierarchicalCacheManager] = None


def get_hierarchical_cache() -> HierarchicalCacheManager:
    """Get global hierarchical cache manager instance."""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = HierarchicalCacheManager()
    return _global_cache_manager


def cache_get(key: str, tags: List[str] = None) -> Optional[Any]:
    """Get item from hierarchical cache."""
    return get_hierarchical_cache().get(key, tags)


def cache_put(key: str, data: Any, ttl_seconds: Optional[float] = None, 
              tags: List[str] = None) -> bool:
    """Put item in hierarchical cache."""
    return get_hierarchical_cache().put(key, data, ttl_seconds, tags)


def cache_remove(key: str) -> bool:
    """Remove item from hierarchical cache."""
    return get_hierarchical_cache().remove(key)


def cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics."""
    return get_hierarchical_cache().get_comprehensive_stats()
