"""Modern progress widget with animations."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QFont, QPainter, QPen, QBrush, QColor
# Removed theme manager - using simple styling


class ModernProgressBar(QProgressBar):
    """Custom progress bar with smooth animations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Using simple black theme
        self._animated_value = 0
        
        # Animation for smooth progress updates
        self.value_animation = QPropertyAnimation(self, b"animated_value")
        self.value_animation.setDuration(300)
        self.value_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #3d3d3d;
                text-align: center;
                font-weight: 500;
                height: 16px;
                color: #ffffff;
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #bb86fc,
                    stop:1 #03dac6);
            }
        """)
    
    @pyqtProperty(float)
    def animated_value(self):
        return self._animated_value
    
    @animated_value.setter
    def animated_value(self, value):
        self._animated_value = value
        super().setValue(int(value))
    
    def setValue(self, value):
        """Set value with smooth animation."""
        self.value_animation.setStartValue(self._animated_value)
        self.value_animation.setEndValue(value)
        self.value_animation.start()


class ProgressWidget(QWidget):
    """Modern progress widget with status and animations."""
    
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Using simple black theme
        self.setup_ui()
        
        # Animation timer for pulse effect (will be created when needed)
        self.pulse_timer = None
        self.pulse_opacity = 1.0
        self.pulse_direction = -1
    
    def setup_ui(self):
        """Setup the progress widget UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Title label
        self.title_label = QLabel("Processing...")
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.title_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.title_label)
        
        # Progress bar
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Status layout
        status_layout = QHBoxLayout()
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setStyleSheet("color: #b3b3b3;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Speed label
        self.speed_label = QLabel("")
        self.speed_label.setFont(QFont("Segoe UI", 9))
        self.speed_label.setStyleSheet("color: #b3b3b3;")
        status_layout.addWidget(self.speed_label)
        
        layout.addLayout(status_layout)
        
        # Details layout
        details_layout = QHBoxLayout()
        
        # Files count
        self.files_label = QLabel("")
        self.files_label.setFont(QFont("Segoe UI", 8))
        self.files_label.setStyleSheet("color: #666666;")
        details_layout.addWidget(self.files_label)
        
        details_layout.addStretch()
        
        # Time remaining
        self.time_label = QLabel("")
        self.time_label.setFont(QFont("Segoe UI", 8))
        self.time_label.setStyleSheet("color: #666666;")
        details_layout.addWidget(self.time_label)
        
        layout.addLayout(details_layout)
        
        # Apply styling
        self.setStyleSheet("""
            ProgressWidget {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 12px;
            }
        """)
    
    def set_title(self, title: str):
        """Set the progress title."""
        self.title_label.setText(title)
    
    def set_progress(self, value: int, maximum: int = 100):
        """Set progress value with animation."""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
    
    def set_status(self, status: str):
        """Set the status text."""
        self.status_label.setText(status)
    
    def set_speed(self, speed: str):
        """Set the speed text."""
        self.speed_label.setText(speed)
    
    def set_files_info(self, current: int, total: int):
        """Set files information."""
        self.files_label.setText(f"Files: {current}/{total}")
    
    def set_time_remaining(self, time_str: str):
        """Set time remaining."""
        self.time_label.setText(f"ETA: {time_str}")
    
    def set_indeterminate(self, indeterminate: bool = True):
        """Set indeterminate progress mode."""
        if indeterminate:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
            self.start_pulse()
        else:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
            self.stop_pulse()
    
    def start_pulse(self):
        """Start pulse animation for indeterminate progress."""
        if self.pulse_timer is None:
            self.pulse_timer = QTimer()
            self.pulse_timer.timeout.connect(self.pulse_animation)
        self.pulse_timer.start(50)
    
    def stop_pulse(self):
        """Stop pulse animation."""
        if self.pulse_timer is not None:
            self.pulse_timer.stop()
        self.opacity = 1.0
    
    def pulse_animation(self):
        """Animate pulse effect."""
        self.pulse_opacity += self.pulse_direction * 0.02
        
        if self.pulse_opacity <= 0.6:
            self.pulse_direction = 1
        elif self.pulse_opacity >= 1.0:
            self.pulse_direction = -1
        
        self.opacity = self.pulse_opacity
    
    def set_complete(self):
        """Set progress to complete state."""
        self.set_progress(100)
        self.set_status("Complete!")
        self.stop_pulse()
        
        # Flash success color
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #3d3d3d;
                text-align: center;
                font-weight: 500;
                height: 16px;
                color: #ffffff;
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background-color: #4caf50;
            }
        """)
    
    def set_error(self, error_message: str):
        """Set progress to error state."""
        self.set_status(f"Error: {error_message}")
        self.stop_pulse()
        
        # Flash error color
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #3d3d3d;
                text-align: center;
                font-weight: 500;
                height: 16px;
                color: #ffffff;
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background-color: #cf6679;
            }
        """)