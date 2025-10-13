import yaml
from pathlib import Path

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = "config.yaml"):
        if not hasattr(self, 'initialized'):
            self.config_path = Path(config_path)
            self.settings = self._load_config()
            self.initialized = True

    def _load_config(self) -> dict:
        """Loads the configuration from the YAML file."""
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Configuration file not found at: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default=None):
        """Retrieves a value from the configuration using dot notation."""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def set(self, key: str, value):
        """Sets a value in the configuration using dot notation and saves it."""
        keys = key.split('.')
        d = self.settings
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self._save_config()

    def _save_config(self):
        """Saves the current configuration to the YAML file."""
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.settings, f)

# Singleton instance
config = Config()