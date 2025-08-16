"""Enhanced display utilities for interactive CLI mode."""

from typing import List, Optional, Any, Callable
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.prompt import Prompt, Confirm

from core.sites.base import GalleryInfo


class InteractiveMenu:
    """Base class for interactive menus."""
    
    def __init__(self, console: Console, title: str):
        self.console = console
        self.title = title
        self.running = True
    
    def show(self):
        """Show the menu and handle user interaction."""
        while self.running:
            self._display_menu()
            choice = self._get_choice()
            if choice is not None:
                self._handle_choice(choice)
    
    def _display_menu(self):
        """Display the menu. Override in subclasses."""
        pass
    
    def _get_choice(self) -> Optional[int]:
        """Get user choice. Override in subclasses."""
        pass
    
    def _handle_choice(self, choice: int):
        """Handle user choice. Override in subclasses."""
        pass
    
    def _pause(self):
        """Pause for user input."""
        try:
            self.console.input("\nPress Enter to continue...")
            self.console.print()
        except KeyboardInterrupt:
            raise


class InputValidator:
    """Utility class for validating user inputs."""
    
    @staticmethod
    def get_url(console: Console, prompt: str = "Enter gallery URL") -> Optional[str]:
        """Get and validate a URL input."""
        from core.sites.hentaifox import HentaiFoxSite
        
        site = HentaiFoxSite()
        
        while True:
            try:
                url = Prompt.ask(prompt).strip()
                
                if not url:
                    return None
                
                if url.lower() in ['q', 'quit', 'cancel', 'back']:
                    return None
                
                if site.is_valid_url(url):
                    return url
                else:
                    console.print("❌ Invalid HentaiFox URL. Please try again.", style="red")
                    
            except KeyboardInterrupt:
                return None
    
    @staticmethod
    def get_integer(console: Console, prompt: str, min_val: int = 1, max_val: int = 999) -> Optional[int]:
        """Get and validate an integer input."""
        while True:
            try:
                value_str = Prompt.ask(f"{prompt} [{min_val}-{max_val}]").strip()
                
                if not value_str:
                    return None
                
                if value_str.lower() in ['q', 'quit', 'cancel', 'back']:
                    return None
                
                value = int(value_str)
                
                if min_val <= value <= max_val:
                    return value
                else:
                    console.print(f"❌ Please enter a number between {min_val} and {max_val}", style="red")
                    
            except ValueError:
                console.print("❌ Please enter a valid number", style="red")
            except KeyboardInterrupt:
                return None
    
    @staticmethod
    def get_choice(console: Console, prompt: str, min_choice: int, max_choice: int) -> Optional[int]:
        """Get a menu choice with validation."""
        while True:
            try:
                choice_str = Prompt.ask(f"{prompt} [{min_choice}-{max_choice}]").strip()
                
                if not choice_str:
                    return None
                
                if choice_str.lower() in ['q', 'quit', 'cancel', 'back']:
                    return None
                
                choice = int(choice_str)
                
                if min_choice <= choice <= max_choice:
                    return choice
                else:
                    console.print(f"❌ Please enter a number between {min_choice} and {max_choice}", style="red")
                    
            except ValueError:
                console.print("❌ Please enter a valid number", style="red")
            except KeyboardInterrupt:
                return None
    
    @staticmethod
    def get_string(console: Console, prompt: str, required: bool = True) -> Optional[str]:
        """Get a string input with validation."""
        while True:
            try:
                value = Prompt.ask(prompt).strip()
                
                if value.lower() in ['q', 'quit', 'cancel', 'back']:
                    return None
                
                if value or not required:
                    return value if value else None
                else:
                    console.print("❌ This field is required", style="red")
                    
            except KeyboardInterrupt:
                return None


