"""Main application window."""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QStatusBar, QMenuBar, QToolBar, QSplitter)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont

# Removed theme manager - using simple styling
# Temporarily comment out AnimationManager to debug
# from gui.utils.animations import AnimationManager
# Import tabs one by one to test
try:
    from gui.tabs.simple_download_tab import SimpleDownloadTab as DownloadTab
    DOWNLOAD_TAB_AVAILABLE = True
except ImportError as e:
    print(f"Download tab import error: {e}")
    DOWNLOAD_TAB_AVAILABLE = False

try:
    from gui.tabs.search_tab import SearchTab
    SEARCH_TAB_AVAILABLE = True
except ImportError as e:
    print(f"Search tab import error: {e}")
    SEARCH_TAB_AVAILABLE = False

try:
    from gui.tabs.history_tab import HistoryTab
    HISTORY_TAB_AVAILABLE = True
except ImportError as e:
    print(f"History tab import error: {e}")
    HISTORY_TAB_AVAILABLE = False

try:
    from gui.tabs.settings_tab import SettingsTab
    SETTINGS_TAB_AVAILABLE = True
except ImportError as e:
    print(f"Settings tab import error: {e}")
    SETTINGS_TAB_AVAILABLE = False
from gui.widgets.modern_button import ModernButton


