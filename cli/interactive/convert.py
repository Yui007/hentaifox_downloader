"""Interactive conversion menu for HentaiFox Downloader."""

from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Confirm

from cli.utils.interactive_display import InteractiveMenu, InputValidator, HelpSystem
from cli.utils.display import display
from config.settings import config


class ConvertMenu(InteractiveMenu):
    """Interactive conversion menu."""
    
    def __init__(self, console: Console):
        super().__init__(console, "Convert Menu")
    
    def _display_menu(self):
        """Display the conversion menu."""
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Option", style="cyan", width=3)
        table.add_column("Description", style="white")
        
        # Show current auto-conversion status
        auto_convert = config.get("conversion.auto_convert", False)
        default_format = config.get("conversion.default_format", "none")
        status = f"✅ {default_format.upper()}" if auto_convert else "❌ Disabled"
        
        menu_items = [
            ("", f"Auto-conversion: {status}"),
            ("", ""),
            ("1", "📄 Convert Single Gallery"),
            ("2", "📦 Batch Convert Galleries"),
            ("3", "⚙️  Configure Auto-Conversion"),
            ("4", "📊 View Conversion Status"),
            ("5", "❓ Help"),
            ("6", "🔙 Back to Main Menu")
        ]
        
        for option, description in menu_items:
            table.add_row(option, description)
        
        panel = Panel(
            table,
            title="📚 Conversion Menu",
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
            self._convert_single_gallery()
        elif choice == 2:
            self._batch_convert_galleries()
        elif choice == 3:
            self._configure_auto_conversion()
        elif choice == 4:
            self._show_conversion_status()
        elif choice == 5:
            HelpSystem.show_conversion_help(self.console)
            self._pause()
        elif choice == 6:
            self.running = False
    
    def _convert_single_gallery(self):
        """Handle single gallery conversion."""
        directory = InputValidator.get_string(self.console, "Enter gallery directory path")
        
        if not directory:
            display.print_info("Conversion cancelled.")
            self._pause()
            return
        
        # Validate directory
        dir_path = Path(directory)
        if not dir_path.exists():
            display.print_error(f"Directory not found: {directory}")
            self._pause()
            return
        
        if not dir_path.is_dir():
            display.print_error(f"Path is not a directory: {directory}")
            self._pause()
            return
        
        # Get conversion options
        options = self._get_conversion_options()
        if not options:
            display.print_info("Conversion cancelled.")
            self._pause()
            return
        
        # Confirm conversion
        if not Confirm.ask(f"Convert '{dir_path.name}' to {options['format'].upper()}?"):
            display.print_info("Conversion cancelled.")
            self._pause()
            return
        
        # Perform conversion
        self._execute_single_conversion(dir_path, options)
        self._pause()
    
    def _batch_convert_galleries(self):
        """Handle batch gallery conversion."""
        base_directory = InputValidator.get_string(self.console, "Enter base directory with galleries")
        
        if not base_directory:
            display.print_info("Conversion cancelled.")
            self._pause()
            return
        
        # Validate directory
        base_path = Path(base_directory)
        if not base_path.exists():
            display.print_error(f"Directory not found: {base_directory}")
            self._pause()
            return
        
        # Get pattern
        pattern = InputValidator.get_string(self.console, "Enter directory pattern (or Enter for '*')")
        if not pattern:
            pattern = "*"
        
        # Get conversion options
        options = self._get_conversion_options()
        if not options:
            display.print_info("Conversion cancelled.")
            self._pause()
            return
        
        # Find galleries
        gallery_dirs = []
        for item in base_path.iterdir():
            if item.is_dir() and item.match(pattern):
                # Check if directory contains images
                image_files = self._get_image_files(item)
                if image_files:
                    gallery_dirs.append(item)
        
        if not gallery_dirs:
            display.print_warning(f"No gallery directories found matching pattern: {pattern}")
            self._pause()
            return
        
        display.print_info(f"Found {len(gallery_dirs)} galleries to convert:")
        for i, gallery_dir in enumerate(gallery_dirs[:10], 1):  # Show first 10
            self.console.print(f"  {i}. {gallery_dir.name}")
        
        if len(gallery_dirs) > 10:
            self.console.print(f"  ... and {len(gallery_dirs) - 10} more")
        
        # Confirm batch conversion
        if not Confirm.ask(f"Convert {len(gallery_dirs)} galleries to {options['format'].upper()}?"):
            display.print_info("Conversion cancelled.")
            self._pause()
            return
        
        # Perform batch conversion
        self._execute_batch_conversion(gallery_dirs, options)
        self._pause()
    
    def _configure_auto_conversion(self):
        """Configure auto-conversion settings."""
        current_auto = config.get("conversion.auto_convert", False)
        current_format = config.get("conversion.default_format", "none")
        current_delete = config.get("conversion.delete_source_after_conversion", False)
        
        self.console.print(f"Current auto-conversion: {'✅ Enabled' if current_auto else '❌ Disabled'}")
        if current_auto:
            self.console.print(f"Format: {current_format.upper()}")
            self.console.print(f"Delete source: {'✅ Yes' if current_delete else '❌ No'}")
        
        self.console.print()
        
        # Get new settings
        format_choice = InputValidator.get_choice(
            self.console,
            "Auto-conversion format: 1=Disable, 2=PDF, 3=CBZ",
            1, 3
        )
        
        if not format_choice:
            display.print_info("Configuration cancelled.")
            self._pause()
            return
        
        if format_choice == 1:
            # Disable auto-conversion
            config.set("conversion.auto_convert", False)
            config.set("conversion.default_format", "none")
            display.print_success("✅ Auto-conversion disabled")
        else:
            # Enable auto-conversion
            format_name = "pdf" if format_choice == 2 else "cbz"
            config.set("conversion.auto_convert", True)
            config.set("conversion.default_format", format_name)
            
            # Ask about deleting source
            delete_source = Confirm.ask("Delete source images after conversion?", default=False)
            config.set("conversion.delete_source_after_conversion", delete_source)
            
            display.print_success(f"✅ Auto-conversion enabled: {format_name.upper()}")
            if delete_source:
                display.print_info("🗑️  Source images will be deleted after conversion")
        
        # Save configuration
        config.save()
        self._pause()
    
    def _show_conversion_status(self):
        """Show current conversion settings."""
        from cli.commands.convert import show_conversion_status
        show_conversion_status()
        self._pause()
    
    def _get_conversion_options(self) -> Optional[dict]:
        """Get conversion options from user."""
        format_choice = InputValidator.get_choice(
            self.console,
            "Conversion format: 1=PDF, 2=CBZ",
            1, 2
        )
        
        if not format_choice:
            return None
        
        format_name = "pdf" if format_choice == 1 else "cbz"
        
        # Get quality setting
        quality = InputValidator.get_integer(
            self.console,
            f"Image quality for {format_name.upper()} (1-100)",
            1, 100
        )
        if not quality:
            quality = 85 if format_name == "pdf" else 90
        
        # Ask about deleting source
        delete_source = Confirm.ask("Delete source images after conversion?", default=False)
        
        return {
            'format': format_name,
            'quality': quality,
            'delete_source': delete_source
        }
    
    def _execute_single_conversion(self, directory: Path, options: dict):
        """Execute single gallery conversion."""
        from cli.commands.convert import convert_gallery
        
        try:
            convert_gallery(
                directory=str(directory),
                format_type=options['format'],
                output=None,
                delete_source=options['delete_source'],
                quality=options['quality']
            )
        except Exception as e:
            display.print_error(f"Conversion failed: {e}")
    
    def _execute_batch_conversion(self, directories: list, options: dict):
        """Execute batch gallery conversion."""
        from cli.commands.convert import batch_convert
        
        try:
            # Convert first directory's parent as base
            base_dir = str(directories[0].parent)
            
            batch_convert(
                base_directory=base_dir,
                format_type=options['format'],
                delete_source=options['delete_source'],
                pattern="*"
            )
        except Exception as e:
            display.print_error(f"Batch conversion failed: {e}")
    
    def _get_image_files(self, directory: Path) -> list:
        """Get image files from directory."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        return [f for f in directory.iterdir() 
                if f.is_file() and f.suffix.lower() in image_extensions]