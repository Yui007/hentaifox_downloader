"""Interactive history menu for HentaiFox Downloader."""

from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Confirm

from cli.utils.interactive_display import InteractiveMenu, InputValidator
from cli.utils.display import display
from core.history import history


class HistoryMenu(InteractiveMenu):
    """Interactive history menu."""
    
    def __init__(self, console: Console):
        super().__init__(console, "History Menu")
    
    def _display_menu(self):
        """Display the history menu."""
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Option", style="cyan", width=3)
        table.add_column("Description", style="white")
        
        # Get stats for display
        try:
            stats = history.get_stats()
            total_downloads = stats.get("total_downloads", 0)
            recent_downloads = stats.get("recent_downloads", 0)
        except:
            total_downloads = 0
            recent_downloads = 0
        
        menu_items = [
            ("", f"Total downloads: {total_downloads}"),
            ("", f"Recent (7 days): {recent_downloads}"),
            ("", ""),
            ("1", "📋 View Recent Downloads"),
            ("2", "🔍 Search History"),
            ("3", "📊 Download Statistics"),
            ("4", "📤 Export History"),
            ("5", "🗑️  Clear History"),
            ("6", "🔙 Back to Main Menu")
        ]
        
        for option, description in menu_items:
            table.add_row(option, description)
        
        panel = Panel(
            table,
            title="📊 History & Statistics",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _get_choice(self) -> Optional[int]:
        """Get user menu choice."""
        return InputValidator.get_choice(self.console, "Enter your choice", 1, 6)
    
    def _handle_choice(self, choice: int):
        """Handle user menu choice."""
        self.console.print()
        
        if choice == 1:
            self._view_recent_downloads()
        elif choice == 2:
            self._search_history()
        elif choice == 3:
            self._show_statistics()
        elif choice == 4:
            self._export_history()
        elif choice == 5:
            self._clear_history()
        elif choice == 6:
            self.running = False
    
    def _view_recent_downloads(self):
        """View recent downloads."""
        limit = InputValidator.get_integer(
            self.console,
            "Enter number of entries to show",
            1, 1000
        )
        if not limit:
            limit = 20
        
        try:
            entries = history.get_recent_downloads(limit)
            
            if not entries:
                display.print_warning("No download history found.")
                self._pause()
                return
            
            # Create table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", width=8)
            table.add_column("Title", min_width=40)
            table.add_column("Files", width=8, justify="center")
            table.add_column("Date", width=12)
            table.add_column("Path", width=30)
            
            for entry in entries:
                # Format date
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(entry.downloaded_at)
                    date_str = dt.strftime("%Y-%m-%d")
                except:
                    date_str = entry.downloaded_at[:10]
                
                # Truncate long titles and paths
                title = entry.title[:50] + "..." if len(entry.title) > 50 else entry.title
                path_str = entry.download_path
                if len(path_str) > 30:
                    path_str = "..." + path_str[-27:]
                
                table.add_row(
                    entry.gallery_id,
                    title,
                    str(entry.files_count),
                    date_str,
                    path_str
                )
            
            panel = Panel(
                table,
                title=f"📋 Recent Downloads (showing {len(entries)})",
                border_style="green"
            )
            self.console.print(panel)
            
        except Exception as e:
            display.print_error(f"Failed to retrieve history: {e}")
        
        self._pause()
    
    def _search_history(self):
        """Search download history."""
        search_term = InputValidator.get_string(self.console, "Enter search term")
        
        if not search_term:
            display.print_info("Search cancelled.")
            self._pause()
            return
        
        limit = InputValidator.get_integer(
            self.console,
            "Enter max results",
            1, 1000
        )
        if not limit:
            limit = 50
        
        try:
            entries = history.search_history(search_term, limit)
            
            if not entries:
                display.print_warning(f"No results found for '{search_term}'.")
                self._pause()
                return
            
            display.print_success(f"Found {len(entries)} results for '{search_term}':")
            
            # Create table (same format as recent downloads)
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", width=8)
            table.add_column("Title", min_width=40)
            table.add_column("Files", width=8, justify="center")
            table.add_column("Date", width=12)
            
            for entry in entries:
                # Format date
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(entry.downloaded_at)
                    date_str = dt.strftime("%Y-%m-%d")
                except:
                    date_str = entry.downloaded_at[:10]
                
                # Truncate long title
                title = entry.title[:50] + "..." if len(entry.title) > 50 else entry.title
                
                table.add_row(
                    entry.gallery_id,
                    title,
                    str(entry.files_count),
                    date_str
                )
            
            panel = Panel(
                table,
                title=f"🔍 Search Results for '{search_term}'",
                border_style="green"
            )
            self.console.print(panel)
            
        except Exception as e:
            display.print_error(f"Search failed: {e}")
        
        self._pause()
    
    def _show_statistics(self):
        """Show download statistics."""
        try:
            stats = history.get_stats()
            
            # Create stats table
            table = Table(show_header=False, box=box.SIMPLE)
            table.add_column("Metric", style="cyan", width=20)
            table.add_column("Value", style="white")
            
            table.add_row("Total Downloads", str(stats["total_downloads"]))
            table.add_row("Total Files", str(stats["total_files"]))
            table.add_row("Recent (7 days)", str(stats["recent_downloads"]))
            
            # Add site breakdown
            if stats.get("by_site"):
                table.add_row("", "")
                table.add_row("By Site:", "")
                for site, count in stats["by_site"].items():
                    table.add_row(f"  {site.title()}", str(count))
            
            panel = Panel(
                table,
                title="📊 Download Statistics",
                border_style="green"
            )
            self.console.print(panel)
            
        except Exception as e:
            display.print_error(f"Failed to retrieve statistics: {e}")
        
        self._pause()
    
    def _export_history(self):
        """Export download history."""
        format_choice = InputValidator.get_choice(
            self.console,
            "Export format: 1=CSV, 2=JSON",
            1, 2
        )
        
        if not format_choice:
            display.print_info("Export cancelled.")
            self._pause()
            return
        
        output_file = InputValidator.get_string(
            self.console,
            "Enter output filename (or Enter for default)"
        )
        
        if not output_file:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = "csv" if format_choice == 1 else "json"
            output_file = f"hfox_history_{timestamp}.{extension}"
        
        try:
            # Get all history entries
            entries = history.get_recent_downloads(10000)  # Get all entries
            
            if not entries:
                display.print_warning("No history to export.")
                self._pause()
                return
            
            if format_choice == 1:
                self._export_csv(entries, output_file)
            else:
                self._export_json(entries, output_file)
            
            display.print_success(f"✅ History exported to: {output_file}")
            display.print_info(f"Exported {len(entries)} entries")
            
        except Exception as e:
            display.print_error(f"Export failed: {e}")
        
        self._pause()
    
    def _export_csv(self, entries, filename):
        """Export history to CSV format."""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Gallery ID', 'Title', 'Files Count', 'Downloaded At', 'Download Path', 'Site'])
            
            for entry in entries:
                writer.writerow([
                    entry.gallery_id,
                    entry.title,
                    entry.files_count,
                    entry.downloaded_at,
                    entry.download_path,
                    entry.site
                ])
    
    def _export_json(self, entries, filename):
        """Export history to JSON format."""
        import json
        
        data = []
        for entry in entries:
            data.append({
                'gallery_id': entry.gallery_id,
                'title': entry.title,
                'files_count': entry.files_count,
                'downloaded_at': entry.downloaded_at,
                'download_path': entry.download_path,
                'site': entry.site
            })
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
    
    def _clear_history(self):
        """Clear download history."""
        if not Confirm.ask("⚠️  Clear ALL download history? This cannot be undone!", default=False):
            display.print_info("Clear cancelled.")
            self._pause()
            return
        
        if not Confirm.ask("Are you absolutely sure?", default=False):
            display.print_info("Clear cancelled.")
            self._pause()
            return
        
        try:
            # Clear history (this would need to be implemented in history module)
            # For now, just show a message
            display.print_warning("History clearing not yet implemented.")
            display.print_info("You can manually delete the history database file.")
            
        except Exception as e:
            display.print_error(f"Failed to clear history: {e}")
        
        self._pause()