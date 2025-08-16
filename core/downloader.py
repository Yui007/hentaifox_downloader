"""Gallery-dl wrapper for downloading manga."""

import os
import json
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from config.settings import config
from config.performance import ARIA2_HIGH_PERFORMANCE, GALLERY_DL_PERFORMANCE
from .sites.base import GalleryInfo
from .history import history


@dataclass
class DownloadResult:
    """Result of a download operation."""
    success: bool
    gallery_info: Optional[GalleryInfo]
    download_path: Optional[Path]
    files_downloaded: int
    error_message: Optional[str] = None


class GalleryDLDownloader:
    """Wrapper for gallery-dl with custom configuration."""
    
    def __init__(self):
        self.progress_callback: Optional[Callable] = None
        self.aria2_available = self._check_aria2_available()
        self.base_config = self._get_base_config()
    
    def _get_base_config(self) -> Dict[str, Any]:
        """Get base gallery-dl configuration."""
        download_path = config.get("download.base_path")
        
        base_config = {
            "extractor": {
                "base-directory": download_path,
                **GALLERY_DL_PERFORMANCE,
                "retries": config.get("download.retry_attempts", 2),
            }
        }
        
        # Add Aria2c configuration if available and enabled
        if config.get("download.use_aria2", True) and self.aria2_available:
            base_config["downloader"] = {
                "aria2": ARIA2_HIGH_PERFORMANCE
            }
        
        return base_config
    
    def set_progress_callback(self, callback: Callable[[str, int, int], None]):
        """Set callback for progress updates."""
        self.progress_callback = callback
    
    def download_gallery(self, url: str, gallery_info: Optional[GalleryInfo] = None) -> DownloadResult:
        """Download a single gallery."""
        try:
            # Create temporary config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                config_data = self._prepare_config(gallery_info)
                json.dump(config_data, f, indent=2)
                config_file = f.name
            
            # Prepare gallery-dl command
            cmd = ["gallery-dl", "--config", config_file]
            
            # Add verbose flag for debugging
            if config.get("display.log_level") == "DEBUG":
                cmd.append("--verbose")
            
            # Add the URL
            cmd.append(url)
            
            # Execute gallery-dl
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            # Clean up temp config
            os.unlink(config_file)
            
            if result.returncode == 0:
                # Parse output to get download info
                download_path = self._extract_download_path(result.stdout)
                files_count = self._count_downloaded_files(result.stdout)
                
                # Add to history if enabled and gallery info is available
                if config.get("history.enable_history", True) and gallery_info and download_path:
                    history.add_download(
                        gallery_info=gallery_info,
                        download_path=str(download_path),
                        files_count=files_count,
                        site="hentaifox"
                    )
                
                return DownloadResult(
                    success=True,
                    gallery_info=gallery_info,
                    download_path=download_path,
                    files_downloaded=files_count
                )
            else:
                return DownloadResult(
                    success=False,
                    gallery_info=gallery_info,
                    download_path=None,
                    files_downloaded=0,
                    error_message=result.stderr
                )
                
        except subprocess.TimeoutExpired:
            return DownloadResult(
                success=False,
                gallery_info=gallery_info,
                download_path=None,
                files_downloaded=0,
                error_message="Download timed out"
            )
        except Exception as e:
            return DownloadResult(
                success=False,
                gallery_info=gallery_info,
                download_path=None,
                files_downloaded=0,
                error_message=str(e)
            )
    
    def download_multiple(self, urls: List[str]) -> List[DownloadResult]:
        """Download multiple galleries with parallel processing."""
        results = []
        max_workers = config.get("download.max_parallel_galleries", 2)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_url = {
                executor.submit(self.download_gallery, url): url 
                for url in urls
            }
            
            # Process completed downloads
            for i, future in enumerate(as_completed(future_to_url)):
                url = future_to_url[future]
                
                if self.progress_callback:
                    self.progress_callback(f"Completed {i+1}/{len(urls)}", i+1, len(urls))
                
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Create failed result
                    results.append(DownloadResult(
                        success=False,
                        gallery_info=None,
                        download_path=None,
                        files_downloaded=0,
                        error_message=str(e)
                    ))
        
        return results
    
    def _prepare_config(self, gallery_info: Optional[GalleryInfo] = None) -> Dict[str, Any]:
        """Prepare gallery-dl config with custom settings."""
        config_data = self.base_config.copy()
        
        # Set directory structure - use title from gallery-dl's variables if no gallery_info
        if gallery_info:
            safe_title = self._sanitize_filename(gallery_info.title)
            config_data["extractor"]["directory"] = [safe_title]
        else:
            # Use gallery-dl's built-in title variable instead of category_id
            config_data["extractor"]["directory"] = ["{title}"]
        
        # Set filename pattern - use gallery-dl's default variables
        config_data["extractor"]["filename"] = "{filename}.{extension}"
        
        return config_data
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200] + "..."
        
        return filename.strip()
    
    def _extract_download_path(self, output: str) -> Optional[Path]:
        """Extract download path from gallery-dl output."""
        lines = output.split('\n')
        for line in lines:
            # Look for file paths in the output
            if 'Downloads' in line and any(ext in line for ext in ['.webp', '.jpg', '.png', '.gif']):
                # Extract directory from file path
                file_path = Path(line.strip())
                return file_path.parent
        
        return None
    
    def _count_downloaded_files(self, output: str) -> int:
        """Count downloaded files from gallery-dl output."""
        lines = output.split('\n')
        count = 0
        
        for line in lines:
            # Count lines that show downloaded file paths
            if any(ext in line for ext in ['.webp', '.jpg', '.png', '.gif']) and \
               'Downloads' in line and \
               not any(skip in line.lower() for skip in ['error', 'failed', 'skipping']):
                count += 1
        
        return count
    
    def check_gallery_dl_available(self) -> bool:
        """Check if gallery-dl is available in PATH."""
        try:
            result = subprocess.run(
                ["gallery-dl", "--version"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_aria2_available(self) -> bool:
        """Check if aria2c is available in PATH."""
        try:
            aria2_path = config.get("download.aria2_path", "aria2c")
            result = subprocess.run(
                [aria2_path, "--version"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _track_download_progress(self, process: subprocess.Popen, total_files: int = 0):
        """Track download progress in real-time."""
        if not self.progress_callback:
            return
        
        downloaded_count = 0
        while process.poll() is None:
            time.sleep(0.5)
            
            # Try to count downloaded files by checking output
            try:
                # This is a simple approach - in practice you'd parse gallery-dl's output
                if total_files > 0:
                    progress = min(downloaded_count / total_files * 100, 99)
                    self.progress_callback(f"Downloading... {downloaded_count}/{total_files}", progress, 100)
                    downloaded_count += 1
            except:
                pass