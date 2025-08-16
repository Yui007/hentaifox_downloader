"""Download commands for CLI."""

import typer
from typing import Optional, List
from pathlib import Path

from cli.utils.display import display
from core.downloader import GalleryDLDownloader
from core.sites.hentaifox import HentaiFoxSite
from core.converter import converter
from config.settings import config


def download_gallery(
    url: str,
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Force download even if exists"),
    metadata: bool = typer.Option(True, "--metadata/--no-metadata", help="Save metadata"),
    convert_to: Optional[str] = typer.Option(None, "--convert", "-c", help="Convert to format after download (pdf, cbz)"),
    delete_images: bool = typer.Option(False, "--delete-images", help="Delete images after conversion")
):
    """Download a single gallery from URL."""
    
    # Validate URL
    site = HentaiFoxSite()
    if not site.is_valid_url(url):
        display.print_error(f"Invalid HentaiFox URL: {url}")
        raise typer.Exit(1)
    
    # Get gallery info
    display.print_info("Fetching gallery information...")
    gallery_info = site.get_gallery_info(url)
    
    if not gallery_info:
        display.print_error("Could not fetch gallery information.")
        raise typer.Exit(1)
    
    # Display gallery info
    display.print_gallery_info(gallery_info)
    
    # Confirm download
    if not force and not display.confirm("Proceed with download?"):
        display.print_info("Download cancelled.")
        return
    
    # Set custom output directory if provided
    if output_dir:
        original_path = config.get("download.base_path")
        config.set("download.base_path", output_dir)
    
    # Set metadata option
    config.set("metadata.save_metadata", metadata)
    
    # Initialize downloader
    downloader = GalleryDLDownloader()
    
    # Check if gallery-dl is available
    if not downloader.check_gallery_dl_available():
        display.print_error("gallery-dl is not installed or not in PATH.")
        display.print_info("Install with: pip install gallery-dl")
        raise typer.Exit(1)
    
    # Download with progress
    display.print_info("Starting download...")
    
    with display.create_download_progress() as progress:
        task = progress.add_task(f"Downloading {gallery_info.title}", total=gallery_info.pages or 100)
        
        def progress_callback(message: str, current: int, total: int):
            if total > 0:
                progress.update(task, completed=current, description=message)
            else:
                progress.update(task, advance=1, description=message)
        
        downloader.set_progress_callback(progress_callback)
        
        # Start download in a separate thread to allow progress updates
        import threading
        result_container = [None]
        
        def download_thread():
            result_container[0] = downloader.download_gallery(url, gallery_info)
        
        thread = threading.Thread(target=download_thread)
        thread.start()
        
        # Track real progress by monitoring download directory
        files_expected = gallery_info.pages or 100
        download_dir = None
        
        # Try to determine download directory
        from pathlib import Path
        base_path = Path(config.get("download.base_path"))
        safe_title = gallery_info.title.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        potential_dir = base_path / safe_title
        
        while thread.is_alive():
            import time
            time.sleep(0.5)
            
            # Try to count actual downloaded files
            actual_files = 0
            if potential_dir.exists():
                download_dir = potential_dir
                # Count image files in the directory
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
                actual_files = sum(1 for f in download_dir.iterdir() 
                                 if f.is_file() and f.suffix.lower() in image_extensions)
            
            # Update progress with actual file count, but don't exceed expected
            current_progress = min(actual_files, files_expected)
            progress.update(task, completed=current_progress, 
                          description=f"Downloaded {actual_files} files...")
        
        thread.join()
        result = result_container[0]
        
        # Complete the progress bar with actual file count
        if result and result.success:
            # Update both total and completed to actual file count for 100% completion
            progress.update(task, total=result.files_downloaded, completed=result.files_downloaded, description="Download completed!")
        else:
            # Fallback to estimated completion
            progress.update(task, completed=files_expected, description="Download completed!")
    
    # Restore original config
    if output_dir:
        config.set("download.base_path", original_path)
    
    # Show results
    if result.success:
        display.print_success(f"Download completed! {result.files_downloaded} files downloaded.")
        if result.download_path:
            display.print_info(f"Saved to: {result.download_path}")
            
            # Handle conversion
            should_convert = False
            conversion_format = None
            should_delete = False
            
            # Check command line options first
            if convert_to:
                should_convert = True
                conversion_format = convert_to.lower()
                should_delete = delete_images
            # Check auto-conversion settings
            elif config.get("conversion.auto_convert", False):
                should_convert = True
                conversion_format = config.get("conversion.default_format", "pdf")
                should_delete = config.get("conversion.delete_source_after_conversion", False)
            
            # Perform conversion if requested
            if should_convert and conversion_format in ['pdf', 'cbz']:
                display.print_info(f"Converting to {conversion_format.upper()}...")
                
                conversion_result = converter.convert_gallery(
                    source_dir=result.download_path,
                    format_type=conversion_format,
                    delete_source=should_delete
                )
                
                if conversion_result.success:
                    display.print_success(f"✅ Converted to {conversion_format.upper()}: {conversion_result.output_path}")
                    if should_delete:
                        display.print_info("🗑️  Source images deleted")
                else:
                    display.print_error(f"❌ Conversion failed: {conversion_result.error_message}")
    else:
        display.print_error(f"Download failed: {result.error_message}")
        raise typer.Exit(1)


def download_multiple(
    urls: List[str] = typer.Argument(..., help="List of gallery URLs"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    continue_on_error: bool = typer.Option(True, "--continue/--stop-on-error", help="Continue on errors")
):
    """Download multiple galleries from URLs."""
    
    if not urls:
        display.print_error("No URLs provided.")
        raise typer.Exit(1)
    
    site = HentaiFoxSite()
    valid_urls = []
    
    # Validate all URLs
    for url in urls:
        if site.is_valid_url(url):
            valid_urls.append(url)
        else:
            display.print_warning(f"Skipping invalid URL: {url}")
    
    if not valid_urls:
        display.print_error("No valid URLs found.")
        raise typer.Exit(1)
    
    display.print_info(f"Found {len(valid_urls)} valid URLs to download.")
    
    # Set custom output directory if provided
    if output_dir:
        original_path = config.get("download.base_path")
        config.set("download.base_path", output_dir)
    
    # Initialize downloader
    downloader = GalleryDLDownloader()
    
    if not downloader.check_gallery_dl_available():
        display.print_error("gallery-dl is not installed or not in PATH.")
        raise typer.Exit(1)
    
    # Download all galleries with parallel processing
    successful = 0
    failed = 0
    
    display.print_info(f"Starting parallel downloads (max {config.get('download.max_parallel_galleries', 2)} concurrent)...")
    
    with display.create_download_progress() as progress:
        main_task = progress.add_task("Overall Progress", total=len(valid_urls))
        
        # Use the downloader's parallel processing
        def batch_progress_callback(message: str, current: int, total: int):
            progress.update(main_task, completed=current, description=message)
        
        downloader.set_progress_callback(batch_progress_callback)
        results = downloader.download_multiple(valid_urls)
        
        # Count results
        for result in results:
            if result.success:
                successful += 1
            else:
                failed += 1
                if not continue_on_error and result.error_message:
                    display.print_error(f"Download failed: {result.error_message}")
                    break
        
        progress.update(main_task, completed=len(valid_urls), description="All downloads completed!")
    
    # Restore original config
    if output_dir:
        config.set("download.base_path", original_path)
    
    # Show summary
    display.print_download_summary(successful, failed, len(valid_urls))
    
    if failed > 0 and not continue_on_error:
        raise typer.Exit(1)