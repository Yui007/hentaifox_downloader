"""Search commands for CLI."""

import typer
from typing import Optional

from cli.utils.display import display
from core.sites.hentaifox import HentaiFoxSite


def search_galleries(
    query: str = typer.Argument(..., help="Search query"),
    page_start: int = typer.Option(1, "--page", "-p", help="Starting page number"),
    page_end: Optional[int] = typer.Option(None, "--page-end", help="Ending page number (for range)"),
    limit: int = typer.Option(50, "--limit", "-l", help="Max results per page")
):
    """Search for galleries on HentaiFox."""
    
    site = HentaiFoxSite()
    all_galleries = []
    
    # Determine page range
    if page_end is None:
        page_end = page_start
    
    if page_start > page_end:
        display.print_error("Starting page cannot be greater than ending page.")
        raise typer.Exit(1)
    
    # Search across page range
    for page in range(page_start, page_end + 1):
        if page > page_start:
            display.print_info(f"Searching page {page}...")
        else:
            display.print_info(f"Searching for: '{query}' (page {page})")
        
        try:
            results = site.search(query, page)
            
            if not results:
                display.print_error(f"Search failed on page {page}.")
                continue
            
            if not results.galleries:
                if page == page_start:
                    display.print_warning("No galleries found for your search.")
                    return
                else:
                    display.print_info(f"No more results on page {page}.")
                    break
            
            # Apply limit per page
            page_galleries = results.galleries
            if limit and len(page_galleries) > limit:
                page_galleries = page_galleries[:limit]
            
            all_galleries.extend(page_galleries)
                
        except Exception as e:
            display.print_error(f"Search error on page {page}: {e}")
            if page == page_start:
                raise typer.Exit(1)
            continue
    
    if not all_galleries:
        display.print_warning("No galleries found.")
        return
    
    # Create a mock SearchResult for display
    from core.sites.base import SearchResult
    display_results = SearchResult(
        galleries=all_galleries,
        total_count=len(all_galleries),
        current_page=page_start,
        total_pages=page_end,
        has_next=False
    )
    
    display.print_search_results(display_results)
    
    # Get user selection for download
    selected_galleries = display.get_gallery_selection(all_galleries)
    
    if selected_galleries:
        display.print_info(f"Selected {len(selected_galleries)} galleries for download:")
        for i, gallery in enumerate(selected_galleries, 1):
            display.console.print(f"  {i}. {gallery.title}")
        
        if display.confirm("Proceed with download?"):
            from cli.commands.download import download_multiple
            urls = [gallery.url for gallery in selected_galleries]
            download_multiple(urls, None, continue_on_error=True)
        else:
            display.print_info("Download cancelled.")
    else:
        display.print_info("No galleries selected.")


def search_by_tag(
    tag: str = typer.Argument(..., help="Tag to search for"),
    page_start: int = typer.Option(1, "--page", "-p", help="Starting page number"),
    page_end: Optional[int] = typer.Option(None, "--page-end", help="Ending page number (for range)"),
    limit: int = typer.Option(50, "--limit", "-l", help="Max results per page")
):
    """Search galleries by tag on HentaiFox."""
    
    site = HentaiFoxSite()
    all_galleries = []
    
    # Determine page range
    if page_end is None:
        page_end = page_start
    
    if page_start > page_end:
        display.print_error("Starting page cannot be greater than ending page.")
        raise typer.Exit(1)
    
    # Search across page range
    for page in range(page_start, page_end + 1):
        if page > page_start:
            display.print_info(f"Searching tag page {page}...")
        else:
            display.print_info(f"Searching tag: '{tag}' (page {page})")
        
        try:
            results = site.get_tag_galleries(tag, page)
            
            if not results:
                display.print_error(f"Tag search failed on page {page}.")
                continue
            
            if not results.galleries:
                if page == page_start:
                    display.print_warning(f"No galleries found for tag '{tag}'.")
                    return
                else:
                    display.print_info(f"No more results on page {page}.")
                    break
            
            # Apply limit per page
            page_galleries = results.galleries
            if limit and len(page_galleries) > limit:
                page_galleries = page_galleries[:limit]
            
            all_galleries.extend(page_galleries)
                
        except Exception as e:
            display.print_error(f"Tag search error on page {page}: {e}")
            if page == page_start:
                raise typer.Exit(1)
            continue
    
    if not all_galleries:
        display.print_warning("No galleries found.")
        return
    
    # Create a mock SearchResult for display
    from core.sites.base import SearchResult
    display_results = SearchResult(
        galleries=all_galleries,
        total_count=len(all_galleries),
        current_page=page_start,
        total_pages=page_end,
        has_next=False
    )
    
    display.print_search_results(display_results)
    
    # Get user selection for download
    selected_galleries = display.get_gallery_selection(all_galleries)
    
    if selected_galleries:
        display.print_info(f"Selected {len(selected_galleries)} galleries for download:")
        for i, gallery in enumerate(selected_galleries, 1):
            display.console.print(f"  {i}. {gallery.title}")
        
        if display.confirm("Proceed with download?"):
            from cli.commands.download import download_multiple
            urls = [gallery.url for gallery in selected_galleries]
            download_multiple(urls, None, continue_on_error=True)
        else:
            display.print_info("Download cancelled.")
    else:
        display.print_info("No galleries selected.")


def download_search_results(
    query: str = typer.Argument(..., help="Search query"),
    page: int = typer.Option(1, "--page", "-p", help="Page number"),
    limit: int = typer.Option(5, "--limit", "-l", help="Max galleries to download"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Search and download galleries in one command."""
    
    site = HentaiFoxSite()
    
    display.print_info(f"Searching and downloading: '{query}'")
    
    try:
        results = site.search(query, page)
        
        if not results or not results.galleries:
            display.print_error("No galleries found.")
            raise typer.Exit(1)
        
        # Limit results
        galleries_to_download = results.galleries[:limit]
        
        display.print_info(f"Found {len(results.galleries)} results, downloading first {len(galleries_to_download)}")
        
        # Show what will be downloaded
        for i, gallery in enumerate(galleries_to_download, 1):
            display.console.print(f"  {i}. {gallery.title}")
        
        if not display.confirm(f"Download these {len(galleries_to_download)} galleries?"):
            display.print_info("Download cancelled.")
            return
        
        # Import download function
        from cli.commands.download import download_multiple
        
        urls = [gallery.url for gallery in galleries_to_download]
        download_multiple(urls, output_dir, continue_on_error=True)
        
    except Exception as e:
        display.print_error(f"Search and download error: {e}")
        raise typer.Exit(1)