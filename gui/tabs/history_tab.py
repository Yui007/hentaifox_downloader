"""History tab for viewing download history."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QLineEdit, QLabel,
                            QComboBox, QGroupBox, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

# Removed theme manager - using simple styling
from gui.widgets.modern_button import ModernButton
from core.history import history


class HistoryTab(QWidget):
    """History tab for viewing and managing download history."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Using simple black theme
        self.history_data = []
        
        self.setup_ui()
        self.apply_styling()
        self.load_history()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_history)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def setup_ui(self):
        """Setup the history tab UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("📚 Download History")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(header_label)
        
        # Controls section
        self.setup_controls_section(layout)
        
        # History table
        self.setup_history_table(layout)
        
        # Statistics section
        self.setup_statistics_section(layout)
    
    def setup_controls_section(self, parent_layout):
        """Setup controls section."""
        group = QGroupBox("Search & Filter")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        # Search and filter row
        controls_layout = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title, artist, or URL...")
        self.search_input.setFont(QFont("Segoe UI", 10))
        self.search_input.textChanged.connect(self.filter_history)
        controls_layout.addWidget(self.search_input)
        
        # Filter by site
        controls_layout.addWidget(QLabel("Site:"))
        self.site_filter = QComboBox()
        self.site_filter.addItems(["All Sites", "HentaiFox"])
        self.site_filter.currentTextChanged.connect(self.filter_history)
        controls_layout.addWidget(self.site_filter)
        
        # Filter by date
        controls_layout.addWidget(QLabel("Period:"))
        self.date_filter = QComboBox()
        self.date_filter.addItems(["All Time", "Today", "This Week", "This Month"])
        self.date_filter.currentTextChanged.connect(self.filter_history)
        controls_layout.addWidget(self.date_filter)
        
        controls_layout.addStretch()
        
        # Action buttons
        self.refresh_button = ModernButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.refresh_history)
        controls_layout.addWidget(self.refresh_button)
        
        self.clear_button = ModernButton("🗑️ Clear History", button_type="danger")
        self.clear_button.clicked.connect(self.clear_history)
        controls_layout.addWidget(self.clear_button)
        
        layout.addLayout(controls_layout)
        parent_layout.addWidget(group)
    
    def setup_history_table(self, parent_layout):
        """Setup history table."""
        group = QGroupBox("Download History")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QVBoxLayout(group)
        
        # Create table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Title", "Artist", "Files", "Date", "Size", "Status"
        ])
        
        # Configure table
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSortingEnabled(True)
        self.history_table.verticalHeader().setVisible(False)
        
        # Set column widths
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Title
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Artist
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Files
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status
        
        # Context menu
        self.history_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.history_table)
        parent_layout.addWidget(group)
    
    def setup_statistics_section(self, parent_layout):
        """Setup statistics section."""
        group = QGroupBox("Statistics")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QHBoxLayout(group)
        
        # Total downloads
        self.total_downloads_label = QLabel("Total Downloads: 0")
        self.total_downloads_label.setFont(QFont("Segoe UI", 10))
        self.total_downloads_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.total_downloads_label)
        
        # Total files
        self.total_files_label = QLabel("Total Files: 0")
        self.total_files_label.setFont(QFont("Segoe UI", 10))
        self.total_files_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.total_files_label)
        
        # Recent downloads
        self.recent_downloads_label = QLabel("Recent (7 days): 0")
        self.recent_downloads_label.setFont(QFont("Segoe UI", 10))
        self.recent_downloads_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.recent_downloads_label)
        
        layout.addStretch()
        
        # Export button
        self.export_button = ModernButton("📊 Export CSV")
        self.export_button.clicked.connect(self.export_history)
        layout.addWidget(self.export_button)
        
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
            
            QTableWidget {
                gridline-color: #374151;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #111827, stop:1 #0F172A);
                alternate-background-color: #1F2937;
                selection-background-color: #8B5CF6;
                color: #F8FAFC;
                border: 1px solid #4B5563;
                border-radius: 8px;
                font-size: 11px;
            }
            
            QTableWidget::item {
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #374151;
            }
            
            QTableWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6, stop:1 #7C3AED);
                color: #FFFFFF;
            }
            
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #374151, stop:1 #1F2937);
                padding: 12px 8px;
                border: 1px solid #4B5563;
                border-radius: 0px;
                font-weight: 600;
                color: #F8FAFC;
                font-size: 11px;
            }
            
            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }
            
            QHeaderView::section:last {
                border-top-right-radius: 8px;
            }
            
            QHeaderView::section:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4B5563, stop:1 #374151);
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
    
    def load_history(self):
        """Load download history from database."""
        try:
            # Get recent downloads
            entries = history.get_recent_downloads(1000)  # Load last 1000 entries
            self.history_data = entries
            self.populate_table(entries)
            self.update_statistics()
        except Exception as e:
            print(f"Error loading history: {e}")
    
    def populate_table(self, entries):
        """Populate table with history entries."""
        self.history_table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Title
            title_item = QTableWidgetItem(entry.title[:50] + "..." if len(entry.title) > 50 else entry.title)
            title_item.setToolTip(entry.title)
            self.history_table.setItem(row, 0, title_item)
            
            # Artist (extract from title or use placeholder)
            artist = "Unknown"
            if hasattr(entry, 'artist') and entry.artist:
                artist = entry.artist
            self.history_table.setItem(row, 1, QTableWidgetItem(artist))
            
            # Files count
            self.history_table.setItem(row, 2, QTableWidgetItem(str(entry.files_count)))
            
            # Date
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(entry.downloaded_at)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = entry.downloaded_at[:16]
            self.history_table.setItem(row, 3, QTableWidgetItem(date_str))
            
            # Size (placeholder - would need to calculate actual size)
            self.history_table.setItem(row, 4, QTableWidgetItem("N/A"))
            
            # Status
            status = "✅ Complete"
            status_item = QTableWidgetItem(status)
            from PyQt6.QtGui import QColor
            status_item.setForeground(QColor('#4caf50'))
            self.history_table.setItem(row, 5, status_item)
    
    def filter_history(self):
        """Filter history based on search and filter criteria."""
        search_text = self.search_input.text().lower()
        site_filter = self.site_filter.currentText()
        date_filter = self.date_filter.currentText()
        
        # Filter entries
        filtered_entries = []
        for entry in self.history_data:
            # Search filter
            if search_text and search_text not in entry.title.lower() and search_text not in entry.url.lower():
                continue
            
            # Site filter
            if site_filter != "All Sites" and entry.site.lower() != site_filter.lower():
                continue
            
            # Date filter
            if date_filter != "All Time":
                from datetime import datetime, timedelta
                try:
                    entry_date = datetime.fromisoformat(entry.downloaded_at)
                    now = datetime.now()
                    
                    if date_filter == "Today" and entry_date.date() != now.date():
                        continue
                    elif date_filter == "This Week" and (now - entry_date).days > 7:
                        continue
                    elif date_filter == "This Month" and (now - entry_date).days > 30:
                        continue
                except:
                    continue
            
            filtered_entries.append(entry)
        
        self.populate_table(filtered_entries)
    
    def update_statistics(self):
        """Update statistics labels."""
        try:
            stats = history.get_stats()
            
            self.total_downloads_label.setText(f"Total Downloads: {stats['total_downloads']}")
            self.total_files_label.setText(f"Total Files: {stats['total_files']}")
            self.recent_downloads_label.setText(f"Recent (7 days): {stats['recent_downloads']}")
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def refresh_history(self):
        """Refresh history data."""
        self.refresh_button.set_loading(True)
        QTimer.singleShot(1000, self.finish_refresh)
        self.load_history()
    
    def finish_refresh(self):
        """Finish refresh operation."""
        self.refresh_button.set_success(1000)
    
    def clear_history(self):
        """Clear download history."""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all download history?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                history.clear_history()
                self.load_history()
                self.clear_button.set_success(2000)
            except Exception as e:
                self.clear_button.set_error(2000)
                print(f"Error clearing history: {e}")
    
    def export_history(self):
        """Export history to CSV file."""
        from PyQt6.QtWidgets import QFileDialog
        import csv
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export History", "download_history.csv", "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Title', 'URL', 'Files', 'Downloaded', 'Path', 'Site'])
                    
                    for entry in self.history_data:
                        writer.writerow([
                            entry.title,
                            entry.url,
                            entry.files_count,
                            entry.downloaded_at,
                            entry.download_path,
                            entry.site
                        ])
                
                self.export_button.set_success(2000)
            except Exception as e:
                self.export_button.set_error(2000)
                print(f"Error exporting history: {e}")
    
    def show_context_menu(self, position):
        """Show context menu for table items."""
        # This would show a context menu with options like "Open Folder", "Re-download", etc.
        pass
    
    def refresh_history(self):
        """Refresh history (called from download completion)."""
        self.load_history()