class StatusDisplay:
    """Utility class for displaying status information."""
    
    @staticmethod
    def show_gallery_selection_help(console: Console):
        """Show help for gallery selection."""
        help_text = """
Selection Options:
• Single number: '3'
• Range: '1-5' 
• Multiple: '1,3,5'
• All: 'all'
• Cancel: 'none', 'q', or Enter
        """
        
        panel = Panel(
            help_text.strip(),
            title="Selection Help",
            border_style="blue",
            box=box.SIMPLE
        )
        console.print(panel)
    
    @staticmethod
    def show_search_results_table(console: Console, galleries: List[GalleryInfo]) -> Table:
        """Create a formatted table for search results."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", width=4, justify="center")
        table.add_column("ID", width=8)
        table.add_column("Title", min_width=50)
        table.add_column("Pages", width=8, justify="center")
        
        for i, gallery in enumerate(galleries, 1):
            title = gallery.title[:60] + "..." if len(gallery.title) > 60 else gallery.title
            pages = str(gallery.pages) if gallery.pages else "?"
            
            table.add_row(
                str(i),
                gallery.id,
                title,
                pages
            )
        
        return table
    
    @staticmethod
    def show_config_section(console: Console, section_name: str, config_data: dict):
        """Display a configuration section."""
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Setting", style="white", width=30)
        table.add_column("Value", style="yellow", width=30)
        table.add_column("Description", style="dim white")
        
        for key, value in config_data.items():
            # Format value for display
            if isinstance(value, bool):
                display_value = "✅ Enabled" if value else "❌ Disabled"
            elif isinstance(value, (int, float)):
                display_value = str(value)
            elif isinstance(value, str):
                display_value = value[:25] + "..." if len(str(value)) > 25 else str(value)
            else:
                display_value = str(value)
            
            # Add description based on key
            description = StatusDisplay._get_setting_description(key)
            
            table.add_row(key, display_value, description)
        
        panel = Panel(
            table,
            title=f"⚙️  {section_name} Settings",
            border_style="cyan"
        )
        console.print(panel)
    
    @staticmethod
    def _get_setting_description(key: str) -> str:
        """Get description for a configuration setting."""
        descriptions = {
            "base_path": "Download directory",
            "max_parallel_galleries": "Concurrent downloads",
            "max_connections_per_server": "Connections per server",
            "use_aria2": "Fast download engine",
            "auto_convert": "Auto-convert downloads",
            "default_format": "Conversion format",
            "delete_source_after_conversion": "Delete after convert",
            "pdf_quality": "PDF image quality",
            "cbz_quality": "CBZ image quality",
            "enable_history": "Track downloads",
            "show_progress": "Show progress bars",
            "use_colors": "Colored output"
        }
        return descriptions.get(key, "")


class HelpSystem:
    """Contextual help system for interactive mode."""
    
    @staticmethod
    def show_download_help(console: Console):
        """Show download help."""
        help_text = """
Download Options:
• Single Gallery: Download one gallery by URL
• Multiple Galleries: Download several galleries at once
• From File: Load URLs from a text file

Tips:
• URLs must be from HentaiFox
• Enable Turbo Mode for faster downloads
• Set auto-conversion to save time
• Check gallery info before downloading
        """
        
        panel = Panel(
            help_text.strip(),
            title="Download Help",
            border_style="green"
        )
        console.print(panel)
    
    @staticmethod
    def show_search_help(console: Console):
        """Show search help."""
        help_text = """
Search Types:
• Query Search: Search by title or content
• Tag Search: Search by specific tags
• Advanced: Multi-page searches

Selection:
• Choose specific galleries to download
• Use ranges for multiple selections
• Preview gallery info before downloading
        """
        
        panel = Panel(
            help_text.strip(),
            title="Search Help", 
            border_style="green"
        )
        console.print(panel)
    
    @staticmethod
    def show_conversion_help(console: Console):
        """Show conversion help."""
        help_text = """
Conversion Formats:
• PDF: Universal format, great for reading
• CBZ: Comic book format for comic readers

Options:
• Quality: 1-100 (higher = better quality)
• Delete Source: Remove original images
• Auto-Convert: Convert all future downloads
        """
        
        panel = Panel(
            help_text.strip(),
            title="Conversion Help",
            border_style="green"
        )
        console.print(panel)