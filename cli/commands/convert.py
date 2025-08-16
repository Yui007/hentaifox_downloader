"""Conversion commands for CLI."""

import typer
from typing import Optional
from pathlib import Path

from cli.utils.display import display
from core.converter import converter
from config.settings import config


def convert_gallery(
    directory: str = typer.Argument(..., help="Gallery directory to convert"),
    format_type: str = typer.Option("pdf", "--format", "-f", help="Output format (pdf, cbz)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    delete_source: bool = typer.Option(False, "--delete-source", "-d", help="Delete source images after conversion"),
    quality: Optional[int] = typer.Option(None, "--quality", "-q", help="Image quality (1-100)")
):
    """Convert a gallery directory to PDF or CBZ format."""
    
    source_dir = Path(directory)
    if not source_dir.exists():
        display.print_error(f"Directory not found: {directory}")
        raise typer.Exit(1)
    
    if not source_dir.is_dir():
        display.print_error(f"Path is not a directory: {directory}")
        raise typer.Exit(1)
    
    # Validate format
    if format_type.lower() not in ['pdf', 'cbz']:
        display.print_error(f"Unsupported format: {format_type}")
        display.print_info("Supported formats: pdf, cbz")
        raise typer.Exit(1)
    
    # Set quality if provided
    if quality is not None:
        if format_type.lower() == 'pdf':
            config.set("conversion.pdf_quality", quality)
        else:
            config.set("conversion.cbz_quality", quality)
    
    # Determine output path
    output_path = None
    if output:
        output_path = Path(output)
        # Ensure correct extension
        expected_ext = f".{format_type.lower()}"
        if not output_path.suffix.lower() == expected_ext:
            output_path = output_path.with_suffix(expected_ext)
    
    display.print_info(f"Converting {source_dir.name} to {format_type.upper()}...")
    
    # Show conversion progress
    with display.create_download_progress() as progress:
        task = progress.add_task(f"Converting to {format_type.upper()}", total=100)
        
        # Start conversion
        result = converter.convert_gallery(
            source_dir=source_dir,
            format_type=format_type,
            output_path=output_path,
            delete_source=delete_source
        )
        
        progress.update(task, completed=100, description="Conversion completed!")
    
    # Show results
    if result.success:
        display.print_success(f"✅ Conversion completed!")
        display.print_info(f"📁 Input: {result.input_files_count} images")
        display.print_info(f"📄 Output: {result.output_path}")
        
        if delete_source:
            display.print_info("🗑️  Source images deleted")
        
        # Show file size
        if result.output_path and result.output_path.exists():
            size_mb = result.output_path.stat().st_size / (1024 * 1024)
            display.print_info(f"📊 File size: {size_mb:.1f} MB")
    else:
        display.print_error(f"❌ Conversion failed: {result.error_message}")
        raise typer.Exit(1)


def batch_convert(
    base_directory: str = typer.Argument(..., help="Base directory containing gallery folders"),
    format_type: str = typer.Option("pdf", "--format", "-f", help="Output format (pdf, cbz)"),
    delete_source: bool = typer.Option(False, "--delete-source", "-d", help="Delete source images after conversion"),
    pattern: str = typer.Option("*", "--pattern", "-p", help="Directory name pattern to match")
):
    """Convert multiple gallery directories to PDF or CBZ format."""
    
    base_path = Path(base_directory)
    if not base_path.exists():
        display.print_error(f"Directory not found: {base_directory}")
        raise typer.Exit(1)
    
    # Find gallery directories
    gallery_dirs = []
    for item in base_path.iterdir():
        if item.is_dir() and item.match(pattern):
            # Check if directory contains images
            image_files = converter.get_image_files(item)
            if image_files:
                gallery_dirs.append(item)
    
    if not gallery_dirs:
        display.print_warning(f"No gallery directories found matching pattern: {pattern}")
        return
    
    display.print_info(f"Found {len(gallery_dirs)} galleries to convert")
    
    successful = 0
    failed = 0
    
    with display.create_download_progress() as progress:
        main_task = progress.add_task("Converting galleries", total=len(gallery_dirs))
        
        for i, gallery_dir in enumerate(gallery_dirs):
            current_task = progress.add_task(f"Converting {gallery_dir.name}", total=100)
            
            result = converter.convert_gallery(
                source_dir=gallery_dir,
                format_type=format_type,
                delete_source=delete_source
            )
            
            progress.update(current_task, completed=100)
            progress.update(main_task, advance=1)
            
            if result.success:
                successful += 1
                display.print_success(f"✅ {gallery_dir.name} -> {result.output_path.name}")
            else:
                failed += 1
                display.print_error(f"❌ {gallery_dir.name}: {result.error_message}")
    
    # Show summary
    display.print_info(f"\n📊 Batch Conversion Summary:")
    display.print_info(f"✅ Successful: {successful}")
    display.print_info(f"❌ Failed: {failed}")
    display.print_info(f"📁 Total: {len(gallery_dirs)}")


def set_auto_convert(
    format_type: str = typer.Argument(..., help="Auto-convert format (none, pdf, cbz)"),
    delete_source: bool = typer.Option(False, "--delete-source", "-d", help="Delete source images after auto-conversion")
):
    """Set automatic conversion format for future downloads."""
    
    if format_type.lower() not in ['none', 'pdf', 'cbz']:
        display.print_error(f"Invalid format: {format_type}")
        display.print_info("Valid formats: none, pdf, cbz")
        raise typer.Exit(1)
    
    # Update configuration
    config.set("conversion.default_format", format_type.lower())
    config.set("conversion.auto_convert", format_type.lower() != 'none')
    config.set("conversion.delete_source_after_conversion", delete_source)
    config.save()
    
    if format_type.lower() == 'none':
        display.print_success("✅ Auto-conversion disabled")
    else:
        display.print_success(f"✅ Auto-conversion enabled: {format_type.upper()}")
        if delete_source:
            display.print_info("🗑️  Source images will be deleted after conversion")
        else:
            display.print_info("📁 Source images will be kept after conversion")


def show_conversion_status():
    """Show current conversion settings."""
    display.print_info("📊 Current Conversion Settings:")
    
    auto_convert = config.get("conversion.auto_convert", False)
    default_format = config.get("conversion.default_format", "none")
    delete_source = config.get("conversion.delete_source_after_conversion", False)
    
    if auto_convert:
        display.print_info(f"  • Auto-conversion: ✅ {default_format.upper()}")
        display.print_info(f"  • Delete source: {'✅' if delete_source else '❌'}")
    else:
        display.print_info("  • Auto-conversion: ❌ Disabled")
    
    # Show quality settings
    pdf_quality = config.get("conversion.pdf_quality", 85)
    cbz_quality = config.get("conversion.cbz_quality", 90)
    display.print_info(f"  • PDF quality: {pdf_quality}%")
    display.print_info(f"  • CBZ quality: {cbz_quality}%")