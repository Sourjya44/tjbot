"""
Configuration file loading and merging for TJBot.

Handles loading TOML configuration files with cascading merge support.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import tomlkit
from tomlkit import TOMLDocument


class ConfigLoader:
    """Load and merge TJBot configuration files."""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / '.tjbot'
        self.user_config_path = self.config_dir / 'tjbot.toml'
        
        # Try to find node-tjbotlib default config
        self.default_config_path = self._find_default_config()
    
    def _find_default_config(self) -> Optional[Path]:
        """
        Find the default tjbot configuration from node-tjbotlib.
        
        Returns:
            Path to tjbot.default.toml or None if not found
        """
        # Common locations to check
        search_paths = [
            Path.home() / 'Desktop' / 'node-tjbotlib' / 'src' / 'config' / 'tjbot.default.toml',
            Path('/usr/local/lib/node_modules/node-tjbotlib/src/config/tjbot.default.toml'),
            Path('/usr/lib/node_modules/node-tjbotlib/src/config/tjbot.default.toml'),
            Path.home() / 'node_modules' / 'node-tjbotlib' / 'src' / 'config' / 'tjbot.default.toml',
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        return None
    
    def load_default_config(self) -> Optional[TOMLDocument]:
        """
        Load the default configuration from node-tjbotlib.
        
        Returns:
            TOMLDocument with default configuration or None if not found
        """
        if not self.default_config_path:
            return None
        
        try:
            with open(self.default_config_path, 'r', encoding='utf-8') as f:
                return tomlkit.load(f)
        except Exception as e:
            print(f"Warning: Could not load default config: {e}")
            return None
    
    def load_user_config(self) -> Optional[TOMLDocument]:
        """
        Load user configuration from ~/.tjbot/tjbot.toml.
        
        Returns:
            TOMLDocument with user configuration or None if doesn't exist
        """
        if not self.user_config_path.exists():
            return None
        
        try:
            with open(self.user_config_path, 'r', encoding='utf-8') as f:
                return tomlkit.load(f)
        except Exception as e:
            raise ValueError(f"Error loading user config: {e}")
    
    def merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two configuration dictionaries.
        
        Args:
            base: Base configuration (defaults)
            override: Override configuration (user settings)
        
        Returns:
            Merged configuration with override values taking precedence
        """
        if not override:
            return base
        
        if not base:
            return override
        
        result = dict(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self.merge_configs(result[key], value)
            else:
                # Override value (including lists/arrays - no element merging)
                result[key] = value
        
        return result
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load full configuration with cascade (default + user override).
        
        Returns:
            Merged configuration dictionary
        """
        # Load default config
        default_config = self.load_default_config()
        default_dict = dict(default_config) if default_config else {}
        
        # Load user config
        user_config = self.load_user_config()
        user_dict = dict(user_config) if user_config else {}
        
        # Merge
        return self.merge_configs(default_dict, user_dict)
    
    def get_config_value(self, config: Dict[str, Any], path: str) -> Any:
        """
        Get a nested configuration value by dot-separated path.
        
        Args:
            config: Configuration dictionary
            path: Dot-separated path (e.g., 'listen.backend.type')
        
        Returns:
            Value at path or None if not found
        """
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def has_user_config(self) -> bool:
        """Check if user configuration file exists."""
        return self.user_config_path.exists()
    
    def get_user_config_path(self) -> Path:
        """Get path to user configuration file."""
        return self.user_config_path
    
    def get_config_dir(self) -> Path:
        """Get path to configuration directory."""
        return self.config_dir


def load_tjbot_config() -> Dict[str, Any]:
    """
    Convenience function to load TJBot configuration.
    
    Returns:
        Merged configuration dictionary
    """
    loader = ConfigLoader()
    return loader.load_config()
