"""Interactive download menu for HentaiFox Downloader."""

from typing import List, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Confirm

from cli.utils.interactive_display import InteractiveMenu, InputValidator, HelpSystem
from cli.utils.display import display
from core.sites.hentaifox import HentaiFoxSite
from config.settings import config


class DownloadMenu(InteractiveMenu):
    """Interactive download menu."""
    
    def __init__(self, console: Console):
        super().__init__(console, "Download Menu")
        self.site = HentaiFoxSite()
    
    def _display_menu(self):
        """Display the download menu."""
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Option", style="cyan", width=3)
        table.add_column("Description", style="white")
        
        menu_items = [
            ("1", "📥 Download Single Gallery"),
            ("2", "📦 Download Multiple Galleries"),
            ("3", "📄 Download from File (URLs list)"),
            ("4", "ℹ️  Gallery Info (no download)"),
            ("5", "⚙️  Download Settings"),
            ("6", "❓ Help"),
            ("7", "🔙 Back to Main Menu")
        ]
        
        for option, description in menu_items:
            table.add_row(option, description)
        
        panel = Panel(
            table,
            title="📥 Download Menu",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _get_choice(self) -> Optional[int]:
        """Get user menu choice."""
        return InputValidator.get_choice(self.console, "Enter your choice", 1, 7)
    
    def _handle_choice(self, choice: int):
        """Handle user menu choice."""
        self.console.print()
        
        if choice == 1:
            self._download_single_gallery()
        elif choice == 2:
            self._download_multiple_galleries()
        elif choice == 3:
            self._download_from_file()
        elif choice == 4:
            self._show_gallery_info()
        elif choice == 5:
            self._show_download_settings()
        elif choice == 6:
            HelpSystem.show_download_help(self.console)
            self._pause()
        elif choice == 7:
            self.running = False
    
    def _download_single_gallery(self):
        """Handle single gallery download."""
        url = InputValidator.get_url(self.console, "Enter gallery URL")
        
        if not url:
            display.print_info("Download cancelled.")
            self._pause()
            return
        
        # Get gallery info first
        display.print_info("Fetching gallery information...")
        gallery_info = self.site.get_gallery_info(url)
        
        if not gallery_info:
            display.print_error("Could not fetch gallery information.")
            self._pause()
            return
        
        # Show gallery info
        display.print_gallery_info(gallery_info)
        
        # Get download options
        options = self._get_download_options()
        if not options:
            display.print_info("Download cancelled.")
            self._pause()
            return
        
        # Confirm download
        if not Confirm.ask("Proceed with download?"):
            display.print_info("Download cancelled.")
            self._pause()
            return
        
        # Perform download
        self._execute_single_download(url, gallery_info, options)
        self._pause()
    
    def _download_multiple_galleries(self):
        """Handle multiple gallery downloads."""
        urls = []
        
        self.console.print("Enter gallery URLs (one per line, empty line to finish):")
        
        while True:
            url = InputValidator.get_url(self.console, f"URL #{len(urls) + 1} (or Enter to finish)")
            
            if not url:
                break
            
            urls.append(url)
            display.print_success(f"Added: {url}")
        
        if not urls:
            display.print_info("No URLs entered.")
            self._pause()
            return
        
        display.print_info(f"Total URLs: {len(urls)}")
        
        # Get download options
        options = self._get_download_options()
        if not options:
            display.print_info("Download cancelled.")
            self._pause()
            return
        
        # Confirm download
        if not Confirm.ask(f"Download {len(urls)} galleries?"):
            display.print_info("Download cancelled.")
            self._pause()
            return
        
        # Perform downloads
        self._execute_multiple_downloads(urls, options)
        self._pause()
    
    def _download_from_file(self):
        """Handle download from file."""
        file_path = InputValidator.get_string(self.console, "Enter file path with URLs")
        
        if not file_path:
            display.print_info("Download cancelled.")
            self._pause()
            return
        
        # Read URLs from file
        try:
            path = Path(file_path)
            if not path.exists():
                display.print_error(f"File not found: {file_path}")
                self._pause()
                return
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            urls = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if self.site.is_valid_url(line):
                        urls.append(line)
                    else:
                        display.print_warning(f"Invalid URL on line {line_num}: {line}")
            
            if not urls:
                display.print_error("No valid URLs found in file.")
                self._pause()
                return
            
            display.print_info(f"Found {len(urls)} valid URLs in file.")
            
            # Get download options
            options = self._get_download_options()
            if not options:
                display.print_info("Download cancelled.")
                self._pause()
                return
            
            # Confirm download
            if not Confirm.ask(f"Download {len(urls)} galleries from file?"):
                display.print_info("Download cancelled.")
                self._pause()
                return
            
            # Perform downloads
            self._execute_multiple_downloads(urls, options)
            
        except Exception as e:
            display.print_error(f"Error reading file: {e}")
        
        self._pause()
    
    def _show_gallery_info(self):
        """Show gallery info without downloading."""
        url = InputValidator.get_url(self.console, "Enter gallery URL")
        
        if not url:
            display.print_info("Cancelled.")
            self._pause()
            return
        
        display.print_info("Fetching gallery information...")
        gallery_info = self.site.get_gallery_info(url)
        
        if gallery_info:
            display.print_gallery_info(gallery_info)
        else:
            display.print_error("Could not fetch gallery information.")
        
        self._pause()
    
    def _get_download_options(self) -> Optional[dict]:
        """Get download options from user."""
        options = {
            'convert_format': None,
            'delete_images': False,
            'custom_output': None
        }
        
        # Conversion options
        if Confirm.ask("Configure conversion options?", default=False):
            format_choice = InputValidator.get_choice(
                self.console, 
                "Conversion format: 1=None, 2=PDF, 3=CBZ", 
                1, 3
            )
            
            if format_choice == 2:
                options['convert_format'] = 'pdf'
            elif format_choice == 3:
                options['convert_format'] = 'cbz'
            
            if options['convert_format']:
                options['delete_images'] = Confirm.ask("Delete images after conversion?", default=False)
        
        # Output directory
        if Confirm.ask("Use custom output directory?", default=False):
            custom_dir = InputValidator.get_string(self.console, "Enter output directory", required=False)
            if custom_dir:
                options['custom_output'] = custom_dir
        
        return options
    
    def _execute_single_download(self, url: str, gallery_info, options: dict):
        """Execute single gallery download."""
        from cli.commands.download import download_gallery
        
        try:
            download_gallery(
                url=url,
                output_dir=options.get('custom_output'),
                force=False,
                metadata=True,
                convert_to=options.get('convert_format'),
                delete_images=options.get('delete_images', False)
            )
        except Exception as e:
            display.print_error(f"Download failed: {e}")
    
    def _execute_multiple_downloads(self, urls: List[str], options: dict):
        """Execute multiple gallery downloads."""
        from cli.commands.download import download_multiple
        
        try:
            download_multiple(
                urls=urls,
                output_dir=options.get('custom_output'),
                continue_on_error=True
            )
        except Exception as e:
            display.print_error(f"Batch download failed: {e}")
    
    def _show_download_settings(self):
        """Show current download settings."""
        from cli.utils.interactive_display import StatusDisplay
        
        download_config = {
            "base_path": config.get("download.base_path"),
            "max_parallel_galleries": config.get("download.max_parallel_galleries", 2),
            "max_connections_per_server": config.get("download.max_connections_per_server", 4),
            "use_aria2": config.get("download.use_aria2", True),
            "retry_attempts": config.get("download.retry_attempts", 3)
        }
        
        StatusDisplay.show_config_section(self.console, "Download", download_config)
        self._pause()