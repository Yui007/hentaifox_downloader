"""Base site class for manga downloading sites."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re


@dataclass
class GalleryInfo:
    """Information about a manga gallery."""
    id: str
    title: str
    url: str
    tags: List[str]
    artist: Optional[str] = None
    pages: Optional[int] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SearchResult:
    """Search results from a site."""
    galleries: List[GalleryInfo]
    total_count: int
    current_page: int
    total_pages: int
    has_next: bool


class BaseSite(ABC):
    """Abstract base class for manga sites."""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.rate_limit = 1.0  # seconds between requests
    
    @abstractmethod
    def is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to this site."""
        pass
    
    @abstractmethod
    def extract_gallery_id(self, url: str) -> Optional[str]:
        """Extract gallery ID from URL."""
        pass
    
    @abstractmethod
    def get_gallery_info(self, url: str) -> Optional[GalleryInfo]:
        """Get gallery information from URL."""
        pass
    
    @abstractmethod
    def search(self, query: str, page: int = 1) -> Optional[SearchResult]:
        """Search for galleries."""
        pass
    
    @abstractmethod
    def get_tag_galleries(self, tag: str, page: int = 1) -> Optional[SearchResult]:
        """Get galleries by tag."""
        pass
    
    def get_gallery_dl_config(self) -> Dict[str, Any]:
        """Get gallery-dl configuration for this site."""
        return {
            "extractor": {
                self.name: {
                    "sleep": self.rate_limit,
                }
            }
        }
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL format for consistency."""
        # Remove trailing slashes and fragments
        url = url.rstrip('/').split('#')[0].split('?')[0]
        return url
    
    def validate_gallery_url(self, url: str) -> bool:
        """Validate that URL is a valid gallery URL."""
        return self.is_valid_url(url) and self.extract_gallery_id(url) is not None