"""Main GUI application entry point."""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

from gui.windows.main_window import MainWindow
# Removed theme manager - using simple styling


class HentaiFoxDownloaderApp(QApplication):
    """Main GUI application class."""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("HentaiFox Downloader")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("HentaiFox Downloader")
        
        # Set application properties for high DPI support
        try:
            self.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
            self.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        except AttributeError:
            # These attributes might not be available in all PyQt6 versions
            pass
        
        # Apply simple dark theme
        self.setStyleSheet("""
            QApplication {
                background-color: #1e1e1e;
                color: #ffffff;
            }
        """)
        
        # Set custom font
        font = QFont("Segoe UI", 9)
        self.setFont(font)
        
        # Create main window
        self.main_window = MainWindow()
        self.main_window.show()
    
    def run(self):
        """Run the application."""
        return self.exec()


def main():
    """Main entry point for GUI application."""
    app = HentaiFoxDownloaderApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()