"""Search tab for browsing and searching galleries."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                            QScrollArea, QLabel, QComboBox, QSpinBox, QFrame,
                            QGridLayout, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont

# Removed theme manager - using simple styling
from gui.widgets.modern_button import ModernButton
from gui.widgets.gallery_card import GalleryCard
from gui.workers.search_worker import SearchWorker


class SearchTab(QWidget):
    """Search tab for finding and browsing galleries."""
    
    download_requested = pyqtSignal(str)  # gallery_url
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Using simple black theme
        self.search_results = []
        self.current_page = 1
        self.total_pages = 1
        self.search_worker = None
        self.search_thread = None
        
        self.setup_ui()
        self.apply_styling()
    
    def setup_ui(self):
        """Setup the search tab UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("🔍 Search & Browse")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(header_label)
        
        # Search section
        self.setup_search_section(layout)
        
        # Results section
        self.setup_results_section(layout)
        
        layout.addStretch()
    
    def setup_search_section(self, parent_layout):
        """Setup search input section."""
        group = QGroupBox("Search Options")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        # Search input
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search galleries, tags, artists...")
        self.search_input.setFont(QFont("Segoe UI", 10))
        self.search_input.returnPressed.connect(self.start_search)
        search_layout.addWidget(self.search_input)
        
        self.search_button = ModernButton("Search", button_type="primary")
        self.search_button.clicked.connect(self.start_search)
        search_layout.addWidget(self.search_button)
        
        layout.addLayout(search_layout)
        
        # Search options
        options_layout = QHBoxLayout()
        
        # Search type
        options_layout.addWidget(QLabel("Type:"))
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["All", "Title", "Tag", "Artist"])
        options_layout.addWidget(self.search_type_combo)
        
        # Sort by
        options_layout.addWidget(QLabel("Sort by:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Newest", "Popular", "Most Viewed", "Rating"])
        options_layout.addWidget(self.sort_combo)
        
        # Results per page
        options_layout.addWidget(QLabel("Per page:"))
        self.per_page_spin = QSpinBox()
        self.per_page_spin.setRange(10, 100)
        self.per_page_spin.setValue(20)
        self.per_page_spin.setSingleStep(10)
        options_layout.addWidget(self.per_page_spin)
        
        options_layout.addStretch()
        
        # Quick search buttons
        self.popular_button = ModernButton("Popular")
        self.popular_button.clicked.connect(lambda: self.quick_search("popular"))
        options_layout.addWidget(self.popular_button)
        
        self.recent_button = ModernButton("Recent")
        self.recent_button.clicked.connect(lambda: self.quick_search("recent"))
        options_layout.addWidget(self.recent_button)
        
        layout.addLayout(options_layout)
        
        parent_layout.addWidget(group)
    
    def setup_results_section(self, parent_layout):
        """Setup search results section."""
        group = QGroupBox("Search Results")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QVBoxLayout(group)
        
        # Results info and pagination
        info_layout = QHBoxLayout()
        
        self.results_info_label = QLabel("No search performed")
        self.results_info_label.setFont(QFont("Segoe UI", 9))
        self.results_info_label.setStyleSheet("color: #b3b3b3;")
        info_layout.addWidget(self.results_info_label)
        
        info_layout.addStretch()
        
        # Pagination controls
        self.prev_button = ModernButton("← Previous")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setEnabled(False)
        info_layout.addWidget(self.prev_button)
        
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setFont(QFont("Segoe UI", 9))
        self.page_label.setStyleSheet("color: #b3b3b3;")
        info_layout.addWidget(self.page_label)
        
        self.next_button = ModernButton("Next →")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        info_layout.addWidget(self.next_button)
        
        layout.addLayout(info_layout)
        
        # Results scroll area
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_scroll.setMinimumHeight(400)
        
        self.results_widget = QWidget()
        self.results_layout = QGridLayout(self.results_widget)
        self.results_layout.setSpacing(16)
        
        self.results_scroll.setWidget(self.results_widget)
        layout.addWidget(self.results_scroll)
        
        # Empty state
        self.empty_label = QLabel("🔍 Enter a search term to find galleries")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setFont(QFont("Segoe UI", 12))
        self.empty_label.setStyleSheet("color: #b3b3b3;")
        layout.addWidget(self.empty_label)
        
        # Loading state
        self.loading_label = QLabel("🔄 Searching...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setFont(QFont("Segoe UI", 12))
        self.loading_label.setStyleSheet("color: #bb86fc;")
        self.loading_label.hide()
        layout.addWidget(self.loading_label)
        
        parent_layout.addWidget(group)
    
    def apply_styling(self):
        """Apply beautiful modern styling."""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 12px;
                border: 1px solid #4B5563;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1F2937, stop:1 #111827);
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 12px 0 12px;
                color: #8B5CF6;
                font-weight: 700;
                font-size: 13px;
            }
            
            QLabel {
                color: #F8FAFC;
                font-size: 11px;
                font-weight: 500;
            }
            
            QScrollArea {
                border: 1px solid #4B5563;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #111827, stop:1 #0F172A);
            }
            
            QScrollBar:vertical {
                background: #1F2937;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6, stop:1 #7C3AED);
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #A855F7, stop:1 #8B5CF6);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def start_search(self):
        """Start searching with current parameters."""
        query = self.search_input.text().strip()
        if not query:
            return
        
        self.current_page = 1
        self.perform_search(query, self.current_page)
    
    def perform_search(self, query: str, page: int):
        """Perform search with given parameters."""
        # Cancel existing search safely
        try:
            if hasattr(self, 'search_thread') and self.search_thread:
                if self.search_thread.isRunning():
                    if hasattr(self, 'search_worker') and self.search_worker:
                        self.search_worker.cancel()
                    self.search_thread.quit()
                    self.search_thread.wait()
        except RuntimeError:
            # Thread was already deleted, ignore
            pass
        
        # Show loading state
        self.show_loading_state()
        
        # Create search worker
        search_options = {
            'search_type': self.search_type_combo.currentText().lower(),
            'sort_by': self.sort_combo.currentText().lower(),
            'per_page': self.per_page_spin.value(),
            'page': page
        }
        
        self.search_worker = SearchWorker(query, search_options)
        self.search_thread = QThread()
        self.search_worker.moveToThread(self.search_thread)
        
        # Connect signals
        self.search_thread.started.connect(self.search_worker.start_search)
        self.search_worker.search_completed.connect(self.on_search_completed)
        self.search_worker.search_error.connect(self.on_search_error)
        self.search_worker.finished.connect(self.search_thread.quit)
        self.search_worker.finished.connect(self.search_worker.deleteLater)
        self.search_thread.finished.connect(self.search_thread.deleteLater)
        
        # Start search
        self.search_thread.start()
    
    def show_loading_state(self):
        """Show loading state."""
        self.empty_label.hide()
        self.results_scroll.hide()
        self.loading_label.show()
        self.search_button.set_loading(True)
    
    def hide_loading_state(self):
        """Hide loading state."""
        self.loading_label.hide()
        self.search_button.set_loading(False)
    
    def on_search_completed(self, results, total_pages):
        """Handle search completion."""
        self.hide_loading_state()
        self.search_results = results
        self.total_pages = max(1, total_pages)  # Ensure at least 1 page
        
        if results:
            self.display_results(results)
            self.update_pagination_info()
            self.empty_label.hide()
            self.results_scroll.show()
        else:
            self.show_no_results()
    
    def on_search_error(self, error_message):
        """Handle search error."""
        self.hide_loading_state()
        self.show_error_state(error_message)
    
    def display_results(self, results):
        """Display search results in grid layout."""
        # Clear existing results
        self.clear_results()
        
        # Add gallery cards
        columns = 2  # Number of columns in grid
        for i, gallery_info in enumerate(results):
            row = i // columns
            col = i % columns
            
            card = GalleryCard(gallery_info)
            card.download_requested.connect(self.download_requested.emit)
            card.info_requested.connect(self.show_gallery_info)
            
            self.results_layout.addWidget(card, row, col)
        
        # Add stretch to bottom
        self.results_layout.setRowStretch(len(results) // columns + 1, 1)
    
    def clear_results(self):
        """Clear all result widgets."""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def show_no_results(self):
        """Show no results state."""
        self.empty_label.setText("😔 No galleries found for your search")
        self.empty_label.show()
        self.results_scroll.hide()
        self.update_pagination_info()
    
    def show_error_state(self, error_message):
        """Show error state."""
        self.empty_label.setText(f"❌ Search error: {error_message}")
        self.empty_label.show()
        self.results_scroll.hide()
    
    def update_pagination_info(self):
        """Update pagination information."""
        if self.search_results:
            results_on_page = len(self.search_results)
            self.results_info_label.setText(f"Showing {results_on_page} results on page {self.current_page}")
        else:
            self.results_info_label.setText("No results found")
        
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
        
        # Update button states and text
        can_go_prev = self.current_page > 1
        can_go_next = self.current_page < self.total_pages
        
        self.prev_button.setEnabled(can_go_prev)
        self.next_button.setEnabled(can_go_next)
        
        # Update button text to show page numbers
        if can_go_prev:
            self.prev_button.setText(f"← Page {self.current_page - 1}")
        else:
            self.prev_button.setText("← Previous")
            
        if can_go_next:
            self.next_button.setText(f"Page {self.current_page + 1} →")
        else:
            self.next_button.setText("Next →")
    
    def previous_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            query = self.search_input.text().strip()
            self.perform_search(query, self.current_page)
    
    def next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            query = self.search_input.text().strip()
            self.perform_search(query, self.current_page)
    

    
    def quick_search(self, search_type: str):
        """Perform quick search - change sort order while keeping current search."""
        # Keep the current search query, just change the sort order
        current_query = self.search_input.text().strip()
        
        if search_type == "popular":
            self.sort_combo.setCurrentText("Popular")
        elif search_type == "recent":
            self.sort_combo.setCurrentText("Newest")
        
        # Reset to page 1 and re-search with the same query but different sort
        self.current_page = 1
        
        # If there's no current search, perform a browse operation
        if not current_query:
            # For browsing without search terms, we can use empty query
            self.perform_search("", self.current_page)
        else:
            # Re-search with current query but new sort order
            self.perform_search(current_query, self.current_page)
    
    def show_gallery_info(self, url: str):
        """Show detailed gallery information."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
        from PyQt6.QtCore import QThread, QObject, pyqtSignal
        
        # Create info dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Gallery Information")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Loading state
        loading_label = QLabel("🔄 Loading gallery information...")
        loading_label.setStyleSheet("color: #bb86fc; font-size: 14px;")
        layout.addWidget(loading_label)
        
        # Info display (initially hidden)
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        title_label = QLabel()
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #bb86fc;")
        title_label.setWordWrap(True)
        info_layout.addWidget(title_label)
        
        artist_label = QLabel()
        artist_label.setStyleSheet("font-size: 12px; color: #b3b3b3;")
        info_layout.addWidget(artist_label)
        
        pages_label = QLabel()
        pages_label.setStyleSheet("font-size: 12px; color: #b3b3b3;")
        info_layout.addWidget(pages_label)
        
        tags_text = QTextEdit()
        tags_text.setMaximumHeight(100)
        tags_text.setReadOnly(True)
        info_layout.addWidget(QLabel("Tags:"))
        info_layout.addWidget(tags_text)
        
        url_label = QLabel()
        url_label.setStyleSheet("font-size: 10px; color: #666666;")
        url_label.setWordWrap(True)
        info_layout.addWidget(url_label)
        
        info_widget.hide()
        layout.addWidget(info_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        download_btn = ModernButton("Download", button_type="primary")
        download_btn.clicked.connect(lambda: self.download_requested.emit(url))
        download_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(download_btn)
        
        close_btn = ModernButton("Close")
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Worker to fetch gallery info
        class InfoWorker(QObject):
            info_loaded = pyqtSignal(object)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, url):
                super().__init__()
                self.url = url
            
            def fetch_info(self):
                try:
                    from core.sites.hentaifox import HentaiFoxSite
                    site = HentaiFoxSite()
                    gallery_info = site.get_gallery_info(self.url)
                    if gallery_info:
                        self.info_loaded.emit(gallery_info)
                    else:
                        self.error_occurred.emit("Could not fetch gallery information")
                except Exception as e:
                    self.error_occurred.emit(str(e))
        
        def on_info_loaded(gallery_info):
            loading_label.hide()
            title_label.setText(gallery_info.title or "Unknown Title")
            artist_label.setText(f"Artist: {gallery_info.artist or 'Unknown'}")
            pages_label.setText(f"Pages: {gallery_info.pages or 'Unknown'}")
            
            if gallery_info.tags:
                tags_text.setPlainText(", ".join(gallery_info.tags))
            else:
                tags_text.setPlainText("No tags available")
            
            url_label.setText(f"URL: {gallery_info.url}")
            info_widget.show()
        
        def on_error(error_msg):
            loading_label.setText(f"❌ Error: {error_msg}")
            loading_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
        
        # Start worker
        worker = InfoWorker(url)
        thread = QThread()
        worker.moveToThread(thread)
        
        thread.started.connect(worker.fetch_info)
        worker.info_loaded.connect(on_info_loaded)
        worker.error_occurred.connect(on_error)
        worker.info_loaded.connect(thread.quit)
        worker.error_occurred.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)
        worker.info_loaded.connect(worker.deleteLater)
        worker.error_occurred.connect(worker.deleteLater)
        
        thread.start()
        
        dialog.exec()