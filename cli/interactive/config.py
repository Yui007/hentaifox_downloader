"""Interactive configuration menu for HentaiFox Downloader."""

from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Confirm

from cli.utils.interactive_display import InteractiveMenu, InputValidator, StatusDisplay
from cli.utils.display import display
from config.settings import config


class ConfigMenu(InteractiveMenu):
    """Interactive configuration menu."""
    
    def __init__(self, console: Console):
        super().__init__(console, "Configuration Menu")
    
    def _display_menu(self):
        """Display the configuration menu."""
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Option", style="cyan", width=3)
        table.add_column("Description", style="white")
        
        menu_items = [
            ("1", "📥 Download Settings"),
            ("2", "📚 Conversion Settings"),
            ("3", "🚀 Performance Settings"),
            ("4", "🎨 Display Settings"),
            ("5", "📊 History Settings"),
            ("6", "👁️  View Current Config"),
            ("7", "🔄 Reset to Defaults"),
            ("8", "💾 Save Configuration"),
            ("9", "🔙 Back to Main Menu")
        ]
        
        for option, description in menu_items:
            table.add_row(option, description)
        
        panel = Panel(
            table,
            title="⚙️  Configuration Menu",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _get_choice(self) -> Optional[int]:
        """Get user menu choice."""
        return InputValidator.get_choice(self.console, "Enter your choice", 1, 9)
    
    def _handle_choice(self, choice: int):
        """Handle user menu choice."""
        self.console.print()
        
        if choice == 1:
            self._configure_download_settings()
        elif choice == 2:
            self._configure_conversion_settings()
        elif choice == 3:
            self._configure_performance_settings()
        elif choice == 4:
            self._configure_display_settings()
        elif choice == 5:
            self._configure_history_settings()
        elif choice == 6:
            self._view_current_config()
        elif choice == 7:
            self._reset_to_defaults()
        elif choice == 8:
            self._save_configuration()
        elif choice == 9:
            self.running = False
    
    def _configure_download_settings(self):
        """Configure download settings."""
        download_config = {
            "base_path": config.get("download.base_path"),
            "max_parallel_galleries": config.get("download.max_parallel_galleries", 2),
            "max_connections_per_server": config.get("download.max_connections_per_server", 4),
            "use_aria2": config.get("download.use_aria2", True),
            "retry_attempts": config.get("download.retry_attempts", 3)
        }
        
        StatusDisplay.show_config_section(self.console, "Download", download_config)
        
        if not Confirm.ask("Modify download settings?", default=False):
            self._pause()
            return
        
        # Base path
        if Confirm.ask("Change download directory?", default=False):
            new_path = InputValidator.get_string(self.console, "Enter new download directory")
            if new_path:
                config.set("download.base_path", new_path)
                display.print_success(f"Download directory set to: {new_path}")
        
        # Parallel galleries
        if Confirm.ask("Change max parallel galleries?", default=False):
            new_parallel = InputValidator.get_integer(
                self.console, 
                "Enter max parallel galleries", 
                1, 10
            )
            if new_parallel:
                config.set("download.max_parallel_galleries", new_parallel)
                display.print_success(f"Max parallel galleries set to: {new_parallel}")
        
        # Connections per server
        if Confirm.ask("Change max connections per server?", default=False):
            new_connections = InputValidator.get_integer(
                self.console,
                "Enter max connections per server",
                1, 32
            )
            if new_connections:
                config.set("download.max_connections_per_server", new_connections)
                display.print_success(f"Max connections per server set to: {new_connections}")
        
        # Aria2 usage
        if Confirm.ask("Change aria2c usage?", default=False):
            use_aria2 = Confirm.ask("Use aria2c for downloads?", default=True)
            config.set("download.use_aria2", use_aria2)
            status = "enabled" if use_aria2 else "disabled"
            display.print_success(f"Aria2c {status}")
        
        # Retry attempts
        if Confirm.ask("Change retry attempts?", default=False):
            new_retries = InputValidator.get_integer(
                self.console,
                "Enter retry attempts",
                0, 10
            )
            if new_retries is not None:
                config.set("download.retry_attempts", new_retries)
                display.print_success(f"Retry attempts set to: {new_retries}")
        
        self._pause()
    
    def _configure_conversion_settings(self):
        """Configure conversion settings."""
        conversion_config = {
            "auto_convert": config.get("conversion.auto_convert", False),
            "default_format": config.get("conversion.default_format", "none"),
            "delete_source_after_conversion": config.get("conversion.delete_source_after_conversion", False),
            "pdf_quality": config.get("conversion.pdf_quality", 85),
            "cbz_quality": config.get("conversion.cbz_quality", 90)
        }
        
        StatusDisplay.show_config_section(self.console, "Conversion", conversion_config)
        
        if not Confirm.ask("Modify conversion settings?", default=False):
            self._pause()
            return
        
        # Auto-conversion
        if Confirm.ask("Change auto-conversion?", default=False):
            format_choice = InputValidator.get_choice(
                self.console,
                "Auto-conversion: 1=Disable, 2=PDF, 3=CBZ",
                1, 3
            )
            
            if format_choice == 1:
                config.set("conversion.auto_convert", False)
                config.set("conversion.default_format", "none")
                display.print_success("Auto-conversion disabled")
            elif format_choice:
                format_name = "pdf" if format_choice == 2 else "cbz"
                config.set("conversion.auto_convert", True)
                config.set("conversion.default_format", format_name)
                display.print_success(f"Auto-conversion enabled: {format_name.upper()}")
        
        # Delete source
        if Confirm.ask("Change delete source setting?", default=False):
            delete_source = Confirm.ask("Delete source images after conversion?", default=False)
            config.set("conversion.delete_source_after_conversion", delete_source)
            status = "enabled" if delete_source else "disabled"
            display.print_success(f"Delete source after conversion {status}")
        
        # PDF quality
        if Confirm.ask("Change PDF quality?", default=False):
            pdf_quality = InputValidator.get_integer(
                self.console,
                "Enter PDF quality",
                1, 100
            )
            if pdf_quality:
                config.set("conversion.pdf_quality", pdf_quality)
                display.print_success(f"PDF quality set to: {pdf_quality}%")
        
        # CBZ quality
        if Confirm.ask("Change CBZ quality?", default=False):
            cbz_quality = InputValidator.get_integer(
                self.console,
                "Enter CBZ quality",
                1, 100
            )
            if cbz_quality:
                config.set("conversion.cbz_quality", cbz_quality)
                display.print_success(f"CBZ quality set to: {cbz_quality}%")
        
        self._pause()
    
    def _configure_performance_settings(self):
        """Configure performance settings."""
        # Redirect to performance menu from main interactive CLI
        display.print_info("Redirecting to Performance Settings...")
        self._pause()
    
    def _configure_display_settings(self):
        """Configure display settings."""
        display_config = {
            "show_progress": config.get("display.show_progress", True),
            "use_colors": config.get("display.use_colors", True),
            "log_level": config.get("display.log_level", "INFO")
        }
        
        StatusDisplay.show_config_section(self.console, "Display", display_config)
        
        if not Confirm.ask("Modify display settings?", default=False):
            self._pause()
            return
        
        # Show progress
        if Confirm.ask("Change progress bar setting?", default=False):
            show_progress = Confirm.ask("Show progress bars?", default=True)
            config.set("display.show_progress", show_progress)
            status = "enabled" if show_progress else "disabled"
            display.print_success(f"Progress bars {status}")
        
        # Use colors
        if Confirm.ask("Change color setting?", default=False):
            use_colors = Confirm.ask("Use colored output?", default=True)
            config.set("display.use_colors", use_colors)
            status = "enabled" if use_colors else "disabled"
            display.print_success(f"Colored output {status}")
        
        # Log level
        if Confirm.ask("Change log level?", default=False):
            log_choice = InputValidator.get_choice(
                self.console,
                "Log level: 1=ERROR, 2=WARNING, 3=INFO, 4=DEBUG",
                1, 4
            )
            
            if log_choice:
                levels = ["ERROR", "WARNING", "INFO", "DEBUG"]
                log_level = levels[log_choice - 1]
                config.set("display.log_level", log_level)
                display.print_success(f"Log level set to: {log_level}")
        
        self._pause()
    
    def _configure_history_settings(self):
        """Configure history settings."""
        history_config = {
            "enable_history": config.get("history.enable_history", True),
            "max_history_entries": config.get("history.max_history_entries", 10000)
        }
        
        StatusDisplay.show_config_section(self.console, "History", history_config)
        
        if not Confirm.ask("Modify history settings?", default=False):
            self._pause()
            return
        
        # Enable history
        if Confirm.ask("Change history tracking?", default=False):
            enable_history = Confirm.ask("Enable download history tracking?", default=True)
            config.set("history.enable_history", enable_history)
            status = "enabled" if enable_history else "disabled"
            display.print_success(f"History tracking {status}")
        
        # Max entries
        if Confirm.ask("Change max history entries?", default=False):
            max_entries = InputValidator.get_integer(
                self.console,
                "Enter max history entries",
                100, 100000
            )
            if max_entries:
                config.set("history.max_history_entries", max_entries)
                display.print_success(f"Max history entries set to: {max_entries}")
        
        self._pause()
    
    def _view_current_config(self):
        """View current configuration."""
        import yaml
        
        display.print_info("Current Configuration:")
        config_yaml = yaml.dump(config.config, default_flow_style=False, indent=2)
        
        # Create a panel with the config
        panel = Panel(
            config_yaml,
            title="📋 Current Configuration",
            border_style="green",
            expand=False
        )
        self.console.print(panel)
        self._pause()
    
    def _reset_to_defaults(self):
        """Reset configuration to defaults."""
        if not Confirm.ask("⚠️  Reset ALL settings to defaults? This cannot be undone!", default=False):
            display.print_info("Reset cancelled.")
            self._pause()
            return
        
        if not Confirm.ask("Are you absolutely sure?", default=False):
            display.print_info("Reset cancelled.")
            self._pause()
            return
        
        try:
            config.reset_to_defaults()
            display.print_success("✅ Configuration reset to defaults")
        except Exception as e:
            display.print_error(f"Failed to reset configuration: {e}")
        
        self._pause()
    
    def _save_configuration(self):
        """Save current configuration."""
        try:
            config.save()
            display.print_success("✅ Configuration saved successfully")
        except Exception as e:
            display.print_error(f"Failed to save configuration: {e}")
        
        self._pause()