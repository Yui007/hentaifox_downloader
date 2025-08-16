"""Modern animated button widget with beautiful styling."""

from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer, pyqtProperty, QRect, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QLinearGradient, QPainterPath
import math


class ModernButton(QPushButton):
    """Ultra-modern button with gradient backgrounds, smooth animations, and ripple effects."""
    
    clicked_animated = pyqtSignal()
    
    def __init__(self, text="", parent=None, button_type="default"):
        super().__init__(text, parent)
        self.button_type = button_type
        
        # Animation properties
        self._hover_progress = 0.0
        self._press_progress = 0.0
        self._ripple_progress = 0.0
        self._ripple_x = 0
        self._ripple_y = 0
        
        # Setup animations
        self.hover_animation = QPropertyAnimation(self, b"hover_progress")
        self.hover_animation.setDuration(300)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.press_animation = QPropertyAnimation(self, b"press_progress")
        self.press_animation.setDuration(150)
        self.press_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.ripple_animation = QPropertyAnimation(self, b"ripple_progress")
        self.ripple_animation.setDuration(600)
        self.ripple_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Setup styling
        self.setup_styling()
        
        # Connect signals
        self.pressed.connect(self.on_pressed)
        self.released.connect(self.on_released)
        self.clicked.connect(self.on_clicked)
    
    def setup_styling(self):
        """Setup button styling based on type."""
        # Remove default button styling
        self.setFlat(True)
        
        # Set minimum size and padding
        self.setMinimumHeight(40)
        self.setMinimumWidth(100)
        
        # Add beautiful shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)
        
        # Set modern font
        font = QFont("Segoe UI", 10, QFont.Weight.Medium)
        self.setFont(font)
        
        # Apply base styling
        self.setStyleSheet(self.get_base_style())
    
    @pyqtProperty(float)
    def hover_progress(self):
        return self._hover_progress
    
    @hover_progress.setter
    def hover_progress(self, value):
        self._hover_progress = value
        self.update()
    
    @pyqtProperty(float)
    def press_progress(self):
        return self._press_progress
    
    @press_progress.setter
    def press_progress(self, value):
        self._press_progress = value
        self.update()
    
    @pyqtProperty(float)
    def ripple_progress(self):
        return self._ripple_progress
    
    @ripple_progress.setter
    def ripple_progress(self, value):
        self._ripple_progress = value
        self.update()
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        super().enterEvent(event)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        super().leaveEvent(event)
        self.hover_animation.setEndValue(0.0)
        self.hover_animation.start()
    
    def on_pressed(self):
        """Handle button press."""
        self.press_animation.setEndValue(1.0)
        self.press_animation.start()
    
    def on_released(self):
        """Handle button release."""
        self.press_animation.setEndValue(0.0)
        self.press_animation.start()
    
    def on_clicked(self):
        """Handle button click with ripple effect."""
        # Start ripple from center
        self._ripple_x = self.width() // 2
        self._ripple_y = self.height() // 2
        
        self.ripple_animation.setStartValue(0.0)
        self.ripple_animation.setEndValue(1.0)
        self.ripple_animation.start()
        
        # Emit custom signal after animation
        QTimer.singleShot(100, self.clicked_animated.emit)
    
    def paintEvent(self, event):
        """Custom paint event with beautiful gradients and animations."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get button rect
        rect = self.rect()
        
        # Create rounded rectangle path
        path = QPainterPath()
        radius = 12
        # Convert QRect to QRectF for addRoundedRect
        rectf = QRectF(rect)
        path.addRoundedRect(rectf, radius, radius)
        
        # Create gradient based on button type and state
        gradient = self.create_gradient(rect)
        
        # Apply hover and press effects
        if self._hover_progress > 0 or self._press_progress > 0:
            # Modify gradient for hover/press
            gradient = self.modify_gradient_for_state(gradient)
        
        # Draw button background
        painter.fillPath(path, QBrush(gradient))
        
        # Draw border
        border_color = self.get_border_color()
        painter.setPen(QPen(border_color, 1))
        painter.drawPath(path)
        
        # Draw ripple effect
        if self._ripple_progress > 0:
            self.draw_ripple_effect(painter, rect)
        
        # Draw text
        self.draw_text(painter, rect)
    
    def create_gradient(self, rect):
        """Create gradient based on button type."""
        gradient = QLinearGradient(0, 0, 0, rect.height())
        
        if self.button_type == "primary":
            # Beautiful purple gradient
            gradient.setColorAt(0, QColor('#8B5CF6'))  # Purple 500
            gradient.setColorAt(1, QColor('#7C3AED'))  # Purple 600
        elif self.button_type == "danger":
            # Beautiful red gradient
            gradient.setColorAt(0, QColor('#EF4444'))  # Red 500
            gradient.setColorAt(1, QColor('#DC2626'))  # Red 600
        elif self.button_type == "secondary":
            # Beautiful gray gradient
            gradient.setColorAt(0, QColor('#6B7280'))  # Gray 500
            gradient.setColorAt(1, QColor('#4B5563'))  # Gray 600
        else:
            # Default dark gradient
            gradient.setColorAt(0, QColor('#374151'))  # Gray 700
            gradient.setColorAt(1, QColor('#1F2937'))  # Gray 800
        
        return gradient
    
    def modify_gradient_for_state(self, gradient):
        """Modify gradient for hover/press states."""
        # Create a brighter version for hover/press
        new_gradient = QLinearGradient(gradient)
        
        # Make colors brighter
        colors = []
        positions = []
        
        # Extract colors and positions (simplified approach)
        if self.button_type == "primary":
            new_gradient.setColorAt(0, QColor('#A855F7'))  # Brighter purple
            new_gradient.setColorAt(1, QColor('#9333EA'))
        elif self.button_type == "danger":
            new_gradient.setColorAt(0, QColor('#F87171'))  # Brighter red
            new_gradient.setColorAt(1, QColor('#EF4444'))
        elif self.button_type == "secondary":
            new_gradient.setColorAt(0, QColor('#9CA3AF'))  # Brighter gray
            new_gradient.setColorAt(1, QColor('#6B7280'))
        else:
            new_gradient.setColorAt(0, QColor('#4B5563'))  # Brighter default
            new_gradient.setColorAt(1, QColor('#374151'))
        
        return new_gradient
    
    def get_border_color(self):
        """Get border color based on button type."""
        if self.button_type == "primary":
            return QColor('#A855F7')
        elif self.button_type == "danger":
            return QColor('#F87171')
        elif self.button_type == "secondary":
            return QColor('#9CA3AF')
        else:
            return QColor('#4B5563')
    
    def draw_ripple_effect(self, painter, rect):
        """Draw beautiful ripple effect."""
        # Calculate ripple radius
        max_radius = math.sqrt(rect.width()**2 + rect.height()**2) / 2
        radius = max_radius * self._ripple_progress
        
        # Create ripple color
        ripple_color = QColor(255, 255, 255, int(40 * (1 - self._ripple_progress)))
        
        # Draw ripple
        painter.setBrush(QBrush(ripple_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(self._ripple_x - radius),
            int(self._ripple_y - radius),
            int(radius * 2),
            int(radius * 2)
        )
    
    def draw_text(self, painter, rect):
        """Draw button text with proper styling."""
        # Set text color
        if self.isEnabled():
            text_color = QColor('#FFFFFF')
        else:
            text_color = QColor('#9CA3AF')
        
        painter.setPen(text_color)
        painter.setFont(self.font())
        
        # Draw text centered
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
    
    def get_base_style(self):
        """Get base stylesheet."""
        return """
            ModernButton {
                border: none;
                background: transparent;
                color: white;
                padding: 8px 16px;
                border-radius: 12px;
            }
            ModernButton:disabled {
                color: #9CA3AF;
            }
        """
    
    def set_loading(self, loading: bool):
        """Set button loading state."""
        if loading:
            if not hasattr(self, '_original_text'):
                self._original_text = self.text()
            self.setText("Loading...")
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            if hasattr(self, '_original_text'):
                self.setText(self._original_text)
                delattr(self, '_original_text')
    
    def set_success(self, duration: int = 2000):
        """Temporarily show success state."""
        if not hasattr(self, '_original_text'):
            self._original_text = self.text()
        self.setText("✓ Success")
        self.setProperty("success", True)
        self.setEnabled(True)  # Ensure button is enabled
        self.style().polish(self)
        
        QTimer.singleShot(duration, lambda: self.reset_state(self._original_text))
    
    def set_error(self, duration: int = 2000):
        """Temporarily show error state."""
        if not hasattr(self, '_original_text'):
            self._original_text = self.text()
        self.setText("✗ Error")
        self.setProperty("error", True)
        self.setEnabled(True)  # Ensure button is enabled
        self.style().polish(self)
        
        QTimer.singleShot(duration, lambda: self.reset_state(self._original_text))
    
    def reset_state(self, original_text: str = None):
        """Reset button to original state."""
        if original_text is None and hasattr(self, '_original_text'):
            original_text = self._original_text
        if original_text:
            self.setText(original_text)
        self.setProperty("success", False)
        self.setProperty("error", False)
        self.setEnabled(True)
        self.style().polish(self)
        # Clean up stored text
        if hasattr(self, '_original_text'):
            delattr(self, '_original_text')