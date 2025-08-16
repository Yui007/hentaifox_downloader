"""Rich-based display utilities for CLI."""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from typing import List, Optional

from core.sites.base import GalleryInfo, SearchResult


class CLIDisplay:
    """Rich-based display manager for CLI output."""
    
    def __init__(self):
        self.console = Console()
    
    def print_success(self, message: str):
        """Print success message."""
        self.console.print(f"✅ {message}", style="green")
    
    def print_error(self, message: str):
        """Print error message."""
        self.console.print(f"❌ {message}", style="red")
    
    def print_warning(self, message: str):
        """Print warning message."""
        self.console.print(f"⚠️  {message}", style="yellow")
    
    def print_info(self, message: str):
        """Print info message."""
        self.console.print(f"ℹ️  {message}", style="blue")
    
    def print_gallery_info(self, gallery: GalleryInfo):
        """Print detailed gallery information."""
        table = Table(show_header=False, box=box.ROUNDED)
        table.add_column("Field", style="cyan", width=12)
        table.add_column("Value", style="white")
        
        table.add_row("Title", gallery.title)
        table.add_row("ID", gallery.id)
        table.add_row("URL", gallery.url)
        
        if gallery.artist:
            table.add_row("Artist", gallery.artist)
        
        if gallery.pages:
            table.add_row("Pages", str(gallery.pages))
        
        if gallery.tags:
            tags_text = ", ".join(gallery.tags[:10])  # Show first 10 tags
            if len(gallery.tags) > 10:
                tags_text += f" (+{len(gallery.tags) - 10} more)"
            table.add_row("Tags", tags_text)
        
        panel = Panel(table, title="🎯 Gallery Information", border_style="blue")
        self.console.print(panel)
    
    def print_search_results(self, results: SearchResult):
        """Print search results in a table."""
        if not results.galleries:
            self.print_warning("No galleries found.")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", width=4, justify="center")
        table.add_column("ID", width=8)
        table.add_column("Title", min_width=50)
        
        for i, gallery in enumerate(results.galleries, 1):
            table.add_row(
                str(i),
                gallery.id,
                gallery.title[:70] + "..." if len(gallery.title) > 70 else gallery.title
            )
        
        self.console.print(table)
        
        # Print pagination info
        if results.total_pages > 1:
            self.print_info(
                f"Page {results.current_page}/{results.total_pages} "
                f"({len(results.galleries)} results shown)"
            )
    
    def create_download_progress(self) -> Progress:
        """Create a progress bar for downloads."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )
    
    def print_download_summary(self, successful: int, failed: int, total: int):
        """Print download summary."""
        if failed == 0:
            self.print_success(f"All {successful} downloads completed successfully!")
        else:
            self.print_warning(f"Completed: {successful}/{total} downloads")
            if failed > 0:
                self.print_error(f"Failed: {failed} downloads")
    
    def print_banner(self):
        """Print application banner."""
        banner_text = Text()
        banner_text.append("HFox", style="bold magenta")
        banner_text.append(" Downloader", style="bold white")
        
        panel = Panel(
            banner_text,
            subtitle="Beautiful manga downloader powered by gallery-dl",
            border_style="magenta"
        )
        self.console.print(panel)
    
    def confirm(self, message: str) -> bool:
        """Ask for user confirmation."""
        response = self.console.input(f"❓ {message} [y/N]: ")
        return response.lower() in ['y', 'yes']
    
    def get_gallery_selection(self, galleries: List[GalleryInfo]) -> List[GalleryInfo]:
        """Get user selection of galleries to download."""
        if not galleries:
            return []
        
        self.console.print()
        self.print_info("Select galleries to download:")
        self.console.print("  • Enter a single number (e.g., '3')")
        self.console.print("  • Enter a range (e.g., '1-5')")
        self.console.print("  • Enter 'all' for all galleries")
        self.console.print("  • Enter 'none' or 'q' to cancel")
        
        while True:
            try:
                selection = self.console.input("❓ Your selection: ").strip().lower()
                
                if selection in ['none', 'q', 'quit', 'cancel', '']:
                    return []
                
                if selection == 'all':
                    return galleries
                
                # Handle range (e.g., "1-5")
                if '-' in selection:
                    start_str, end_str = selection.split('-', 1)
                    start = int(start_str.strip())
                    end = int(end_str.strip())
                    
                    if start < 1 or end > len(galleries) or start > end:
                        self.print_error(f"Invalid range. Use 1-{len(galleries)}")
                        continue
                    
                    return galleries[start-1:end]
                
                # Handle single number
                num = int(selection)
                if num < 1 or num > len(galleries):
                    self.print_error(f"Invalid selection. Use 1-{len(galleries)}")
                    continue
                
                return [galleries[num-1]]
                
            except ValueError:
                self.print_error("Invalid input. Please try again.")
                continue
            except KeyboardInterrupt:
                self.print_info("Selection cancelled.")
                return []


# Global display instance
display = CLIDisplay()