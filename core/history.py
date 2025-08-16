"""Download history and library management."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

from config.settings import config
from .sites.base import GalleryInfo


@dataclass
class HistoryEntry:
    """A download history entry."""
    id: int
    gallery_id: str
    title: str
    url: str
    download_path: str
    downloaded_at: str
    files_count: int
    site: str
    metadata: Optional[Dict[str, Any]] = None


class HistoryManager:
    """Manages download history using SQLite."""
    
    def __init__(self):
        self.db_path = Path(config.get("history.database_path"))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the history database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gallery_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    download_path TEXT NOT NULL,
                    downloaded_at TEXT NOT NULL,
                    files_count INTEGER NOT NULL,
                    site TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_gallery_id ON downloads(gallery_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_site ON downloads(site)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_downloaded_at ON downloads(downloaded_at)")
    
    def add_download(
        self,
        gallery_info: GalleryInfo,
        download_path: str,
        files_count: int,
        site: str = "hentaifox"
    ) -> int:
        """Add a download to history."""
        
        # Check if already exists
        if self.is_downloaded(gallery_info.id, site):
            return self.get_download_id(gallery_info.id, site)
        
        metadata_json = None
        if gallery_info.metadata:
            metadata_json = json.dumps(gallery_info.metadata)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO downloads 
                (gallery_id, title, url, download_path, downloaded_at, files_count, site, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gallery_info.id,
                gallery_info.title,
                gallery_info.url,
                download_path,
                datetime.now().isoformat(),
                files_count,
                site,
                metadata_json
            ))
            return cursor.lastrowid
    
    def is_downloaded(self, gallery_id: str, site: str = "hentaifox") -> bool:
        """Check if a gallery has been downloaded."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM downloads WHERE gallery_id = ? AND site = ?",
                (gallery_id, site)
            )
            return cursor.fetchone()[0] > 0
    
    def get_download_id(self, gallery_id: str, site: str = "hentaifox") -> Optional[int]:
        """Get the download ID for a gallery."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM downloads WHERE gallery_id = ? AND site = ? ORDER BY downloaded_at DESC LIMIT 1",
                (gallery_id, site)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_recent_downloads(self, limit: int = 50) -> List[HistoryEntry]:
        """Get recent downloads."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, gallery_id, title, url, download_path, downloaded_at, files_count, site, metadata
                FROM downloads 
                ORDER BY downloaded_at DESC 
                LIMIT ?
            """, (limit,))
            
            entries = []
            for row in cursor.fetchall():
                metadata = None
                if row[8]:
                    try:
                        metadata = json.loads(row[8])
                    except json.JSONDecodeError:
                        pass
                
                entries.append(HistoryEntry(
                    id=row[0],
                    gallery_id=row[1],
                    title=row[2],
                    url=row[3],
                    download_path=row[4],
                    downloaded_at=row[5],
                    files_count=row[6],
                    site=row[7],
                    metadata=metadata
                ))
            
            return entries
    
    def search_history(self, query: str, limit: int = 50) -> List[HistoryEntry]:
        """Search download history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, gallery_id, title, url, download_path, downloaded_at, files_count, site, metadata
                FROM downloads 
                WHERE title LIKE ? OR gallery_id LIKE ?
                ORDER BY downloaded_at DESC 
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            entries = []
            for row in cursor.fetchall():
                metadata = None
                if row[8]:
                    try:
                        metadata = json.loads(row[8])
                    except json.JSONDecodeError:
                        pass
                
                entries.append(HistoryEntry(
                    id=row[0],
                    gallery_id=row[1],
                    title=row[2],
                    url=row[3],
                    download_path=row[4],
                    downloaded_at=row[5],
                    files_count=row[6],
                    site=row[7],
                    metadata=metadata
                ))
            
            return entries
    
    def get_stats(self) -> Dict[str, Any]:
        """Get download statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Total downloads
            cursor = conn.execute("SELECT COUNT(*) FROM downloads")
            total_downloads = cursor.fetchone()[0]
            
            # Total files
            cursor = conn.execute("SELECT SUM(files_count) FROM downloads")
            total_files = cursor.fetchone()[0] or 0
            
            # Downloads by site
            cursor = conn.execute("SELECT site, COUNT(*) FROM downloads GROUP BY site")
            by_site = dict(cursor.fetchall())
            
            # Recent activity (last 7 days)
            cursor = conn.execute("""
                SELECT COUNT(*) FROM downloads 
                WHERE downloaded_at >= datetime('now', '-7 days')
            """)
            recent_downloads = cursor.fetchone()[0]
            
            return {
                "total_downloads": total_downloads,
                "total_files": total_files,
                "by_site": by_site,
                "recent_downloads": recent_downloads
            }
    
    def cleanup_old_entries(self, max_entries: Optional[int] = None):
        """Clean up old history entries."""
        if max_entries is None:
            max_entries = config.get("history.max_history_entries", 10000)
        
        with sqlite3.connect(self.db_path) as conn:
            # Count current entries
            cursor = conn.execute("SELECT COUNT(*) FROM downloads")
            current_count = cursor.fetchone()[0]
            
            if current_count > max_entries:
                # Delete oldest entries
                entries_to_delete = current_count - max_entries
                conn.execute("""
                    DELETE FROM downloads 
                    WHERE id IN (
                        SELECT id FROM downloads 
                        ORDER BY downloaded_at ASC 
                        LIMIT ?
                    )
                """, (entries_to_delete,))
    
    def clear_history(self):
        """Clear all download history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM downloads")
            conn.commit()


# Global history manager instance
history = HistoryManager()