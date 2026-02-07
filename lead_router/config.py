#!/usr/bin/env python3
"""
Configuration loader - YAML + Environment variables + CLI args
Supports dynamic updates via env var overrides
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# Default config path
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


class Config:
    """Dynamic configuration with file + env var support."""
    
    def __init__(self, config_path: Optional[Path] = None):
        # Allow custom config path via env var
        env_path = os.environ.get('LEAD_ROUTER_CONFIG_PATH')
        if env_path:
            self._path = Path(env_path)
        else:
            self._path = config_path or CONFIG_PATH
        self._data: Dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        """Load config from file."""
        if self._path.exists():
            with open(self._path) as f:
                self._data = yaml.safe_load(f) or {}
    
    def _env_override(self, key: str, default: Any) -> Any:
        """Get value with environment variable override."""
        env_key = f"LEAD_ROUTER_{key.upper().replace('.', '_')}"
        env_val = os.environ.get(env_key)
        
        if env_val is not None:
            # Type conversion
            if isinstance(default, bool):
                return env_val.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(default, int):
                return int(env_val)
            elif isinstance(default, float):
                return float(env_val)
            return env_val
        
        return default
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get config value by dot path (e.g., 'qualification.min_score')."""
        keys = path.split('.')
        value = self._data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return self._env_override(path, default)
            else:
                return self._env_override(path, default)
        
        return self._env_override(path, value if value is not None else default)
    
    # Convenience properties
    @property
    def min_score(self) -> int:
        return self.get('qualification.min_score', 40)
    
    @property
    def reddit_subs(self) -> List[Dict]:
        """Get enabled Reddit subreddits."""
        reddit_cfg = self._data.get('channels', {}).get('reddit', {})
        if not reddit_cfg.get('enabled', True):
            return []
        return reddit_cfg.get('subreddits', [])
    
    @property
    def indiehackers_enabled(self) -> bool:
        return self.get('channels.indiehackers.enabled', True)
    
    @property
    def upwork_enabled(self) -> bool:
        return self.get('channels.upwork.enabled', True)
    
    def reload(self) -> None:
        """Reload config from file."""
        self._load()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export current config as dict."""
        return self._data.copy()


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Force reload config from file."""
    global _config
    _config = Config()
    return _config


if __name__ == "__main__":
    cfg = get_config()
    print(f"Min score: {cfg.min_score}")
    print(f"Reddit subs: {len(cfg.reddit_subs)}")
    print(f"IndieHackers: {cfg.indiehackers_enabled}")
