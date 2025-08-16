"""Default configuration settings for HFox Downloader."""

import os
from pathlib import Path

# Default configuration values
DEFAULT_CONFIG = {
    "download": {
        "base_path": str(Path.home() / "Downloads" / "HFox"),
        "create_subfolders": True,
        "folder_template": "{title}",
        "filename_template": "{page:03d}.{ext}",
        "max_concurrent": 8,
        "retry_attempts": 3,
        "use_aria2": True,
        "aria2_path": "aria2c",
        "max_parallel_galleries": 3,
        "max_connections_per_server": 8,
    },
    "metadata": {
        "save_metadata": True,
        "metadata_format": "json",  # json, yaml, csv
        "include_tags": True,
        "include_artist": True,
        "include_description": True,
    },
    "history": {
        "enable_history": True,
        "database_path": str(Path.home() / ".hfox" / "history.db"),
        "max_history_entries": 10000,
    },
    "display": {
        "show_progress": True,
        "use_colors": True,
        "progress_style": "bar",  # bar, spinner, dots
        "log_level": "INFO",
    },
    "conversion": {
        "auto_convert": False,  # Automatically convert after download
        "default_format": "none",  # none, pdf, cbz
        "delete_source_after_conversion": False,
        "pdf_quality": 100,  # JPEG quality for PDF images (1-100)
        "max_image_width": 2048,  # Max width for PDF images
        "cbz_compression": 6,  # ZIP compression level (0-9)
        "cbz_quality": 100,  # JPEG quality for CBZ optimization
        "max_cbz_width": 1920,  # Max width for CBZ images
        "optimize_cbz_images": False,  # Optimize images in CBZ
    },
    "sites": {
        "hentaifox": {
            "enabled": True,
            "base_url": "https://hentaifox.com",
            "rate_limit": 1.0,  # seconds between requests
        }
    }
}

# Config file locations
CONFIG_DIRS = [
    Path.home() / ".hfox",
    Path.home() / ".config" / "hfox",
    Path.cwd() / ".hfox",
]

CONFIG_FILENAME = "config.yaml"