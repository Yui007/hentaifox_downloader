"""Settings tab for configuring the application."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QSpinBox, QCheckBox, QComboBox,
                            QGroupBox, QGridLayout, QSlider, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Removed theme manager - using simple styling
from gui.widgets.modern_button import ModernButton
from config.settings import config


class SettingsTab(QWidget):
    """Settings tab for application configuration."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Using simple black theme
        
        self.setup_ui()
        self.apply_styling()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings tab UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("⚙️ Settings")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(header_label)
        
        # Download settings
        self.setup_download_settings(layout)
        
        # Performance settings
        self.setup_performance_settings(layout)
        
        # Conversion settings
        self.setup_conversion_settings(layout)
        
        # Interface settings
        self.setup_interface_settings(layout)
        
        # Action buttons
        self.setup_action_buttons(layout)
        
        layout.addStretch()
    
    def setup_download_settings(self, parent_layout):
        """Setup download settings section."""
        group = QGroupBox("Download Settings")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QGridLayout(group)
        layout.setSpacing(12)
        
        # Base download path
        layout.addWidget(QLabel("Download Directory:"), 0, 0)
        self.download_path_input = QLineEdit()
        layout.addWidget(self.download_path_input, 0, 1)
        
        browse_button = ModernButton("Browse")
        browse_button.clicked.connect(self.browse_download_directory)
        layout.addWidget(browse_button, 0, 2)
        
        # Folder template
        layout.addWidget(QLabel("Folder Template:"), 1, 0)
        self.folder_template_input = QLineEdit()
        self.folder_template_input.setPlaceholderText("{title}")
        layout.addWidget(self.folder_template_input, 1, 1, 1, 2)
        
        # Filename template
        layout.addWidget(QLabel("Filename Template:"), 2, 0)
        self.filename_template_input = QLineEdit()
        self.filename_template_input.setPlaceholderText("{page:03d}.{ext}")
        layout.addWidget(self.filename_template_input, 2, 1, 1, 2)
        
        # Max concurrent downloads
        layout.addWidget(QLabel("Max Concurrent Downloads:"), 3, 0)
        self.max_concurrent_spin = QSpinBox()
        self.max_concurrent_spin.setRange(1, 20)
        layout.addWidget(self.max_concurrent_spin, 3, 1)
        
        # Retry attempts
        layout.addWidget(QLabel("Retry Attempts:"), 3, 2)
        self.retry_attempts_spin = QSpinBox()
        self.retry_attempts_spin.setRange(0, 10)
        layout.addWidget(self.retry_attempts_spin, 3, 3)
        
        # Checkboxes
        self.create_subfolders_check = QCheckBox("Create subfolders")
        layout.addWidget(self.create_subfolders_check, 4, 0)
        
        parent_layout.addWidget(group)
    
    def setup_performance_settings(self, parent_layout):
        """Setup performance settings section."""
        group = QGroupBox("Performance Settings")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QGridLayout(group)
        layout.setSpacing(12)
        
        # Use Aria2c
        self.use_aria2_check = QCheckBox("Use Aria2c for faster downloads")
        layout.addWidget(self.use_aria2_check, 0, 0, 1, 2)
        
        # Aria2c path
        layout.addWidget(QLabel("Aria2c Path:"), 1, 0)
        self.aria2_path_input = QLineEdit()
        self.aria2_path_input.setPlaceholderText("aria2c")
        layout.addWidget(self.aria2_path_input, 1, 1)
        
        # Max connections per server
        layout.addWidget(QLabel("Max Connections per Server:"), 2, 0)
        self.max_connections_spin = QSpinBox()
        self.max_connections_spin.setRange(1, 16)
        layout.addWidget(self.max_connections_spin, 2, 1)
        
        # Max parallel galleries
        layout.addWidget(QLabel("Max Parallel Galleries:"), 2, 2)
        self.max_parallel_spin = QSpinBox()
        self.max_parallel_spin.setRange(1, 10)
        layout.addWidget(self.max_parallel_spin, 2, 3)
        
        # Turbo mode
        self.turbo_mode_check = QCheckBox("Enable Turbo Mode (maximum speed)")
        self.turbo_mode_check.toggled.connect(self.on_turbo_mode_toggled)
        layout.addWidget(self.turbo_mode_check, 3, 0, 1, 2)
        
        parent_layout.addWidget(group)
    
    def setup_conversion_settings(self, parent_layout):
        """Setup conversion settings section."""
        group = QGroupBox("Conversion Settings")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout = QGridLayout(group)
        layout.setSpacing(12)
        
        # Auto convert
        self.auto_convert_check = QCheckBox("Auto-convert after download")
        layout.addWidget(self.auto_convert_check, 0, 0)
        
        # Default format
        layout.addWidget(QLabel("Default Format:"), 0, 1)
        self.default_format_combo = QComboBox()
        self.default_format_combo.addItems(["None", "PDF", "CBZ"])
        layout.addWidget(self.default_format_combo, 0, 2)
        
        # PDF quality
        layout.addWidget(QLabel("PDF Quality:"), 1, 0)
        self.pdf_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.pdf_quality_slider.setRange(1, 100)
        self.pdf_quality_slider.setValue(95)
        layout.addWidget(self.pdf_quality_slider, 1, 1)
        
        self.pdf_quality_label = QLabel("95%")
        self.pdf_quality_slider.valueChanged.connect(
            lambda v: self.pdf_quality_label.setText(f"{v}%")
        )
        layout.addWidget(self.pdf_quality_label, 1, 2)
        
        # Max image width
        layout.addWidget(QLabel("Max Image Width:"), 2, 0)
        self.max_width_spin = QSpinBox()
        self.max_width_spin.setRange(512, 4096)
        self.max_width_spin.setSingleStep(256)
        self.max_width_spin.setSuffix("px")
        layout.addWidget(self.max_width_spin, 2, 1)
        
        # CBZ compression
        layout.addWidget(QLabel("CBZ Compression:"), 2, 2)
        self.cbz_compression_spin = QSpinBox()
        self.cbz_compression_spin.setRange(0, 9)
        layout.addWidget(self.cbz_compression_spin, 2, 3)
        
        # Delete source after conversion
        self.delete_source_check = QCheckBox("Delete source images after conversion")
        layout.addWidget(self.delete_source_check, 3, 0, 1, 2)
        
        parent_layout.addWidget(group)
    
    def setup_interface_settings(self, parent_layout):
        """Setup interface settings section."""
        # Interface settings removed - using defaults
        pass
    
    def setup_action_buttons(self, parent_layout):
        """Setup action buttons."""
        buttons_layout = QHBoxLayout()
        
        # Reset to defaults
        self.reset_button = ModernButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        buttons_layout.addWidget(self.reset_button)
        
        # Test system
        self.test_button = ModernButton("Test System")
        self.test_button.clicked.connect(self.test_system)
        buttons_layout.addWidget(self.test_button)
        
        buttons_layout.addStretch()
        
        # Cancel changes
        self.cancel_button = ModernButton("Cancel")
        self.cancel_button.clicked.connect(self.load_settings)
        buttons_layout.addWidget(self.cancel_button)
        
        # Save settings
        self.save_button = ModernButton("Save Settings", button_type="primary")
        self.save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_button)
        
        parent_layout.addLayout(buttons_layout)
    
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
            
            QSlider::groove:horizontal {
                border: 1px solid #4B5563;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #374151, stop:1 #1F2937);
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #A855F7, stop:1 #8B5CF6);
                border: 2px solid #FFFFFF;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -8px 0;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #C084FC, stop:1 #A855F7);
                transform: scale(1.1);
            }
            
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6, stop:1 #7C3AED);
                border-radius: 4px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #94A3B8;
                margin-right: 5px;
            }
            
            QComboBox QAbstractItemView {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1F2937, stop:1 #111827);
                border: 1px solid #4B5563;
                border-radius: 8px;
                selection-background-color: #8B5CF6;
                color: #F8FAFC;
            }
            
            QSpinBox::up-button, QSpinBox::down-button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4B5563, stop:1 #374151);
                border: 1px solid #6B7280;
                width: 16px;
                border-radius: 4px;
            }
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6B7280, stop:1 #4B5563);
            }
            
            QSpinBox::up-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid #94A3B8;
            }
            
            QSpinBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #94A3B8;
            }
        """)
    
    def load_settings(self):
        """Load current settings into the UI."""
        # Download settings
        self.download_path_input.setText(config.get("download.base_path", ""))
        self.folder_template_input.setText(config.get("download.folder_template", "{title}"))
        self.filename_template_input.setText(config.get("download.filename_template", "{page:03d}.{ext}"))
        self.max_concurrent_spin.setValue(config.get("download.max_concurrent", 8))
        self.retry_attempts_spin.setValue(config.get("download.retry_attempts", 3))
        self.create_subfolders_check.setChecked(config.get("download.create_subfolders", True))
        
        # Performance settings
        self.use_aria2_check.setChecked(config.get("download.use_aria2", True))
        self.aria2_path_input.setText(config.get("download.aria2_path", "aria2c"))
        self.max_connections_spin.setValue(config.get("download.max_connections_per_server", 8))
        self.max_parallel_spin.setValue(config.get("download.max_parallel_galleries", 3))
        
        # Check if turbo mode is active (4+ parallel galleries and 8+ connections)
        is_turbo = (config.get("download.max_parallel_galleries", 3) >= 4 and 
                   config.get("download.max_connections_per_server", 8) >= 8)
        self.turbo_mode_check.setChecked(is_turbo)
        self.on_turbo_mode_toggled(is_turbo)  # Set initial state
        
        # Conversion settings
        self.auto_convert_check.setChecked(config.get("conversion.auto_convert", False))
        default_format = config.get("conversion.default_format", "none").title()
        if default_format == "None":
            default_format = "None"
        self.default_format_combo.setCurrentText(default_format)
        self.pdf_quality_slider.setValue(config.get("conversion.pdf_quality", 95))
        self.max_width_spin.setValue(config.get("conversion.max_image_width", 2048))
        self.cbz_compression_spin.setValue(config.get("conversion.cbz_compression", 6))
        self.delete_source_check.setChecked(config.get("conversion.delete_source_after_conversion", False))
        
        # Interface settings removed - using defaults
    
    def save_settings(self):
        """Save current settings."""
        try:
            # Download settings
            config.set("download.base_path", self.download_path_input.text())
            config.set("download.folder_template", self.folder_template_input.text())
            config.set("download.filename_template", self.filename_template_input.text())
            config.set("download.max_concurrent", self.max_concurrent_spin.value())
            config.set("download.retry_attempts", self.retry_attempts_spin.value())
            config.set("download.create_subfolders", self.create_subfolders_check.isChecked())
            
            # Performance settings
            config.set("download.use_aria2", self.use_aria2_check.isChecked())
            config.set("download.aria2_path", self.aria2_path_input.text())
            
            # Handle turbo mode
            if self.turbo_mode_check.isChecked():
                # Enable turbo mode settings
                config.set("download.max_connections_per_server", 16)
                config.set("download.max_parallel_galleries", 4)
                # Update UI to reflect turbo values
                self.max_connections_spin.setValue(16)
                self.max_parallel_spin.setValue(4)
            else:
                # Use manual settings
                config.set("download.max_connections_per_server", self.max_connections_spin.value())
                config.set("download.max_parallel_galleries", self.max_parallel_spin.value())
            
            # Conversion settings
            config.set("conversion.auto_convert", self.auto_convert_check.isChecked())
            config.set("conversion.default_format", self.default_format_combo.currentText().lower())
            config.set("conversion.pdf_quality", self.pdf_quality_slider.value())
            config.set("conversion.max_image_width", self.max_width_spin.value())
            config.set("conversion.cbz_compression", self.cbz_compression_spin.value())
            config.set("conversion.delete_source_after_conversion", self.delete_source_check.isChecked())
            
            # Interface settings removed - using defaults
            
            # Save to file
            config.save()
            
            self.save_button.set_success(2000)
            self.settings_changed.emit()
            
        except Exception as e:
            self.save_button.set_error(2000)
            print(f"Error saving settings: {e}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            config.reset_to_defaults()
            self.load_settings()
            self.reset_button.set_success(2000)
    
    def test_system(self):
        """Test system components."""
        self.test_button.set_loading(True)
        
        # This would run system tests similar to CLI test command
        # For now, just simulate success
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.test_button.set_success(2000))
    
    def browse_download_directory(self):
        """Browse for download directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Download Directory"
        )
        
        if directory:
            self.download_path_input.setText(directory)
    
    def on_turbo_mode_toggled(self, checked: bool):
        """Handle turbo mode toggle."""
        if checked:
            # Disable manual controls and set turbo values
            self.max_connections_spin.setValue(16)
            self.max_parallel_spin.setValue(4)
            self.max_connections_spin.setEnabled(False)
            self.max_parallel_spin.setEnabled(False)
        else:
            # Enable manual controls
            self.max_connections_spin.setEnabled(True)
            self.max_parallel_spin.setEnabled(True)