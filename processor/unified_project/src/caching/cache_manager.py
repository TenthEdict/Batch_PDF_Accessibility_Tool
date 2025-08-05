#!/usr/bin/env python3
"""
Cache Manager for ePubs Processing

This module provides SQLite-based caching for document processing results,
including OCR output, ML analysis, and processing metadata with automatic
cleanup and performance monitoring.
"""

import sqlite3
import json
import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import platform
import pickle
import gzip

logger = logging.getLogger(__name__)


class CacheManager:
    """
    SQLite-based cache manager for document processing results.
    
    Provides platform-aware caching with automatic cleanup, compression,
    and performance monitoring for ePubs document enhancement pipeline.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache manager with platform-specific cache directory.
        
        Args:
            cache_dir: Optional custom cache directory path
        """
        self.cache_dir = self._get_cache_directory(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.cache_dir / "epubs_cache.db"
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        
        # Performance tracking
        self.stats = {
            'hits': 0,
            'misses': 0,
            'stores': 0,
            'deletions': 0
        }
        
        logger.info(f"Cache manager initialized: {self.cache_dir}")
    
    def _get_cache_directory(self, custom_dir: Optional[Path] = None) -> Path:
        """Get platform-appropriate cache directory."""
        if custom_dir:
            return Path(custom_dir)
        
        system = platform.system()
        if system == 'Darwin':  # macOS
            return Path.home() / ".epubs" / "cache"
        elif system == 'Linux':  # Ubuntu/Linux
            return Path.home() / ".cache" / "epubs"
        else:  # Windows or other
            return Path.home() / ".epubs" / "cache"
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        content_hash TEXT NOT NULL,
                        data_type TEXT NOT NULL,
                        compressed BOOLEAN DEFAULT FALSE,
                        file_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        metadata TEXT,
                        size_bytes INTEGER DEFAULT 0
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS cache_data (
                        cache_id INTEGER PRIMARY KEY,
                        data BLOB NOT NULL,
                        FOREIGN KEY (cache_id) REFERENCES cache_entries (id) ON DELETE CASCADE
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_cache_key ON cache_entries(key)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_content_hash ON cache_entries(content_hash)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)
                ''')
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize cache database: {e}")
            raise    
    def generate_cache_key(self, file_path: Path, operation: str, **kwargs) -> str:
        """
        Generate cache key for a file and operation.
        
        Args:
            file_path: Path to the file being processed
            operation: Operation type (e.g., 'ocr', 'ml_analysis', 'pdf_enhancement')
            **kwargs: Additional parameters that affect the operation
            
        Returns:
            str: Cache key
        """
        # Create hash from file content and operation parameters
        try:
            file_hash = self._calculate_file_hash(file_path)
            
            # Include operation and parameters in key
            key_components = {
                'file_hash': file_hash,
                'operation': operation,
                'file_size': file_path.stat().st_size,
                'modified_time': file_path.stat().st_mtime,
                'parameters': sorted(kwargs.items()) if kwargs else []
            }
            
            key_string = json.dumps(key_components, sort_keys=True)
            return hashlib.sha256(key_string.encode()).hexdigest()
            
        except Exception as e:
            logger.warning(f"Failed to generate cache key for {file_path}: {e}")
            # Fallback to simpler key
            return hashlib.sha256(f"{file_path}_{operation}".encode()).hexdigest()
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash file {file_path}: {e}")
            return f"error_{file_path.stat().st_size}_{file_path.stat().st_mtime}"
    
    def get(self, cache_key: str) -> Optional[Any]:
        """
        Retrieve cached data by key.
        
        Args:
            cache_key: Cache key to retrieve
            
        Returns:
            Cached data or None if not found/expired
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT ce.id, ce.data_type, ce.compressed, ce.expires_at, ce.metadata, cd.data
                    FROM cache_entries ce
                    JOIN cache_data cd ON ce.id = cd.cache_id
                    WHERE ce.key = ?
                ''', (cache_key,))
                
                row = cursor.fetchone()
                if not row:
                    self.stats['misses'] += 1
                    return None
                
                cache_id, data_type, compressed, expires_at, metadata, data_blob = row
                
                # Check expiration
                if expires_at:
                    expires_dt = datetime.fromisoformat(expires_at)
                    if datetime.now() > expires_dt:
                        self._delete_entry(cache_id)
                        self.stats['misses'] += 1
                        return None
                
                # Update access time
                conn.execute('''
                    UPDATE cache_entries SET accessed_at = CURRENT_TIMESTAMP WHERE id = ?
                ''', (cache_id,))
                
                # Decompress and deserialize data
                if compressed:
                    data_blob = gzip.decompress(data_blob)
                
                if data_type == 'json':
                    data = json.loads(data_blob.decode())
                elif data_type == 'pickle':
                    data = pickle.loads(data_blob)
                else:
                    data = data_blob.decode()
                
                self.stats['hits'] += 1
                logger.debug(f"Cache hit for key: {cache_key[:12]}...")
                return data
                
        except Exception as e:
            logger.warning(f"Failed to retrieve cache entry {cache_key}: {e}")
            self.stats['misses'] += 1
            return None    
    def put(self, cache_key: str, data: Any, data_type: str = 'auto', 
            expires_in_hours: Optional[int] = None, metadata: Optional[Dict] = None) -> bool:
        """
        Store data in cache.
        
        Args:
            cache_key: Cache key
            data: Data to cache
            data_type: Data type ('json', 'pickle', 'text', 'auto')
            expires_in_hours: Expiration time in hours (None = no expiration)
            metadata: Optional metadata dictionary
            
        Returns:
            bool: True if stored successfully
        """
        try:
            # Auto-detect data type
            if data_type == 'auto':
                if isinstance(data, (dict, list)):
                    data_type = 'json'
                elif isinstance(data, str):
                    data_type = 'text'
                else:
                    data_type = 'pickle'
            
            # Serialize data
            if data_type == 'json':
                data_blob = json.dumps(data, default=str).encode()
            elif data_type == 'pickle':
                data_blob = pickle.dumps(data)
            else:
                data_blob = str(data).encode()
            
            # Compress if beneficial
            compressed = False
            if len(data_blob) > 1024:  # Compress data larger than 1KB
                compressed_blob = gzip.compress(data_blob)
                if len(compressed_blob) < len(data_blob) * 0.9:  # Only if 10%+ reduction
                    data_blob = compressed_blob
                    compressed = True
            
            # Calculate expiration
            expires_at = None
            if expires_in_hours:
                expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).isoformat()
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                # Insert or replace cache entry
                cursor = conn.execute('''
                    INSERT OR REPLACE INTO cache_entries 
                    (key, content_hash, data_type, compressed, created_at, accessed_at, 
                     expires_at, metadata, size_bytes)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?)
                ''', (
                    cache_key,
                    hashlib.sha256(data_blob).hexdigest(),
                    data_type,
                    compressed,
                    expires_at,
                    json.dumps(metadata) if metadata else None,
                    len(data_blob)
                ))
                
                cache_id = cursor.lastrowid
                
                # Store data blob
                conn.execute('''
                    INSERT OR REPLACE INTO cache_data (cache_id, data)
                    VALUES (?, ?)
                ''', (cache_id, data_blob))
                
                conn.commit()
                
            self.stats['stores'] += 1
            logger.debug(f"Cached data for key: {cache_key[:12]}... (size: {len(data_blob)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store cache entry {cache_key}: {e}")
            return False
    
    def delete(self, cache_key: str) -> bool:
        """Delete cache entry by key."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT id FROM cache_entries WHERE key = ?', (cache_key,))
                row = cursor.fetchone()
                
                if row:
                    cache_id = row[0]
                    self._delete_entry(cache_id)
                    self.stats['deletions'] += 1
                    return True
                    
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete cache entry {cache_key}: {e}")
            return False
    
    def _delete_entry(self, cache_id: int):
        """Delete cache entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM cache_entries WHERE id = ?', (cache_id,))
            conn.execute('DELETE FROM cache_data WHERE cache_id = ?', (cache_id,))
            conn.commit()    
    def clear_all(self) -> int:
        """Clear all cache entries and return count of deleted entries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM cache_entries')
                count = cursor.fetchone()[0]
                
                conn.execute('DELETE FROM cache_entries')
                conn.execute('DELETE FROM cache_data')
                conn.commit()
                
                self.stats['deletions'] += count
                logger.info(f"Cleared {count} cache entries")
                return count
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return 0
    
    def prune_expired(self) -> int:
        """Remove expired cache entries and return count of deleted entries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT COUNT(*) FROM cache_entries 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                ''', (datetime.now().isoformat(),))
                
                count = cursor.fetchone()[0]
                
                conn.execute('''
                    DELETE FROM cache_entries 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                ''', (datetime.now().isoformat(),))
                
                conn.commit()
                
                self.stats['deletions'] += count
                logger.info(f"Pruned {count} expired cache entries")
                return count
                
        except Exception as e:
            logger.error(f"Failed to prune expired entries: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total entries
                cursor = conn.execute('SELECT COUNT(*) FROM cache_entries')
                total_entries = cursor.fetchone()[0]
                
                # Total size
                cursor = conn.execute('SELECT SUM(size_bytes) FROM cache_entries')
                total_size = cursor.fetchone()[0] or 0
                
                # Entries by type
                cursor = conn.execute('''
                    SELECT data_type, COUNT(*), SUM(size_bytes)
                    FROM cache_entries 
                    GROUP BY data_type
                ''')
                by_type = {row[0]: {'count': row[1], 'size': row[2]} for row in cursor.fetchall()}
                
                # Recent activity
                cursor = conn.execute('''
                    SELECT COUNT(*) FROM cache_entries 
                    WHERE accessed_at > datetime('now', '-1 hour')
                ''')
                recent_access = cursor.fetchone()[0]
                
                # Hit rate calculation
                total_requests = self.stats['hits'] + self.stats['misses']
                hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
                
                return {
                    'total_entries': total_entries,
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'by_type': by_type,
                    'recent_access_count': recent_access,
                    'session_stats': self.stats.copy(),
                    'hit_rate_percent': round(hit_rate, 1),
                    'cache_directory': str(self.cache_dir),
                    'database_path': str(self.db_path)
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'error': str(e)}
    
    def cleanup_old_entries(self, days_old: int = 30) -> int:
        """Remove cache entries older than specified days."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT COUNT(*) FROM cache_entries 
                    WHERE created_at < ?
                ''', (cutoff_date,))
                
                count = cursor.fetchone()[0]
                
                conn.execute('''
                    DELETE FROM cache_entries 
                    WHERE created_at < ?
                ''', (cutoff_date,))
                
                conn.commit()
                
                self.stats['deletions'] += count
                logger.info(f"Cleaned up {count} old cache entries (>{days_old} days)")
                return count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old entries: {e}")
            return 0