"""Search worker for background searching."""

from PyQt6.QtCore import QObject, pyqtSignal

from core.sites.hentaifox import HentaiFoxSite


class SearchWorker(QObject):
    """Worker for handling search operations in background thread."""
    
    # Signals
    search_completed = pyqtSignal(list, int)  # results, total_pages
    search_error = pyqtSignal(str)  # error_message
    finished = pyqtSignal()
    
    def __init__(self, query: str, options: dict):
        super().__init__()
        self.query = query
        self.options = options
        self.cancelled = False
        
        # Initialize site
        self.site = HentaiFoxSite()
    
    def start_search(self):
        """Start the search process."""
        try:
            if self.cancelled:
                self.finished.emit()
                return
            
            # Perform search based on type
            search_type = self.options.get('search_type', 'all')
            page = self.options.get('page', 1)
            per_page = self.options.get('per_page', 20)
            sort_by = self.options.get('sort_by', 'newest')
            
            # Use the available search method - handle empty query for browsing
            results = self.site.search(self.query, page=page, sort_by=sort_by, search_type=search_type)
            
            if self.cancelled:
                self.finished.emit()
                return
            
            if results and results.galleries:
                # Convert SearchResult to gallery info format
                gallery_list = []
                for gallery in results.galleries:
                    gallery_info = {
                        'id': gallery.id,
                        'title': gallery.title,
                        'url': gallery.url,
                        'artist': getattr(gallery, 'artist', 'Unknown Artist'),
                        'pages': getattr(gallery, 'pages', 0),
                        'tags': getattr(gallery, 'tags', []),
                        'thumbnail': getattr(gallery, 'thumbnail', ''),
                        'rating': getattr(gallery, 'rating', 0),
                        'views': getattr(gallery, 'views', 0)
                    }
                    gallery_list.append(gallery_info)
                
                total_pages = getattr(results, 'total_pages', 1)
                self.search_completed.emit(gallery_list, total_pages)
            else:
                self.search_completed.emit([], 1)
                
        except Exception as e:
            self.search_error.emit(str(e))
        finally:
            self.finished.emit()
    
    def cancel(self):
        """Cancel the search operation."""
        self.cancelled = True