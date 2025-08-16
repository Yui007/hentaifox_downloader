"""Performance optimization commands."""

import typer
from cli.utils.display import display
from config.settings import config
from config.performance import NETWORK_OPTIMIZATION


def enable_turbo_mode():
    """Enable turbo mode for maximum download speed."""
    display.print_info("🚀 Enabling Turbo Mode...")
    
    # Update configuration for maximum performance
    config.set("download.max_parallel_galleries", NETWORK_OPTIMIZATION["max_parallel_galleries"])
    config.set("download.max_connections_per_server", NETWORK_OPTIMIZATION["max_connections_per_server"])
    config.set("download.use_aria2", True)
    
    # Save configuration to persist changes
    config.save()
    
    display.print_success("✅ Turbo Mode enabled!")
    display.print_info("Performance settings:")
    display.print_info(f"  • Max parallel galleries: {NETWORK_OPTIMIZATION['max_parallel_galleries']}")
    display.print_info(f"  • Max connections per server: {NETWORK_OPTIMIZATION['max_connections_per_server']}")
    display.print_info("  • High-performance aria2c configuration active")
    display.print_warning("⚠️  Note: Higher resource usage and network load")


def disable_turbo_mode():
    """Disable turbo mode and restore default settings."""
    display.print_info("🐌 Disabling Turbo Mode...")
    
    # Restore default settings
    config.set("download.max_parallel_galleries", 2)
    config.set("download.max_connections_per_server", 4)
    
    # Save configuration to persist changes
    config.save()
    
    display.print_success("✅ Turbo Mode disabled - using default settings")


def show_performance_status():
    """Show current performance configuration."""
    display.print_info("📊 Current Performance Settings:")
    
    parallel_galleries = config.get("download.max_parallel_galleries", 2)
    connections_per_server = config.get("download.max_connections_per_server", 4)
    use_aria2 = config.get("download.use_aria2", True)
    
    display.print_info(f"  • Max parallel galleries: {parallel_galleries}")
    display.print_info(f"  • Max connections per server: {connections_per_server}")
    display.print_info(f"  • Aria2c enabled: {'✅' if use_aria2 else '❌'}")
    
    # Determine if turbo mode is active
    is_turbo = (parallel_galleries >= 4 and connections_per_server >= 8)
    mode = "🚀 TURBO" if is_turbo else "🐌 NORMAL"
    display.print_info(f"  • Current mode: {mode}")