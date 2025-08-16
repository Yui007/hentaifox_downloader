#!/usr/bin/env python3
"""GUI launcher script for HentaiFox Downloader."""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Launch the GUI application."""
    try:
        from gui.main import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error importing GUI modules: {e}")
        print("Make sure PyQt6 is installed: pip install PyQt6")
        sys.exit(1)
    except Exception as e:
        print(f"Error launching GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()