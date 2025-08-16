"""Main CLI entry point for HFox Downloader."""

import typer
from typing import Optional

from cli.utils.display import display
from cli.commands.download import download_gallery, download_multiple
from config.settings import config

# Create main Typer app
app = typer.Typer(
    name="hfox",
    help="🎯 HFox Downloader - Beautiful manga downloader for HentaiFox",
    add_completion=False
)

# Create subcommands
download_app = typer.Typer(help="Download commands")
search_app = typer.Typer(help="Search commands")
perf_app = typer.Typer(help="Performance commands")
convert_app = typer.Typer(help="Conversion commands")
app.add_typer(download_app, name="download")
app.add_typer(search_app, name="search")
app.add_typer(perf_app, name="perf")
app.add_typer(convert_app, name="convert")


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
    config_path: Optional[str] = typer.Option(None, "--config", help="Custom config file path")
):
    """HFox Downloader - Beautiful manga downloader powered by gallery-dl."""
    
    if version:
        display.console.print("HFox Downloader v1.0.0")
        raise typer.Exit()
    
    if config_path:
        # TODO: Load custom config file
        pass


@download_app.command("gallery")
def download_gallery_cmd(
    url: str = typer.Argument(..., help="Gallery URL to download"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Force download"),
    metadata: bool = typer.Option(True, "--metadata/--no-metadata", help="Save metadata"),
    convert_to: Optional[str] = typer.Option(None, "--convert", "-c", help="Convert to format (pdf, cbz)"),
    delete_images: bool = typer.Option(False, "--delete-images", help="Delete images after conversion")
):
    """Download a single gallery."""
    download_gallery(url, output_dir, force, metadata, convert_to, delete_images)


@download_app.command("batch")
def download_batch_cmd(
    urls: list[str] = typer.Argument(..., help="List of gallery URLs"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    continue_on_error: bool = typer.Option(True, "--continue/--stop-on-error", help="Continue on errors")
):
    """Download multiple galleries."""
    download_multiple(urls, output_dir, continue_on_error)


@search_app.command("query")
def search_query_cmd(
    query: str = typer.Argument(..., help="Search query"),
    page_start: int = typer.Option(1, "--page", "-p", help="Starting page number"),
    page_end: Optional[int] = typer.Option(None, "--page-end", help="Ending page number (for range)"),
    limit: int = typer.Option(50, "--limit", "-l", help="Max results per page")
):
    """Search for galleries by query."""
    from cli.commands.search import search_galleries
    search_galleries(query, page_start, page_end, limit)


@search_app.command("tag")
def search_tag_cmd(
    tag: str = typer.Argument(..., help="Tag to search for"),
    page_start: int = typer.Option(1, "--page", "-p", help="Starting page number"),
    page_end: Optional[int] = typer.Option(None, "--page-end", help="Ending page number (for range)"),
    limit: int = typer.Option(50, "--limit", "-l", help="Max results per page")
):
    """Search galleries by tag."""
    from cli.commands.search import search_by_tag
    search_by_tag(tag, page_start, page_end, limit)


@search_app.command("download")
def search_download_cmd(
    query: str = typer.Argument(..., help="Search query"),
    page: int = typer.Option(1, "--page", "-p", help="Page number"),
    limit: int = typer.Option(5, "--limit", "-l", help="Max downloads"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Search and download galleries."""
    from cli.commands.search import download_search_results
    download_search_results(query, page, limit, output_dir)


@app.command("info")
def show_info(
    url: str = typer.Argument(..., help="Gallery URL to get info for")
):
    """Show gallery information without downloading."""
    from core.sites.hentaifox import HentaiFoxSite
    
    site = HentaiFoxSite()
    
    if not site.is_valid_url(url):
        display.print_error(f"Invalid HentaiFox URL: {url}")
        raise typer.Exit(1)
    
    display.print_info("Fetching gallery information...")
    gallery_info = site.get_gallery_info(url)
    
    if gallery_info:
        display.print_gallery_info(gallery_info)
    else:
        display.print_error("Could not fetch gallery information.")
        raise typer.Exit(1)


@app.command("config")
def show_config():
    """Show current configuration."""
    import yaml
    
    display.print_info("Current Configuration:")
    config_yaml = yaml.dump(config.config, default_flow_style=False, indent=2)
    display.console.print(config_yaml)


@app.command("setup")
def setup():
    """Initial setup and configuration."""
    display.print_banner()
    
    display.print_info("Setting up HFox Downloader...")
    
    # Check gallery-dl
    from core.downloader import GalleryDLDownloader
    downloader = GalleryDLDownloader()
    
    if downloader.check_gallery_dl_available():
        display.print_success("gallery-dl is available")
    else:
        display.print_error("gallery-dl is not installed")
        display.print_info("Install with: pip install gallery-dl")
        return
    
    # Check download directory
    download_path = config.get("download.base_path")
    display.print_info(f"Download directory: {download_path}")
    
    from pathlib import Path
    Path(download_path).mkdir(parents=True, exist_ok=True)
    display.print_success("Download directory is ready")
    
    # Save config
    config.save()
    display.print_success("Setup completed!")
    display.print_info("You can now use 'hfox download gallery <url>' to start downloading.")


@app.command("history")
def show_history(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of entries to show"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search history")
):
    """Show download history."""
    from core.history import history
    
    if search:
        entries = history.search_history(search, limit)
        display.print_info(f"Search results for '{search}':")
    else:
        entries = history.get_recent_downloads(limit)
        display.print_info(f"Recent downloads (last {limit}):")
    
    if not entries:
        display.print_warning("No history entries found.")
        return
    
    from rich.table import Table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", width=8)
    table.add_column("Title", min_width=30)
    table.add_column("Files", width=8, justify="center")
    table.add_column("Downloaded", width=12)
    table.add_column("Path", width=30)
    
    for entry in entries:
        # Format date
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(entry.downloaded_at)
            date_str = dt.strftime("%Y-%m-%d")
        except:
            date_str = entry.downloaded_at[:10]
        
        # Truncate long paths
        path_str = entry.download_path
        if len(path_str) > 30:
            path_str = "..." + path_str[-27:]
        
        table.add_row(
            entry.gallery_id,
            entry.title[:40] + "..." if len(entry.title) > 40 else entry.title,
            str(entry.files_count),
            date_str,
            path_str
        )
    
    display.console.print(table)


@app.command("stats")
def show_stats():
    """Show download statistics."""
    from core.history import history
    
    stats = history.get_stats()
    
    from rich.panel import Panel
    from rich.table import Table
    
    # Create stats table
    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    table.add_row("Total Downloads", str(stats["total_downloads"]))
    table.add_row("Total Files", str(stats["total_files"]))
    table.add_row("Recent (7 days)", str(stats["recent_downloads"]))
    
    # Add site breakdown
    for site, count in stats["by_site"].items():
        table.add_row(f"  {site.title()}", str(count))
    
    panel = Panel(table, title="📊 Download Statistics", border_style="green")
    display.console.print(panel)


@perf_app.command("turbo")
def enable_turbo():
    """Enable turbo mode for maximum download speed."""
    from cli.commands.performance import enable_turbo_mode
    enable_turbo_mode()


@perf_app.command("normal")
def disable_turbo():
    """Disable turbo mode and restore default settings."""
    from cli.commands.performance import disable_turbo_mode
    disable_turbo_mode()


@perf_app.command("status")
def perf_status():
    """Show current performance configuration."""
    from cli.commands.performance import show_performance_status
    show_performance_status()


@convert_app.command("gallery")
def convert_gallery_cmd(
    directory: str = typer.Argument(..., help="Gallery directory to convert"),
    format_type: str = typer.Option("pdf", "--format", "-f", help="Output format (pdf, cbz)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    delete_source: bool = typer.Option(False, "--delete-source", "-d", help="Delete source images"),
    quality: Optional[int] = typer.Option(None, "--quality", "-q", help="Image quality (1-100)")
):
    """Convert a gallery directory to PDF or CBZ."""
    from cli.commands.convert import convert_gallery
    convert_gallery(directory, format_type, output, delete_source, quality)


@convert_app.command("batch")
def batch_convert_cmd(
    base_directory: str = typer.Argument(..., help="Base directory with gallery folders"),
    format_type: str = typer.Option("pdf", "--format", "-f", help="Output format (pdf, cbz)"),
    delete_source: bool = typer.Option(False, "--delete-source", "-d", help="Delete source images"),
    pattern: str = typer.Option("*", "--pattern", "-p", help="Directory pattern to match")
):
    """Convert multiple galleries to PDF or CBZ."""
    from cli.commands.convert import batch_convert
    batch_convert(base_directory, format_type, delete_source, pattern)


@convert_app.command("auto")
def set_auto_convert_cmd(
    format_type: str = typer.Argument(..., help="Auto-convert format (none, pdf, cbz)"),
    delete_source: bool = typer.Option(False, "--delete-source", "-d", help="Delete source after conversion")
):
    """Set automatic conversion for future downloads."""
    from cli.commands.convert import set_auto_convert
    set_auto_convert(format_type, delete_source)


@convert_app.command("status")
def conversion_status_cmd():
    """Show current conversion settings."""
    from cli.commands.convert import show_conversion_status
    show_conversion_status()


@app.command("test")
def test_download():
    """Test gallery-dl and aria2c availability."""
    import subprocess
    
    display.print_info("Testing system components...")
    
    # Test gallery-dl
    try:
        result = subprocess.run(["gallery-dl", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            display.print_success(f"gallery-dl is available: {version}")
        else:
            display.print_error("gallery-dl not working properly")
    except Exception:
        display.print_error("gallery-dl is not installed")
        display.print_info("Install with: pip install gallery-dl")
    
    # Test aria2c
    try:
        aria2_path = config.get("download.aria2_path", "aria2c")
        result = subprocess.run([aria2_path, "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.strip().split('\n')[0]
            display.print_success(f"aria2c is available: {version_line}")
            display.print_info("Fast downloads enabled!")
        else:
            display.print_warning("aria2c not working properly")
    except Exception:
        display.print_warning("aria2c is not installed - downloads will be slower")
        display.print_info("Install aria2c for faster downloads:")
        display.print_info("  Windows: Download from https://aria2.github.io/")
        display.print_info("  macOS: brew install aria2")
        display.print_info("  Linux: sudo apt install aria2 (or equivalent)")
    
    # Test HentaiFox URL parsing
    test_url = "https://hentaifox.com/gallery/147838/"
    try:
        cmd_test = ["gallery-dl", "-g", test_url]
        result_test = subprocess.run(cmd_test, capture_output=True, text=True, timeout=30)
        
        if result_test.returncode == 0 and result_test.stdout.strip():
            urls = result_test.stdout.strip().split('\n')
            display.print_success(f"HentaiFox parsing works - found {len(urls)} image URLs")
        else:
            display.print_error("HentaiFox URL parsing failed")
            
    except Exception as e:
        display.print_error(f"Test failed: {e}")


@app.command("interactive")
def interactive_mode():
    """Launch interactive CLI mode with menu-driven interface."""
    from cli.interactive import InteractiveCLI
    interactive_cli = InteractiveCLI()
    interactive_cli.run()


if __name__ == "__main__":
    app()