"""Interactive search menu for HentaiFox Downloader."""

from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Confirm

from cli.utils.interactive_display import InteractiveMenu, InputValidator, StatusDisplay, HelpSystem
from cli.utils.display import display
from core.sites.hentaifox import HentaiFoxSite
from core.sites.base import GalleryInfo


class SearchMenu(InteractiveMenu):
    """Interactive search menu."""
    
    def __init__(self, console: Console):
        super().__init__(console, "Search Menu")
        self.site = HentaiFoxSite()
        self.last_results = []
    
    def _display_menu(self):
        """Display the search menu."""
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Option", style="cyan", width=3)
        table.add_column("Description", style="white")
        
        menu_items = [
            ("1", "🔍 Search by Query"),
            ("2", "🏷️  Search by Tag"),
            ("3", "📄 Advanced Search (multi-page)"),
            ("4", "📥 Download from Last Results"),
            ("5", "❓ Help"),
            ("6", "🔙 Back to Main Menu")
        ]
        
        # Show last results info if available
        if self.last_results:
            menu_items.insert(-2, ("", f"Last search: {len(self.last_results)} results"))
        
        for option, description in menu_items:
            table.add_row(option, description)
        
        panel = Panel(
            table,
            title="🔍 Search Menu",
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
            self._search_by_query()
        elif choice == 2:
            self._search_by_tag()
        elif choice == 3:
            self._advanced_search()
        elif choice == 4:
            self._download_from_last_results()
        elif choice == 5:
            HelpSystem.show_search_help(self.console)
            self._pause()
        elif choice == 6:
            self.running = False
    
    def _search_by_query(self):
        """Handle search by query."""
        query = InputValidator.get_string(self.console, "Enter search query")
        
        if not query:
            display.print_info("Search cancelled.")
            self._pause()
            return
        
        page = InputValidator.get_integer(self.console, "Enter page number", 1, 100)
        if not page:
            page = 1
        
        limit = InputValidator.get_integer(self.console, "Enter max results", 1, 100)
        if not limit:
            limit = 20
        
        # Perform search
        self._execute_search("query", query, page, limit)
    
    def _search_by_tag(self):
        """Handle search by tag."""
        tag = InputValidator.get_string(self.console, "Enter tag name")
        
        if not tag:
            display.print_info("Search cancelled.")
            self._pause()
            return
        
        page = InputValidator.get_integer(self.console, "Enter page number", 1, 100)
        if not page:
            page = 1
        
        limit = InputValidator.get_integer(self.console, "Enter max results", 1, 100)
        if not limit:
            limit = 20
        
        # Perform search
        self._execute_search("tag", tag, page, limit)
    
    def _advanced_search(self):
        """Handle advanced multi-page search."""
        search_type = InputValidator.get_choice(
            self.console,
            "Search type: 1=Query, 2=Tag",
            1, 2
        )
        
        if not search_type:
            display.print_info("Search cancelled.")
            self._pause()
            return
        
        search_term = InputValidator.get_string(
            self.console, 
            "Enter search query" if search_type == 1 else "Enter tag name"
        )
        
        if not search_term:
            display.print_info("Search cancelled.")
            self._pause()
            return
        
        start_page = InputValidator.get_integer(self.console, "Enter start page", 1, 100)
        if not start_page:
            start_page = 1
        
        end_page = InputValidator.get_integer(self.console, "Enter end page", start_page, 100)
        if not end_page:
            end_page = start_page
        
        limit_per_page = InputValidator.get_integer(self.console, "Enter max results per page", 1, 100)
        if not limit_per_page:
            limit_per_page = 50
        
        # Perform multi-page search
        self._execute_advanced_search(
            "query" if search_type == 1 else "tag",
            search_term,
            start_page,
            end_page,
            limit_per_page
        )
    
    def _execute_search(self, search_type: str, term: str, page: int, limit: int):
        """Execute a single-page search."""
        display.print_info(f"Searching for '{term}' on page {page}...")
        
        try:
            if search_type == "query":
                results = self.site.search(term, page)
            else:
                results = self.site.get_tag_galleries(term, page)
            
            if not results or not results.galleries:
                display.print_warning("No results found.")
                self._pause()
                return
            
            # Apply limit
            galleries = results.galleries[:limit] if limit else results.galleries
            self.last_results = galleries
            
            # Display results
            self._display_search_results(galleries)
            
            # Ask for download
            if Confirm.ask("Download selected galleries?", default=False):
                self._handle_gallery_selection(galleries)
            
        except Exception as e:
            display.print_error(f"Search failed: {e}")
        
        self._pause()
    
    def _execute_advanced_search(self, search_type: str, term: str, start_page: int, end_page: int, limit_per_page: int):
        """Execute a multi-page search."""
        all_galleries = []
        
        for page in range(start_page, end_page + 1):
            display.print_info(f"Searching page {page}/{end_page}...")
            
            try:
                if search_type == "query":
                    results = self.site.search(term, page)
                else:
                    results = self.site.get_tag_galleries(term, page)
                
                if not results or not results.galleries:
                    if page == start_page:
                        display.print_warning("No results found.")
                        self._pause()
                        return
                    else:
                        display.print_info(f"No more results on page {page}.")
                        break
                
                # Apply per-page limit
                page_galleries = results.galleries[:limit_per_page] if limit_per_page else results.galleries
                all_galleries.extend(page_galleries)
                
            except Exception as e:
                display.print_error(f"Search failed on page {page}: {e}")
                if page == start_page:
                    self._pause()
                    return
                continue
        
        if not all_galleries:
            display.print_warning("No results found.")
            self._pause()
            return
        
        self.last_results = all_galleries
        display.print_success(f"Found {len(all_galleries)} total results across {end_page - start_page + 1} pages.")
        
        # Display results
        self._display_search_results(all_galleries)
        
        # Ask for download
        if Confirm.ask("Download selected galleries?", default=False):
            self._handle_gallery_selection(all_galleries)
        
        self._pause()
    
    def _display_search_results(self, galleries: List[GalleryInfo]):
        """Display search results in a table."""
        if not galleries:
            display.print_warning("No results to display.")
            return
        
        table = StatusDisplay.show_search_results_table(self.console, galleries)
        
        panel = Panel(
            table,
            title=f"🔍 Search Results ({len(galleries)} found)",
            border_style="green"
        )
        self.console.print(panel)
    
    def _handle_gallery_selection(self, galleries: List[GalleryInfo]):
        """Handle gallery selection for download."""
        StatusDisplay.show_gallery_selection_help(self.console)
        
        selected = display.get_gallery_selection(galleries)
        
        if not selected:
            display.print_info("No galleries selected.")
            return
        
        display.print_info(f"Selected {len(selected)} galleries:")
        for i, gallery in enumerate(selected, 1):
            self.console.print(f"  {i}. {gallery.title}")
        
        if Confirm.ask("Proceed with download?"):
            self._download_selected_galleries(selected)
        else:
            display.print_info("Download cancelled.")
    
    def _download_selected_galleries(self, galleries: List[GalleryInfo]):
        """Download selected galleries."""
        from cli.commands.download import download_multiple
        
        urls = [gallery.url for gallery in galleries]
        
        try:
            download_multiple(urls, None, continue_on_error=True)
        except Exception as e:
            display.print_error(f"Download failed: {e}")
    
    def _download_from_last_results(self):
        """Download from last search results."""
        if not self.last_results:
            display.print_warning("No previous search results available.")
            self._pause()
            return
        
        display.print_info(f"Last search found {len(self.last_results)} results.")
        
        # Display results again
        self._display_search_results(self.last_results)
        
        # Handle selection
        if Confirm.ask("Download selected galleries?", default=False):
            self._handle_gallery_selection(self.last_results)
        
        self._pause()