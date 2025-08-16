"""Configuration management for HFox Downloader."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .defaults import DEFAULT_CONFIG, CONFIG_DIRS, CONFIG_FILENAME


class ConfigManager:
    """Manages application configuration with YAML file support."""
    
    def __init__(self):
        self.config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self.config_path: Optional[Path] = None
        self._load_config()
    
    def _find_config_file(self) -> Optional[Path]:
        """Find the first existing config file in standard locations."""
        for config_dir in CONFIG_DIRS:
            config_file = config_dir / CONFIG_FILENAME
            if config_file.exists():
                return config_file
        return None
    
    def _create_default_config(self) -> Path:
        """Create default config file in user's home directory."""
        config_dir = CONFIG_DIRS[0]  # ~/.hfox
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / CONFIG_FILENAME
        self._save_config_to_file(config_file, self.config)
        return config_file
    
    def _load_config(self):
        """Load configuration from file or create default."""
        config_file = self._find_config_file()
        
        if config_file is None:
            config_file = self._create_default_config()
        
        self.config_path = config_file
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
            
            # Merge user config with defaults
            self._deep_merge(self.config, user_config)
            
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            print("Using default configuration.")
    
    def _deep_merge(self, base: Dict, update: Dict):
        """Recursively merge update dict into base dict."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _save_config_to_file(self, file_path: Path, config: Dict):
        """Save configuration to YAML file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    
    def get(self, key_path: str, default=None):
        """Get config value using dot notation (e.g., 'download.base_path')."""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """Set config value using dot notation."""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save current configuration to file."""
        if self.config_path:
            self._save_config_to_file(self.config_path, self.config)
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = DEFAULT_CONFIG.copy()
        self.save()


# Global config instance
config = ConfigManager()