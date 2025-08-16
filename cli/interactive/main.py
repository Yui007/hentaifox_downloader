"""Main interactive CLI for HentaiFox Downloader."""

import sys
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from cli.utils.display import display
from config.settings import config
from core.downloader import GalleryDLDownloader


class InteractiveCLI:
    """Main interactive CLI interface."""
    
    def __init__(self):
        self.console = Console()
        self.running = True
        self.menu_stack = []
        self.session_data = {}
        
    def run(self):
        """Start the interactive CLI."""
        try:
            self._show_welcome()
            self._check_system_status()
            
            while self.running:
                self._show_main_menu()
                choice = self._get_menu_choice(1, 8)
                
                if choice:
                    self._handle_main_menu_choice(choice)
                    
        except KeyboardInterrupt:
            self._handle_exit()
        except Exception as e:
            display.print_error(f"Unexpected error: {e}")
            self._handle_exit()
    
    def _show_welcome(self):
        """Display welcome banner."""
        banner = Text()
        banner.append("🎯 HentaiFox Downloader", style="bold magenta")
        banner.append(" Interactive Mode", style="bold white")
        
        panel = Panel(
            banner,
            subtitle="Menu-driven interface for manga downloading",
            border_style="magenta",
            box=box.DOUBLE
        )
        self.console.print(panel)
        self.console.print()
    
    def _check_system_status(self):
        """Check and display system status."""
        status_items = []
        
        # Check gallery-dl
        downloader = GalleryDLDownloader()
        if downloader.check_gallery_dl_available():
            status_items.append("✅ gallery-dl")
        else:
            status_items.append("❌ gallery-dl")
        
        # Check aria2c
        if downloader._check_aria2_available():
            status_items.append("✅ aria2c")
        else:
            status_items.append("⚠️  aria2c (optional)")
        
        # Check config
        status_items.append("✅ Config loaded")
        
        # Check performance mode
        parallel_galleries = config.get("download.max_parallel_galleries", 2)
        is_turbo = parallel_galleries >= 4
        perf_status = "🚀 TURBO MODE" if is_turbo else "🐌 NORMAL MODE"
        
        status_text = " | ".join(status_items)
        self.console.print(f"System Status: {status_text}")
        self.console.print(f"Performance: {perf_status}")
        self.console.print()
    
    def _show_main_menu(self):
        """Display the main menu."""
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Option", style="cyan", width=3)
        table.add_column("Description", style="white")
        
        menu_items = [
            ("1", "📥 Download Galleries"),
            ("2", "🔍 Search & Browse"),
            ("3", "📚 Convert Files"),
            ("4", "⚙️  Configuration"),
            ("5", "📊 History & Stats"),
            ("6", "🚀 Performance Settings"),
            ("7", "❓ Help & About"),
            ("8", "🚪 Exit")
        ]
        
        for option, description in menu_items:
            table.add_row(option, description)
        
        panel = Panel(
            table,
            title="Main Menu",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _get_menu_choice(self, min_choice: int, max_choice: int) -> Optional[int]:
        """Get user menu choice with validation."""
        try:
            choice_str = self.console.input(f"Enter your choice [{min_choice}-{max_choice}]: ").strip()
            
            if not choice_str:
                return None
                
            choice = int(choice_str)
            
            if min_choice <= choice <= max_choice:
                return choice
            else:
                display.print_error(f"Please enter a number between {min_choice} and {max_choice}")
                return None
                
        except ValueError:
            display.print_error("Please enter a valid number")
            return None
        except KeyboardInterrupt:
            raise
    
    def _handle_main_menu_choice(self, choice: int):
        """Handle main menu selection."""
        self.console.print()
        
        if choice == 1:
            self._handle_download_menu()
        elif choice == 2:
            self._handle_search_menu()
        elif choice == 3:
            self._handle_convert_menu()
        elif choice == 4:
            self._handle_config_menu()
        elif choice == 5:
            self._handle_history_menu()
        elif choice == 6:
            self._handle_performance_menu()
        elif choice == 7:
            self._show_help()
        elif choice == 8:
            self._handle_exit()
    
    def _handle_download_menu(self):
        """Handle download menu."""
        from .download import DownloadMenu
        download_menu = DownloadMenu(self.console)
        download_menu.show()
    
    def _handle_search_menu(self):
        """Handle search menu."""
        from .search import SearchMenu
        search_menu = SearchMenu(self.console)
        search_menu.show()
    
    def _handle_convert_menu(self):
        """Handle conversion menu."""
        from .convert import ConvertMenu
        convert_menu = ConvertMenu(self.console)
        convert_menu.show()
    
    def _handle_config_menu(self):
        """Handle configuration menu."""
        from .config import ConfigMenu
        config_menu = ConfigMenu(self.console)
        config_menu.show()
    
    def _handle_history_menu(self):
        """Handle history menu."""
        from .history import HistoryMenu
        history_menu = HistoryMenu(self.console)
        history_menu.show()
    
    def _handle_performance_menu(self):
        """Handle performance menu."""
        self._show_performance_menu()
    
    def _show_performance_menu(self):
        """Show performance settings menu."""
        while True:
            table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
            table.add_column("Option", style="cyan", width=3)
            table.add_column("Description", style="white")
            
            # Show current status
            parallel_galleries = config.get("download.max_parallel_galleries", 2)
            connections = config.get("download.max_connections_per_server", 4)
            is_turbo = parallel_galleries >= 4
            
            current_mode = "🚀 TURBO" if is_turbo else "🐌 NORMAL"
            
            table.add_row("", f"Current Mode: {current_mode}")
            table.add_row("", f"Parallel Galleries: {parallel_galleries}")
            table.add_row("", f"Connections per Server: {connections}")
            table.add_row("", "")
            table.add_row("1", "🚀 Enable Turbo Mode")
            table.add_row("2", "🐌 Enable Normal Mode")
            table.add_row("3", "📊 Show Detailed Status")
            table.add_row("4", "🔙 Back to Main Menu")
            
            panel = Panel(table, title="Performance Settings", border_style="yellow")
            self.console.print(panel)
            
            choice = self._get_menu_choice(1, 4)
            if choice == 1:
                self._enable_turbo_mode()
            elif choice == 2:
                self._enable_normal_mode()
            elif choice == 3:
                self._show_detailed_performance()
            elif choice == 4:
                break
            
            self.console.print()
    
    def _enable_turbo_mode(self):
        """Enable turbo mode."""
        from cli.commands.performance import enable_turbo_mode
        enable_turbo_mode()
        self._pause()
    
    def _enable_normal_mode(self):
        """Enable normal mode."""
        from cli.commands.performance import disable_turbo_mode
        disable_turbo_mode()
        self._pause()
    
    def _show_detailed_performance(self):
        """Show detailed performance status."""
        from cli.commands.performance import show_performance_status
        show_performance_status()
        self._pause()
    
    def _show_help(self):
        """Show help information."""
        help_text = """
🎯 HentaiFox Downloader Interactive Mode Help

Navigation:
• Use number keys to select menu options
• Press Ctrl+C to exit at any time
• Most menus have a 'Back' option to return

Features:
• Download: Single or batch gallery downloads
• Search: Find galleries by query or tag
• Convert: Transform downloads to PDF/CBZ
• Config: Adjust all application settings
• History: View download history and stats
• Performance: Optimize download speeds

Tips:
• Enable Turbo Mode for faster downloads
• Set auto-conversion to save time
• Use search to discover new content
• Check history to avoid re-downloads

For detailed documentation, see:
• README.md - Project overview
• usage.md - Complete usage guide
• PERFORMANCE_GUIDE.md - Speed optimization
        """
        
        panel = Panel(
            help_text.strip(),
            title="Help & About",
            border_style="green"
        )
        self.console.print(panel)
        self._pause()
    
    def _handle_exit(self):
        """Handle application exit."""
        display.print_info("Thanks for using HentaiFox Downloader! 👋")
        self.running = False
        sys.exit(0)
    
    def _pause(self):
        """Pause for user input."""
        try:
            self.console.input("\nPress Enter to continue...")
            self.console.print()
        except KeyboardInterrupt:
            raise