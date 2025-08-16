"""Gallery card widget for displaying gallery information."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPixmap, QFont, QPainter, QPen, QBrush, QColor
# Removed theme manager - using simple styling
from gui.widgets.modern_button import ModernButton


class GalleryCard(QWidget):
    """Modern card widget for displaying gallery information."""
    
    download_requested = pyqtSignal(str)  # gallery_url
    info_requested = pyqtSignal(str)      # gallery_url
    
    def __init__(self, gallery_info=None, parent=None):
        super().__init__(parent)
        self.gallery_info = gallery_info
        # Using simple black theme
        self._hover_progress = 0.0
        
        # Setup hover animation
        self.hover_animation = QPropertyAnimation(self, b"hover_progress")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.setup_ui()
        self.setup_styling()
        
        if gallery_info:
            self.update_info(gallery_info)
    
    @pyqtProperty(float)
    def hover_progress(self):
        return self._hover_progress
    
    @hover_progress.setter
    def hover_progress(self, value):
        self._hover_progress = value
        self.update_styling()
    
    def setup_ui(self):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header layout
        header_layout = QHBoxLayout()
        
        # Thumbnail placeholder
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(90, 120)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4B5563, stop:1 #374151);
                border: 1px solid #6B7280;
                border-radius: 12px;
            }
        """)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setText("📖")
        self.thumbnail_label.setFont(QFont("Segoe UI", 28))
        header_layout.addWidget(self.thumbnail_label)
        
        # Info layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        
        # Title
        self.title_label = QLabel("Gallery Title")
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #F8FAFC; line-height: 1.4;")
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)
        
        # Artist
        self.artist_label = QLabel("Artist Name")
        self.artist_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.artist_label.setStyleSheet("color: #8B5CF6; font-weight: 500;")
        info_layout.addWidget(self.artist_label)
        
        # Pages
        self.pages_label = QLabel("0 pages")
        self.pages_label.setFont(QFont("Segoe UI", 9))
        self.pages_label.setStyleSheet("color: #94A3B8; font-weight: 400;")
        info_layout.addWidget(self.pages_label)
        
        # Tags container
        self.tags_widget = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_widget)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(4)
        info_layout.addWidget(self.tags_widget)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        layout.addLayout(header_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.info_button = ModernButton("Info", button_type="default")
        self.info_button.clicked.connect(self.on_info_clicked)
        buttons_layout.addWidget(self.info_button)
        
        buttons_layout.addStretch()
        
        self.download_button = ModernButton("Download", button_type="primary")
        self.download_button.clicked.connect(self.on_download_clicked)
        buttons_layout.addWidget(self.download_button)
        
        layout.addLayout(buttons_layout)
    
    def setup_styling(self):
        """Setup card styling."""
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)
        
        self.update_styling()
    
    def update_styling(self):
        """Update styling based on hover state."""
        # Beautiful gradient hover effect
        if self._hover_progress > 0.5:
            bg_gradient = """
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #374151, stop:1 #1F2937);
                border: 1px solid #6B7280;
            """
        else:
            bg_gradient = """
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1F2937, stop:1 #111827);
                border: 1px solid #4B5563;
            """
        
        self.setStyleSheet(f"""
            GalleryCard {{
                {bg_gradient}
                border-radius: 16px;
            }}
        """)
    
    def update_info(self, gallery_info):
        """Update card with gallery information."""
        self.gallery_info = gallery_info
        
        # Update labels
        self.title_label.setText(gallery_info.get('title', 'Unknown Title'))
        self.artist_label.setText(gallery_info.get('artist', 'Unknown Artist'))
        self.pages_label.setText(f"{gallery_info.get('pages', 0)} pages")
        
        # Update tags
        self.clear_tags()
        tags = gallery_info.get('tags', [])[:3]  # Show max 3 tags
        for tag in tags:
            self.add_tag(tag)
    
    def clear_tags(self):
        """Clear all tag widgets."""
        while self.tags_layout.count():
            child = self.tags_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def add_tag(self, tag_text: str):
        """Add a beautiful tag widget."""
        tag_label = QLabel(tag_text)
        tag_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        tag_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6, stop:1 #7C3AED);
                color: #FFFFFF;
                border-radius: 10px;
                padding: 4px 8px;
                font-weight: 500;
            }
        """)
        self.tags_layout.addWidget(tag_label)
    
    def enterEvent(self, event):
        """Handle mouse enter."""
        super().enterEvent(event)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        super().leaveEvent(event)
        self.hover_animation.setEndValue(0.0)
        self.hover_animation.start()
    
    def on_download_clicked(self):
        """Handle download button click."""
        if self.gallery_info and 'url' in self.gallery_info:
            self.download_button.set_loading(True)
            self.download_requested.emit(self.gallery_info['url'])
    
    def on_info_clicked(self):
        """Handle info button click."""
        if self.gallery_info and 'url' in self.gallery_info:
            self.info_requested.emit(self.gallery_info['url'])
    
    def set_download_complete(self):
        """Set download complete state."""
        self.download_button.set_success()
    
    def set_download_error(self):
        """Set download error state."""
        self.download_button.set_error()
    
    def reset_download_state(self):
        """Reset download button state."""
        self.download_button.reset_state("Download")