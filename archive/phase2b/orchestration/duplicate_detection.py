#!/usr/bin/env python3
"""
S: Drive-Aware Duplicate Detection System

This module provides intelligent duplicate detection to avoid reprocessing
files that have already been downloaded or enhanced, with special handling
for S: drive coordination between platforms.
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import sqlite3
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class FileRecord:
    """Record of a processed file with metadata for duplicate detection."""
    file_path: str
    file_size: int
    file_hash: str
    url_source: Optional[str]
    download_timestamp: str
    enhancement_timestamp: Optional[str]
    enhanced_path: Optional[str]
    processing_status: str  # "downloaded", "enhanced", "failed"
    platform: str
    

class DuplicateDetectionManager:
    """
    Manages duplicate detection across scraper and processor operations.
    
    Uses both file-based tracking (for cross-platform compatibility) and
    SQLite database for efficient querying.
    """
    
    def __init__(self, base_working_dir: Path):
        self.base_working_dir = base_working_dir
        self.tracking_dir = base_working_dir / ".pipeline_tracking"
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        
        # File-based tracking for cross-platform compatibility
        self.manifest_file = self.tracking_dir / "file_manifest.json"
        
        # SQLite database for efficient querying
        self.db_file = self.tracking_dir / "duplicate_detection.db"
        
        self._init_database()
        self._load_manifest()
    
    def _init_database(self):
        """Initialize SQLite database for duplicate detection."""
        try:
            with sqlite3.connect(str(self.db_file)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS file_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT NOT NULL,
                        file_size INTEGER NOT NULL,
                        file_hash TEXT NOT NULL,
                        url_source TEXT,
                        download_timestamp TEXT NOT NULL,
                        enhancement_timestamp TEXT,
                        enhanced_path TEXT,
                        processing_status TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(file_path, file_hash)
                    )
                """)
                
                # Create indexes for efficient queries
                conn.execute("CREATE INDEX IF NOT EXISTS idx_file_hash ON file_records(file_hash)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_url_source ON file_records(url_source)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_processing_status ON file_records(processing_status)")
                
                conn.commit()
                logger.debug("Duplicate detection database initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize duplicate detection database: {e}")
    
    def _load_manifest(self):
        """Load existing file manifest for backwards compatibility."""
        try:
            if self.manifest_file.exists():
                with open(self.manifest_file, 'r') as f:
                    manifest_data = json.load(f)
                
                # Migrate manifest data to database if needed
                self._migrate_manifest_to_db(manifest_data)
                
        except Exception as e:
            logger.warning(f"Failed to load file manifest: {e}")
    
    def _migrate_manifest_to_db(self, manifest_data: Dict):
        """Migrate legacy manifest data to database."""
        try:
            with sqlite3.connect(str(self.db_file)) as conn:
                for file_path, record_data in manifest_data.items():
                    # Check if record already exists
                    existing = conn.execute(
                        "SELECT id FROM file_records WHERE file_path = ? AND file_hash = ?",
                        (file_path, record_data.get('file_hash', ''))
                    ).fetchone()
                    
                    if not existing:
                        # Insert migrated record
                        conn.execute("""
                            INSERT OR IGNORE INTO file_records 
                            (file_path, file_size, file_hash, url_source, download_timestamp, 
                             enhancement_timestamp, enhanced_path, processing_status, platform)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            file_path,
                            record_data.get('file_size', 0),
                            record_data.get('file_hash', ''),
                            record_data.get('url_source'),
                            record_data.get('download_timestamp', datetime.now().isoformat()),
                            record_data.get('enhancement_timestamp'),
                            record_data.get('enhanced_path'),
                            record_data.get('processing_status', 'unknown'),
                            record_data.get('platform', 'unknown')
                        ))
                
                conn.commit()
                logger.info("Successfully migrated manifest data to database")
                
        except Exception as e:
            logger.error(f"Failed to migrate manifest data: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file for duplicate detection."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def is_file_already_processed(self, file_path: Path, url_source: Optional[str] = None) -> Tuple[bool, Optional[FileRecord]]:
        """
        Check if a file has already been processed.
        
        Args:
            file_path: Path to the file to check
            url_source: Optional URL source for additional verification
            
        Returns:
            Tuple of (is_duplicate, existing_record)
        """
        try:
            if not file_path.exists():
                return False, None
            
            file_hash = self._calculate_file_hash(file_path)
            if not file_hash:
                return False, None
            
            with sqlite3.connect(str(self.db_file)) as conn:
                # Check by hash first (most reliable)
                result = conn.execute("""
                    SELECT file_path, file_size, file_hash, url_source, download_timestamp,
                           enhancement_timestamp, enhanced_path, processing_status, platform
                    FROM file_records 
                    WHERE file_hash = ? AND processing_status IN ('downloaded', 'enhanced')
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (file_hash,)).fetchone()
                
                if result:
                    record = FileRecord(
                        file_path=result[0],
                        file_size=result[1],
                        file_hash=result[2],
                        url_source=result[3],
                        download_timestamp=result[4],
                        enhancement_timestamp=result[5],
                        enhanced_path=result[6],
                        processing_status=result[7],
                        platform=result[8]
                    )
                    logger.info(f"Found duplicate file: {file_path.name} (hash: {file_hash[:8]}...)")
                    return True, record
                
                # Also check by URL source if provided
                if url_source:
                    result = conn.execute("""
                        SELECT file_path, file_size, file_hash, url_source, download_timestamp,
                               enhancement_timestamp, enhanced_path, processing_status, platform
                        FROM file_records 
                        WHERE url_source = ? AND processing_status IN ('downloaded', 'enhanced')
                        ORDER BY created_at DESC
                        LIMIT 1
                    """, (url_source,)).fetchone()
                    
                    if result:
                        record = FileRecord(
                            file_path=result[0],
                            file_size=result[1],
                            file_hash=result[2],
                            url_source=result[3],
                            download_timestamp=result[4],
                            enhancement_timestamp=result[5],
                            enhanced_path=result[6],
                            processing_status=result[7],
                            platform=result[8]
                        )
                        logger.info(f"Found duplicate URL source: {url_source}")
                        return True, record
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            return False, None
    
    def record_downloaded_file(self, file_path: Path, url_source: Optional[str] = None, platform: str = "unknown") -> bool:
        """Record a newly downloaded file."""
        try:
            if not file_path.exists():
                logger.warning(f"Cannot record non-existent file: {file_path}")
                return False
            
            file_size = file_path.stat().st_size
            file_hash = self._calculate_file_hash(file_path)
            
            if not file_hash:
                logger.warning(f"Cannot record file without hash: {file_path}")
                return False
            
            record = FileRecord(
                file_path=str(file_path),
                file_size=file_size,
                file_hash=file_hash,
                url_source=url_source,
                download_timestamp=datetime.now().isoformat(),
                enhancement_timestamp=None,
                enhanced_path=None,
                processing_status="downloaded",
                platform=platform
            )
            
            with sqlite3.connect(str(self.db_file)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO file_records 
                    (file_path, file_size, file_hash, url_source, download_timestamp, 
                     enhancement_timestamp, enhanced_path, processing_status, platform)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.file_path, record.file_size, record.file_hash,
                    record.url_source, record.download_timestamp,
                    record.enhancement_timestamp, record.enhanced_path,
                    record.processing_status, record.platform
                ))
                conn.commit()
            
            logger.debug(f"Recorded downloaded file: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record downloaded file {file_path}: {e}")
            return False
    
    def record_enhanced_file(self, original_path: Path, enhanced_path: Path, platform: str = "unknown") -> bool:
        """Record a newly enhanced file."""
        try:
            original_hash = self._calculate_file_hash(original_path) if original_path.exists() else ""
            
            with sqlite3.connect(str(self.db_file)) as conn:
                # Update existing record if found
                updated = conn.execute("""
                    UPDATE file_records 
                    SET enhancement_timestamp = ?, enhanced_path = ?, processing_status = ?
                    WHERE file_path = ? OR file_hash = ?
                """, (
                    datetime.now().isoformat(),
                    str(enhanced_path),
                    "enhanced",
                    str(original_path),
                    original_hash
                )).rowcount
                
                if updated == 0:
                    # Create new record if not found
                    enhanced_size = enhanced_path.stat().st_size if enhanced_path.exists() else 0
                    enhanced_hash = self._calculate_file_hash(enhanced_path) if enhanced_path.exists() else ""
                    
                    conn.execute("""
                        INSERT INTO file_records 
                        (file_path, file_size, file_hash, download_timestamp, 
                         enhancement_timestamp, enhanced_path, processing_status, platform)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(original_path),
                        original_path.stat().st_size if original_path.exists() else 0,
                        original_hash,
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        str(enhanced_path),
                        "enhanced",
                        platform
                    ))
                
                conn.commit()
            
            logger.debug(f"Recorded enhanced file: {original_path.name} -> {enhanced_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record enhanced file {original_path}: {e}")
            return False
    
    def get_files_needing_enhancement(self) -> List[FileRecord]:
        """Get list of downloaded files that haven't been enhanced yet."""
        try:
            with sqlite3.connect(str(self.db_file)) as conn:
                results = conn.execute("""
                    SELECT file_path, file_size, file_hash, url_source, download_timestamp,
                           enhancement_timestamp, enhanced_path, processing_status, platform
                    FROM file_records 
                    WHERE processing_status = 'downloaded'
                    ORDER BY download_timestamp DESC
                """).fetchall()
                
                records = []
                for result in results:
                    record = FileRecord(
                        file_path=result[0],
                        file_size=result[1],
                        file_hash=result[2],
                        url_source=result[3],
                        download_timestamp=result[4],
                        enhancement_timestamp=result[5],
                        enhanced_path=result[6],
                        processing_status=result[7],
                        platform=result[8]
                    )
                    # Verify file still exists
                    if Path(record.file_path).exists():
                        records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"Failed to get files needing enhancement: {e}")
            return []
    
    def get_processing_statistics(self) -> Dict:
        """Get statistics about processed files."""
        try:
            with sqlite3.connect(str(self.db_file)) as conn:
                stats = {}
                
                # Count by status
                status_counts = conn.execute("""
                    SELECT processing_status, COUNT(*) 
                    FROM file_records 
                    GROUP BY processing_status
                """).fetchall()
                
                for status, count in status_counts:
                    stats[f"{status}_count"] = count
                
                # Total counts
                stats["total_files"] = sum(stats.values())
                
                # Platform breakdown
                platform_counts = conn.execute("""
                    SELECT platform, COUNT(*) 
                    FROM file_records 
                    GROUP BY platform
                """).fetchall()
                
                stats["by_platform"] = dict(platform_counts)
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get processing statistics: {e}")
            return {}
    
    def cleanup_stale_records(self, max_age_days: int = 30) -> int:
        """Remove records for files that no longer exist or are very old."""
        try:
            removed_count = 0
            
            with sqlite3.connect(str(self.db_file)) as conn:
                # Get all records
                records = conn.execute("""
                    SELECT id, file_path, enhanced_path 
                    FROM file_records
                """).fetchall()
                
                for record_id, file_path, enhanced_path in records:
                    should_remove = False
                    
                    # Check if original file exists
                    if file_path and not Path(file_path).exists():
                        should_remove = True
                    
                    # Check if enhanced file exists (if specified)
                    if enhanced_path and not Path(enhanced_path).exists():
                        should_remove = True
                    
                    if should_remove:
                        conn.execute("DELETE FROM file_records WHERE id = ?", (record_id,))
                        removed_count += 1
                
                conn.commit()
                
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} stale records")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup stale records: {e}")
            return 0