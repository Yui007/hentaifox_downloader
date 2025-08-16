# HentaiFox Downloader GUI

A beautiful, modern GUI for the HentaiFox Downloader manga downloader built with PyQt6.

![HentaiFox Downloader GUI](screenshot.png)

*Modern interface with gradient backgrounds, purple accents, and smooth animations*

## Features

🎨 **Modern Dark Theme**
- Sleek dark interface with smooth animations
- Custom styled buttons, progress bars, and widgets
- Responsive design with hover effects and transitions

📥 **Download Manager**
- Drag & drop URL input with clipboard support
- Real-time progress tracking with speed and ETA
- Batch download support
- Automatic conversion to PDF/CBZ

🔍 **Search & Browse**
- Search galleries by title, tag, or artist
- Grid-based gallery cards with thumbnails
- Pagination support for large result sets
- Quick search presets (Popular, Recent)

📚 **History Tracking**
- Complete download history with statistics
- Search and filter capabilities
- Export to CSV functionality
- Context menu actions

⚙️ **Settings Management**
- Comprehensive settings panel
- Performance optimization controls
- Conversion quality settings
- Interface customization options

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Launch the GUI:
```bash
python gui_launcher.py
```

### Usage

1. **Download Tab**: Enter a HentaiFox URL and click Download
2. **Search Tab**: Search for galleries and browse results
3. **History Tab**: View your download history and statistics
4. **Settings Tab**: Configure download options and preferences

## Architecture

The GUI follows a modular architecture with strict 300-line file limits:

```
gui/
├── main.py              # Application entry point
├── windows/
│   └── main_window.py   # Main application window
├── tabs/
│   ├── download_tab.py  # Download management
│   ├── search_tab.py    # Search and browse
│   ├── history_tab.py   # Download history
│   └── settings_tab.py  # Configuration
├── widgets/
│   ├── modern_button.py # Animated buttons
│   ├── progress_widget.py # Progress displays
│   └── gallery_card.py  # Gallery information cards
├── workers/
│   ├── download_worker.py # Background downloads
│   └── search_worker.py   # Background search
└── utils/
    ├── theme.py         # Dark theme management
    └── animations.py    # UI animations
```

## Key Components

### Modern Button Widget
- Hover animations and ripple effects
- Loading, success, and error states
- Multiple button types (primary, secondary, danger)

### Progress Widget
- Smooth animated progress bars
- Real-time speed and ETA display
- Indeterminate progress support
- Pulse animations for loading states

### Gallery Card Widget
- Hover effects and smooth transitions
- Tag display and metadata
- Download and info action buttons
- Responsive card layout

### Theme Manager
- Consistent color palette
- Modern dark theme styling
- Customizable UI components
- Smooth color transitions

## Performance Features

- **Background Workers**: All downloads and searches run in separate threads
- **Smooth Animations**: Hardware-accelerated UI transitions
- **Efficient Updates**: Minimal UI redraws with smart caching
- **Memory Management**: Proper cleanup of widgets and threads

## Integration

The GUI seamlessly integrates with your existing CLI functionality:

- Uses the same `core/` modules for downloading
- Shares configuration with CLI via `config/settings.py`
- Maintains download history in the same database
- Supports all CLI features through the GUI interface

## Customization

The GUI is highly customizable through the Settings tab:

- **Download Options**: Paths, templates, concurrent downloads
- **Performance**: Aria2c integration, connection limits
- **Conversion**: Auto-convert, quality settings, formats
- **Interface**: Theme, animations, progress styles

## Development

The GUI follows the same development principles as the CLI:

- **Modular Design**: Each component is self-contained
- **300-Line Limit**: All files respect the hard line limit
- **Type Hints**: Full type annotation support
- **Error Handling**: Graceful error recovery and user feedback
- **Testing**: Unit testable components with dependency injection

Launch the GUI and enjoy a beautiful, modern interface for your manga downloads!