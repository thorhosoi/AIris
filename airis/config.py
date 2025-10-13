"""
Configuration Manager for AIris

This module provides a singleton configuration manager that loads and manages
settings from config.yaml. It supports dot notation for nested configuration access.
"""

import yaml
from pathlib import Path
from typing import Any, Dict

class Config:
    """
    Singleton configuration manager.
    
    This class ensures only one instance exists throughout the application lifecycle
    and provides methods to get/set configuration values using dot notation.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of Config exists."""
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        if not hasattr(self, 'initialized'):
            self.config_path = Path(config_path)
            self.settings = self._load_config()
            self.initialized = True

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the YAML file.
        
        Returns:
            Dictionary containing all configuration settings
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
        """
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Configuration file not found at: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default=None) -> Any:
        """
        Retrieve a value from the configuration using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'ai_engines.default_engine')
            default: Default value to return if key is not found
            
        Returns:
            Configuration value or default if not found
            
        Example:
            >>> config.get('ai_engines.default_engine', 'claude')
            'gemini'
        """
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the configuration using dot notation and save to file.
        
        Args:
            key: Configuration key in dot notation (e.g., 'ai_engines.default_engine')
            value: Value to set
            
        Example:
            >>> config.set('ai_engines.default_engine', 'gemini')
        """
        keys = key.split('.')
        d = self.settings
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self._save_config()

    def _save_config(self) -> None:
        """Save the current configuration to the YAML file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.settings, f, allow_unicode=True, default_flow_style=False)

# Singleton instance
config = Config()