class MainWindow(QMainWindow):
    """Main application window with modern design."""
    
    def __init__(self):
        super().__init__()
        # Using simple black theme
        # self.animation_manager = AnimationManager()
        
        self.setWindowTitle("HentaiFox Downloader - Modern Manga Downloader")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Center window on screen
        self.center_on_screen()
        
        # Setup UI components
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_status_bar()
        self.apply_styling()
        
        # Apply simple black theme
        self.setStyleSheet(self.get_simple_stylesheet())
        
        # Show window normally for now
        # self.show_animated()
        self.show()
    
    def center_on_screen(self):
        """Center the window on screen."""
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())
    
    def setup_ui(self):
        """Setup the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create main tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)
        self.tab_widget.setDocumentMode(True)
        
        # Create tabs (use real tabs if available, fallback to simple ones)
        from PyQt6.QtWidgets import QLabel
        
        # Download tab
        if DOWNLOAD_TAB_AVAILABLE:
            try:
                self.download_tab = DownloadTab()
                self.tab_widget.addTab(self.download_tab, "📥 Download")
            except Exception as e:
                print(f"Error creating download tab: {e}")
                download_tab = QWidget()
                download_layout = QVBoxLayout(download_tab)
                download_layout.addWidget(QLabel("📥 Download tab error"))
                self.tab_widget.addTab(download_tab, "📥 Download")
        else:
            download_tab = QWidget()
            download_layout = QVBoxLayout(download_tab)
            download_layout.addWidget(QLabel("📥 Download functionality coming soon..."))
            self.tab_widget.addTab(download_tab, "📥 Download")
        
        # Search tab
        if SEARCH_TAB_AVAILABLE:
            try:
                self.search_tab = SearchTab()
                self.tab_widget.addTab(self.search_tab, "🔍 Search")
            except Exception as e:
                print(f"Error creating search tab: {e}")
                search_tab = QWidget()
                search_layout = QVBoxLayout(search_tab)
                search_layout.addWidget(QLabel("🔍 Search tab error"))
                self.tab_widget.addTab(search_tab, "🔍 Search")
        else:
            search_tab = QWidget()
            search_layout = QVBoxLayout(search_tab)
            search_layout.addWidget(QLabel("🔍 Search functionality coming soon..."))
            self.tab_widget.addTab(search_tab, "🔍 Search")
        
        # History tab
        if HISTORY_TAB_AVAILABLE:
            try:
                self.history_tab = HistoryTab()
                self.tab_widget.addTab(self.history_tab, "📚 History")
            except Exception as e:
                print(f"Error creating history tab: {e}")
                history_tab = QWidget()
                history_layout = QVBoxLayout(history_tab)
                history_layout.addWidget(QLabel("📚 History tab error"))
                self.tab_widget.addTab(history_tab, "📚 History")
        else:
            history_tab = QWidget()
            history_layout = QVBoxLayout(history_tab)
            history_layout.addWidget(QLabel("📚 History functionality coming soon..."))
            self.tab_widget.addTab(history_tab, "📚 History")
        
        # Settings tab
        if SETTINGS_TAB_AVAILABLE:
            try:
                self.settings_tab = SettingsTab()
                self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
            except Exception as e:
                print(f"Error creating settings tab: {e}")
                settings_tab = QWidget()
                settings_layout = QVBoxLayout(settings_tab)
                settings_layout.addWidget(QLabel("⚙️ Settings tab error"))
                self.tab_widget.addTab(settings_tab, "⚙️ Settings")
        else:
            settings_tab = QWidget()
            settings_layout = QVBoxLayout(settings_tab)
            settings_layout.addWidget(QLabel("⚙️ Settings functionality coming soon..."))
            self.tab_widget.addTab(settings_tab, "⚙️ Settings")
        
        # Connect tab signals if tabs are available
        try:
            if hasattr(self, 'search_tab') and hasattr(self, 'download_tab'):
                self.search_tab.download_requested.connect(self.download_tab.add_download)
            if hasattr(self, 'download_tab') and hasattr(self, 'history_tab'):
                self.download_tab.download_completed.connect(self.history_tab.refresh_history)
            if hasattr(self, 'settings_tab') and hasattr(self, 'download_tab'):
                self.settings_tab.settings_changed.connect(self.download_tab.refresh_settings)
        except Exception as e:
            print(f"Error connecting tab signals: {e}")
        
        layout.addWidget(self.tab_widget)
    
    def setup_menu_bar(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_download_action = QAction("New Download", self)
        new_download_action.setShortcut("Ctrl+N")
        new_download_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        file_menu.addAction(new_download_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        search_action = QAction("Search Galleries", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        tools_menu.addAction(search_action)
        
        history_action = QAction("View History", self)
        history_action.setShortcut("Ctrl+H")
        history_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        tools_menu.addAction(history_action)
        
        tools_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # Quick download action
        download_action = QAction("📥 Quick Download", self)
        download_action.setToolTip("Switch to download tab")
        download_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        toolbar.addAction(download_action)
        
        toolbar.addSeparator()
        
        # Search action
        search_action = QAction("🔍 Search", self)
        search_action.setToolTip("Switch to search tab")
        search_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(search_action)
        
        toolbar.addSeparator()
        
        # History action
        history_action = QAction("📚 History", self)
        history_action.setToolTip("View download history")
        history_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        toolbar.addAction(history_action)
        
        # Add stretch to push settings to the right
        spacer = QWidget()
        from PyQt6.QtWidgets import QSizePolicy
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self)
        settings_action.setToolTip("Open settings")
        settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        toolbar.addAction(settings_action)
    
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_bar.showMessage("Ready")
        
        # Add permanent widgets to status bar
        self.status_label = self.status_bar
    
    def get_simple_stylesheet(self):
        """Get beautiful modern dark theme stylesheet."""
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0F172A, stop:1 #1E293B);
                color: #F8FAFC;
            }
            
            QWidget {
                background-color: transparent;
                color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QTabWidget::pane {
                border: 1px solid #334155;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E293B, stop:1 #0F172A);
                border-radius: 12px;
                margin-top: 8px;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #334155, stop:1 #1E293B);
                color: #CBD5E1;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                font-weight: 500;
                font-size: 11px;
                min-width: 100px;
                border: 1px solid #475569;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6, stop:1 #7C3AED);
                color: #FFFFFF;
                font-weight: 600;
                border-color: #A855F7;
            }
            
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #475569, stop:1 #334155);
                color: #F1F5F9;
            }
            
            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E293B, stop:1 #0F172A);
                color: #F8FAFC;
                border-bottom: 1px solid #334155;
                padding: 4px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: 500;
                color: #F8FAFC;
            }
            
            QMenuBar::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6, stop:1 #7C3AED);
                color: #FFFFFF;
            }
            
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E293B, stop:1 #0F172A);
                border: none;
                border-bottom: 1px solid #334155;
                spacing: 8px;
                padding: 8px;
            }
            
            QToolBar QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #374151, stop:1 #1F2937);
                border: 1px solid #4B5563;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 500;
                color: #F8FAFC;
                min-width: 80px;
            }
            
            QToolBar QToolButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4B5563, stop:1 #374151);
                border-color: #6B7280;
            }
            
            QToolBar QToolButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6, stop:1 #7C3AED);
                border-color: #A855F7;
            }
            
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E293B, stop:1 #0F172A);
                color: #94A3B8;
                border-top: 1px solid #334155;
                padding: 8px;
                font-size: 10px;
            }
            
            /* Input fields styling */
            QLineEdit, QTextEdit, QSpinBox, QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #374151, stop:1 #1F2937);
                border: 1px solid #4B5563;
                border-radius: 8px;
                padding: 8px 12px;
                color: #F8FAFC;
                font-size: 11px;
            }
            
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #8B5CF6;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4B5563, stop:1 #374151);
            }
            
            /* Checkbox styling */
            QCheckBox {
                color: #F8FAFC;
                font-size: 11px;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #4B5563;
                background: #1F2937;
            }
            
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6, stop:1 #7C3AED);
                border-color: #A855F7;
            }
            
            QCheckBox::indicator:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #A855F7, stop:1 #8B5CF6);
            }
        """
    
    def apply_styling(self):
        """Apply custom styling to the window."""
        pass  # Styling now handled in get_simple_stylesheet
        
        # Styling is now handled in get_simple_stylesheet()
    
    # def show_animated(self):
    #     """Show window with fade in animation."""
    #     self.show()
    #     self.animation_manager.fade_in(self, 400)
    
    def show_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox
        
        about_text = """
        <h2>HentaiFox Downloader</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Description:</b> Modern, high-performance manga downloader</p>
        <p><b>Features:</b></p>
        <ul>
            <li>High-speed downloads with Aria2c integration</li>
            <li>Beautiful modern interface</li>
            <li>Search and browse galleries</li>
            <li>Download history tracking</li>
            <li>PDF/CBZ conversion</li>
        </ul>
        <p><b>Built with:</b> Python, PyQt6, gallery-dl</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About HentaiFox Downloader")
        msg.setText(about_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def update_status(self, message: str):
        """Update status bar message."""
        self.status_bar.showMessage(message)
        
        # Clear message after 5 seconds
        QTimer.singleShot(5000, lambda: self.status_bar.showMessage("Ready"))
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Cancel any ongoing downloads
        if hasattr(self.download_tab, 'cancel_all_downloads'):
            self.download_tab.cancel_all_downloads()
        
        event.accept()