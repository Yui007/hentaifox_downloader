"""Simplified download tab without complex threading."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                            QLabel, QCheckBox, QComboBox, QSpinBox, QGroupBox, 
                            QGridLayout, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont

# Removed theme manager - using simple black theme
from gui.widgets.modern_button import ModernButton
from config.settings import config


class SimpleDownloadTab(QWidget):
    """Simplified download tab with basic functionality."""
    
    download_completed = pyqtSignal(str)  # gallery_url
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        self.apply_simple_styling()
    
    def setup_ui(self):
        """Setup the download tab UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("📥 Download Manager")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(header_label)
        
        # URL input section
        self.setup_url_input(layout)
        
        # Download options
        self.setup_download_options(layout)
        
        # Status area
        self.setup_status_area(layout)
        
        layout.addStretch()
    
    def setup_url_input(self, parent_layout):
        """Setup URL input section."""
        group = QGroupBox("Download URL")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        # URL input
        url_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter HentaiFox gallery URL...")
        self.url_input.setFont(QFont("Segoe UI", 10))
        self.url_input.returnPressed.connect(self.start_download)
        url_layout.addWidget(self.url_input)
        
        self.download_button = ModernButton("Download", button_type="primary")
        self.download_button.clicked.connect(self.start_download)
        url_layout.addWidget(self.download_button)
        
        layout.addLayout(url_layout)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        self.paste_button = ModernButton("Paste from Clipboard")
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        actions_layout.addWidget(self.paste_button)
        
        actions_layout.addStretch()
        
        self.clear_button = ModernButton("Clear")
        self.clear_button.clicked.connect(self.clear_input)
        actions_layout.addWidget(self.clear_button)
        
        layout.addLayout(actions_layout)
        
        parent_layout.addWidget(group)
    
    def setup_download_options(self, parent_layout):
        """Setup download options section."""
        group = QGroupBox("Download Options")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QGridLayout(group)
        layout.setSpacing(12)
        
        # Output directory
        layout.addWidget(QLabel("Output Directory:"), 0, 0)
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("Default download directory")
        layout.addWidget(self.output_input, 0, 1)
        
        browse_button = ModernButton("Browse")
        browse_button.clicked.connect(self.browse_output_directory)
        layout.addWidget(browse_button, 0, 2)
        
        # Conversion options
        layout.addWidget(QLabel("Convert to:"), 1, 0)
        self.convert_combo = QComboBox()
        self.convert_combo.addItems(["None", "PDF", "CBZ"])
        layout.addWidget(self.convert_combo, 1, 1)
        
        # Quality settings
        layout.addWidget(QLabel("Quality:"), 1, 2)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(95)
        self.quality_spin.setSuffix("%")
        layout.addWidget(self.quality_spin, 1, 3)
        
        # Checkboxes
        self.delete_images_check = QCheckBox("Delete images after conversion")
        # Load default from settings
        self.refresh_settings()
        layout.addWidget(self.delete_images_check, 2, 0)
        
        self.force_download_check = QCheckBox("Force download (overwrite existing)")
        layout.addWidget(self.force_download_check, 2, 2)
        
        parent_layout.addWidget(group)
    
    def setup_status_area(self, parent_layout):
        """Setup status display area."""
        group = QGroupBox("Status")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QVBoxLayout(group)
        
        # Status text area
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        self.status_text.setReadOnly(True)
        self.status_text.setPlainText("Ready to download...")
        layout.addWidget(self.status_text)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.test_button = ModernButton("Test URL")
        self.test_button.clicked.connect(self.test_url)
        controls_layout.addWidget(self.test_button)
        
        controls_layout.addStretch()
        
        self.clear_status_button = ModernButton("Clear Status")
        self.clear_status_button.clicked.connect(self.clear_status)
        controls_layout.addWidget(self.clear_status_button)
        
        layout.addLayout(controls_layout)
        
        parent_layout.addWidget(group)
    
    def apply_simple_styling(self):
        """Apply beautiful modern styling."""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                color: #F8FAFC;
            }
            
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
            
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #111827, stop:1 #0F172A);
                border: 1px solid #4B5563;
                border-radius: 8px;
                padding: 12px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                color: #F8FAFC;
                line-height: 1.4;
            }
            
            QTextEdit:focus {
                border-color: #8B5CF6;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1F2937, stop:1 #111827);
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
    
    def start_download(self):
        """Start downloading from URL input."""
        url = self.url_input.text().strip()
        if not url:
            self.add_status("❌ Please enter a URL")
            return
        
        self.add_status(f"🔄 Starting download: {url}")
        self.download_button.set_loading(True)
        
        # Start actual download in separate thread
        self.start_threaded_download(url)
    
    def get_download_options(self):
        """Get current download options."""
        return {
            'output_dir': self.output_input.text().strip() or None,
            'convert_to': self.convert_combo.currentText().lower() if self.convert_combo.currentText() != "None" else None,
            'quality': self.quality_spin.value(),
            'delete_images': self.delete_images_check.isChecked(),
            'force_download': self.force_download_check.isChecked()
        }
    
    def test_url(self):
        """Test if URL is valid."""
        url = self.url_input.text().strip()
        if not url:
            self.add_status("❌ Please enter a URL to test")
            return
        
        self.add_status(f"🔍 Testing URL: {url}")
        self.test_button.set_loading(True)
        
        # Test URL using actual site validation
        try:
            from core.sites.hentaifox import HentaiFoxSite
            
            site = HentaiFoxSite()
            if site.is_valid_url(url):
                self.add_status(f"✅ URL format is valid")
                
                # Try to get gallery info
                gallery_info = site.get_gallery_info(url)
                if gallery_info:
                    self.add_status(f"✅ Gallery found: {gallery_info.title}")
                    self.add_status(f"📄 Pages: {gallery_info.pages}")
                    if gallery_info.artist:
                        self.add_status(f"👨‍🎨 Artist: {gallery_info.artist}")
                    self.test_button.set_success(2000)
                else:
                    self.add_status("❌ Could not fetch gallery information")
                    self.test_button.set_error(2000)
            else:
                self.add_status(f"❌ Invalid HentaiFox URL format")
                self.test_button.set_error(2000)
                
        except Exception as e:
            self.add_status(f"❌ Error testing URL: {str(e)}")
            self.test_button.set_error(2000)
    
    def add_status(self, message):
        """Add status message."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")
    
    def clear_status(self):
        """Clear status text."""
        self.status_text.clear()
        self.status_text.setPlainText("Ready to download...")
    
    def clear_input(self):
        """Clear URL input."""
        self.url_input.clear()
    
    def paste_from_clipboard(self):
        """Paste URL from clipboard."""
        from PyQt6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        
        if text:
            self.url_input.setText(text)
            self.add_status(f"📋 Pasted from clipboard: {text}")
    
    def browse_output_directory(self):
        """Browse for output directory."""
        from PyQt6.QtWidgets import QFileDialog
        
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        
        if directory:
            self.output_input.setText(directory)
            self.add_status(f"📁 Output directory set: {directory}")
    
    def start_threaded_download(self, url: str):
        """Start download in a separate thread to avoid GUI hanging."""
        # Create worker and thread
        self.download_worker = SimpleDownloadWorker(url, self.get_download_options())
        self.download_thread = QThread()
        self.download_worker.moveToThread(self.download_thread)
        
        # Connect signals
        self.download_thread.started.connect(self.download_worker.run)
        self.download_worker.status_update.connect(self.add_status)
        self.download_worker.download_complete.connect(self.on_download_complete)
        self.download_worker.download_error.connect(self.on_download_error)
        self.download_worker.finished.connect(self.download_thread.quit)
        self.download_worker.finished.connect(self.download_worker.deleteLater)
        self.download_thread.finished.connect(self.download_thread.deleteLater)
        
        # Start thread
        self.download_thread.start()
    
    def on_download_complete(self, url: str):
        """Handle download completion."""
        self.download_button.set_success(2000)
        self.download_completed.emit(url)
        self.url_input.clear()
    
    def on_download_error(self, error_msg: str):
        """Handle download error."""
        self.download_button.set_error(2000)
    
    def add_download(self, url: str):
        """Add a download (called from search tab)."""
        self.url_input.setText(url)
        self.add_status(f"📥 Added download from search: {url}")
        self.start_download()
    
    def refresh_settings(self):
        """Refresh settings from config."""
        self.delete_images_check.setChecked(config.get("conversion.delete_source_after_conversion", False))


class SimpleDownloadWorker(QObject):
    """Simple worker for downloading in background thread."""
    
    status_update = pyqtSignal(str)
    download_complete = pyqtSignal(str)
    download_error = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, url: str, options: dict):
        super().__init__()
        self.url = url
        self.options = options
    
    def run(self):
        """Run the download process."""
        try:
            from core.sites.hentaifox import HentaiFoxSite
            from core.downloader import GalleryDLDownloader
            from core.converter import converter
            from core.history import history
            
            # Validate URL
            site = HentaiFoxSite()
            if not site.is_valid_url(self.url):
                self.status_update.emit(f"❌ Invalid HentaiFox URL: {self.url}")
                self.download_error.emit("Invalid URL")
                self.finished.emit()
                return
            
            self.status_update.emit("🔍 Fetching gallery information...")
            
            # Get gallery info
            gallery_info = site.get_gallery_info(self.url)
            if not gallery_info:
                self.status_update.emit("❌ Could not fetch gallery information")
                self.download_error.emit("Could not fetch gallery info")
                self.finished.emit()
                return
            
            self.status_update.emit(f"📖 Found: {gallery_info.title}")
            self.status_update.emit(f"📄 Pages: {gallery_info.pages}")
            
            # Setup downloader
            downloader = GalleryDLDownloader()
            
            # Set output directory if specified
            if self.options.get('output_dir'):
                from config.settings import config
                original_path = config.get("download.base_path")
                config.set("download.base_path", self.options.get('output_dir'))
            
            self.status_update.emit("⬇️ Starting download...")
            
            # Perform download
            result = downloader.download_gallery(self.url, gallery_info)
            
            # Restore original path if changed
            if self.options.get('output_dir'):
                config.set("download.base_path", original_path)
            
            if result.success:
                self.status_update.emit(f"✅ Download completed: {result.files_downloaded} files")
                
                # Handle conversion if requested
                convert_to = self.options.get('convert_to')
                if convert_to and convert_to != 'none':
                    self.status_update.emit(f"🔄 Converting to {convert_to.upper()}...")
                    
                    try:
                        if convert_to == 'pdf':
                            conversion_result = converter.convert_to_pdf(
                                result.download_path,
                                delete_source=self.options.get('delete_images', False),
                                quality=self.options.get('quality', 95)
                            )
                        elif convert_to == 'cbz':
                            conversion_result = converter.convert_to_cbz(
                                result.download_path,
                                delete_source=self.options.get('delete_images', False),
                                quality=self.options.get('quality', 95)
                            )
                        
                        if conversion_result.success and conversion_result.output_path:
                            self.status_update.emit(f"✅ Converted to {convert_to.upper()}: {conversion_result.output_path.name}")
                        else:
                            error_msg = conversion_result.error_message or "Unknown error"
                            self.status_update.emit(f"❌ Conversion failed: {error_msg}")
                    except Exception as e:
                        self.status_update.emit(f"❌ Conversion error: {str(e)}")
                
                # Add to history
                if result.gallery_info and result.download_path:
                    try:
                        history.add_download(
                            gallery_info=result.gallery_info,
                            download_path=str(result.download_path),
                            files_count=result.files_downloaded,
                            site="hentaifox"
                        )
                    except Exception as e:
                        self.status_update.emit(f"⚠️ Could not add to history: {str(e)}")
                
                self.download_complete.emit(self.url)
                
            else:
                error_msg = result.error_message or "Download failed"
                self.status_update.emit(f"❌ Download failed: {error_msg}")
                self.download_error.emit(error_msg)
                
        except Exception as e:
            self.status_update.emit(f"❌ Error: {str(e)}")
            self.download_error.emit(str(e))
            import traceback
            print(f"Download error: {traceback.format_exc()}")
        finally:
            self.finished.emit()