"""HentaiFox site implementation."""

import re
import requests
from typing import Optional, List
from bs4 import BeautifulSoup
from .base import BaseSite, GalleryInfo, SearchResult


class HentaiFoxSite(BaseSite):
    """HentaiFox site implementation."""
    
    def __init__(self):
        super().__init__("hentaifox", "https://hentaifox.com")
        self.gallery_pattern = re.compile(r'hentaifox\.com/gallery/(\d+)')
        self.tag_pattern = re.compile(r'hentaifox\.com/tag/([^/]+)')
        self.search_pattern = re.compile(r'hentaifox\.com/search')
        
        # Create persistent session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to HentaiFox."""
        return "hentaifox.com" in url.lower()
    
    def extract_gallery_id(self, url: str) -> Optional[str]:
        """Extract gallery ID from HentaiFox URL."""
        match = self.gallery_pattern.search(url)
        return match.group(1) if match else None
    
    def get_gallery_info(self, url: str) -> Optional[GalleryInfo]:
        """Get gallery information from HentaiFox URL."""
        gallery_id = self.extract_gallery_id(url)
        if not gallery_id:
            return None
        
        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.get_text().strip() if title_elem else f"Gallery {gallery_id}"
            
            # Extract tags
            tags = []
            tag_elements = soup.find_all('a', href=re.compile(r'/tag/'))
            for tag_elem in tag_elements:
                tag_text = tag_elem.get_text().strip()
                if tag_text:
                    tags.append(tag_text)
            
            # Extract artist
            artist = None
            artist_elem = soup.find('a', href=re.compile(r'/artist/'))
            if artist_elem:
                artist = artist_elem.get_text().strip()
            
            # Extract page count
            pages = None
            
            # Look for the specific HentaiFox page count element
            page_elem = soup.find('span', class_='i_text pages')
            if page_elem:
                page_text = page_elem.get_text().strip()
                # Extract number from "Pages: 49" format
                page_match = re.search(r'Pages:\s*(\d+)', page_text)
                if page_match:
                    pages = int(page_match.group(1))
            
            # Extract thumbnail
            thumbnail_url = None
            thumb_elem = soup.find('img', class_='cover')
            if thumb_elem and thumb_elem.get('src'):
                thumbnail_url = thumb_elem['src']
                if not thumbnail_url.startswith('http'):
                    thumbnail_url = self.base_url + thumbnail_url
            
            return GalleryInfo(
                id=gallery_id,
                title=title,
                url=url,
                tags=tags,
                artist=artist,
                pages=pages,
                thumbnail_url=thumbnail_url
            )
            
        except Exception as e:
            return None
    
    def search(self, query: str, page: int = 1, sort_by: str = "newest", search_type: str = "all") -> Optional[SearchResult]:
        """Search for galleries on HentaiFox."""
        try:
            if query.strip():
                # Determine search URL based on search type
                if search_type == "tag":
                    # Search by tag - normalize the tag name
                    # Convert to lowercase and replace spaces with hyphens
                    tag_name = query.lower().strip().replace(' ', '-').replace('_', '-')
                    search_url = f"{self.base_url}/tag/{tag_name}/"
                    params = {'page': page} if page > 1 else {}
                elif search_type == "artist":
                    # Search by artist - normalize the artist name
                    # Convert to lowercase and replace spaces with hyphens
                    artist_name = query.lower().strip().replace(' ', '-').replace('_', '-')
                    search_url = f"{self.base_url}/artist/{artist_name}/"
                    params = {'page': page} if page > 1 else {}
                elif search_type == "title":
                    # Search in titles only
                    search_url = f"{self.base_url}/search/"
                    params = {'q': query, 'page': page, 'type': 'title'}
                else:
                    # Default "all" search
                    search_url = f"{self.base_url}/search/"
                    params = {'q': query, 'page': page}
                
                # Add sort parameter if supported (for regular search)
                if search_type in ["all", "title"]:
                    if sort_by == "popular":
                        params['sort'] = 'popular'
                    elif sort_by == "most viewed":
                        params['sort'] = 'views'
                    elif sort_by == "rating":
                        params['sort'] = 'rating'
                
            else:
                # Browse mode - get galleries by sort order
                if sort_by == "popular":
                    search_url = f"{self.base_url}/popular/"
                elif sort_by == "most viewed":
                    search_url = f"{self.base_url}/most-viewed/"
                else:
                    # Default to latest/newest
                    search_url = f"{self.base_url}/"
                
                params = {'page': page} if page > 1 else {}
            
            response = self.session.get(search_url, params=params, timeout=5)
            
            # If tag/artist URL returns 404, fallback to regular search
            if response.status_code == 404 and search_type in ["tag", "artist"]:
                search_url = f"{self.base_url}/search/"
                # Try different search formats
                if search_type == "tag":
                    params = {'q': f"tag:{query}", 'page': page}
                else:
                    params = {'q': f"artist:{query}", 'page': page}
                response = self.session.get(search_url, params=params, timeout=5)
                
                # If that doesn't work, try just the query itself
                if response.status_code != 200:
                    params = {'q': query, 'page': page}
                    response = self.session.get(search_url, params=params, timeout=5)
            
            response.raise_for_status()
            
            return self._parse_gallery_list(response.content, page)
            
        except Exception as e:
            return None
    
    def get_tag_galleries(self, tag: str, page: int = 1) -> Optional[SearchResult]:
        """Get galleries by tag from HentaiFox."""
        try:
            tag_url = f"{self.base_url}/tag/{tag}/"
            params = {'page': page} if page > 1 else {}
            
            response = self.session.get(tag_url, params=params, timeout=5)
            response.raise_for_status()
            
            return self._parse_gallery_list(response.content, page)
            
        except Exception as e:
            return None
    
    def _parse_gallery_list(self, html_content: bytes, current_page: int) -> SearchResult:
        """Parse HTML content to extract gallery list."""
        soup = BeautifulSoup(html_content, 'html.parser')
        galleries = []
        
        # Find gallery items (adjust selector based on actual HTML structure)
        gallery_items = soup.find_all('div', class_='thumb')
        
        for item in gallery_items:
            try:
                # Extract gallery URL and ID - look specifically in inner_thumb for gallery links
                inner_thumb = item.find('div', class_='inner_thumb')
                if not inner_thumb:
                    continue
                
                link_elem = inner_thumb.find('a', href=lambda x: x and '/gallery/' in x)
                if not link_elem or not link_elem.get('href'):
                    continue
                
                gallery_url = link_elem['href']
                if not gallery_url.startswith('http'):
                    gallery_url = self.base_url + gallery_url
                
                gallery_id = self.extract_gallery_id(gallery_url)
                if not gallery_id:
                    continue
                
                # Extract title from caption
                title_elem = item.find('div', class_='caption')
                title = f"Gallery {gallery_id}"  # Default title
                
                if title_elem:
                    # Try to get title from h2.g_title > a text
                    title_link = title_elem.find('h2', class_='g_title')
                    if title_link:
                        title_a = title_link.find('a')
                        if title_a:
                            title = title_a.get_text().strip()
                        else:
                            title = title_link.get_text().strip()
                    else:
                        # Fallback to any text in caption
                        title = title_elem.get_text().strip()
                
                # Extract thumbnail - use data-src if available (lazy loading)
                img_elem = inner_thumb.find('img')
                thumbnail_url = None
                if img_elem:
                    thumbnail_url = img_elem.get('data-src') or img_elem.get('src')
                    if thumbnail_url and not thumbnail_url.startswith('http'):
                        thumbnail_url = self.base_url + thumbnail_url
                
                galleries.append(GalleryInfo(
                    id=gallery_id,
                    title=title,
                    url=gallery_url,
                    tags=[],  # Tags not available in list view
                    thumbnail_url=thumbnail_url
                ))
                
            except Exception as e:
                continue
        
        # Extract pagination info
        total_pages = 1
        has_next = False
        
        # Look for pagination in different possible locations
        pagination = soup.find('div', class_='pagination') or soup.find('ul', class_='pagination') or soup.find('div', class_='pager')
        
        if pagination:
            # Look for page links
            page_links = pagination.find_all('a')
            page_numbers = []
            
            for link in page_links:
                link_text = link.get_text().strip()
                
                # Try to extract page number
                try:
                    # Handle different formats like "2", "Next", "Last", etc.
                    if link_text.isdigit():
                        page_numbers.append(int(link_text))
                    elif 'page=' in link.get('href', ''):
                        # Extract from URL parameter
                        import re
                        match = re.search(r'page=(\d+)', link.get('href', ''))
                        if match:
                            page_numbers.append(int(match.group(1)))
                except (ValueError, AttributeError):
                    continue
            
            if page_numbers:
                total_pages = max(page_numbers)
            else:
                # Fallback: look for "Next" button to determine if there are more pages
                next_links = pagination.find_all('a', string=lambda text: text and ('next' in text.lower() or '>' in text))
                if next_links:
                    total_pages = current_page + 1  # At least one more page
        
        # Alternative: look for page info text like "Page 1 of 25"
        if total_pages == 1:
            page_info = soup.find(string=lambda text: text and 'page' in text.lower() and 'of' in text.lower())
            if page_info:
                import re
                match = re.search(r'page\s+\d+\s+of\s+(\d+)', page_info.lower())
                if match:
                    total_pages = int(match.group(1))
        
        # If we still have only 1 page but found 20 results, assume there are more pages
        if total_pages == 1 and len(galleries) >= 20:
            total_pages = 10  # Conservative estimate
        
        has_next = current_page < total_pages
        
        return SearchResult(
            galleries=galleries,
            total_count=len(galleries) * total_pages,  # Rough estimate
            current_page=current_page,
            total_pages=total_pages,
            has_next=has_next
        )