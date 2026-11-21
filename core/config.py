"""JSON configuration persistence."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "resolution": [1280, 720],
    "texture": "Default",
    "auto_rotate": True,
    "mouse_sensitivity": 0.2,
    "zoom_sensitivity": 0.1,
    "last_position": {"x": 0, "y": 180, "distance": -5},
    "view_mode": "Normal",
    "animation_enabled": False,
    "effects_enabled": True,
    "sound_enabled": True,
    "atmosphere_enabled": False,
}


class ConfigStore:
    def __init__(self, config_file: str | Path = "simulator_config.json"):
        self.config_file = Path(config_file)

    def save(self, config: dict) -> bool:
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(
                json.dumps(config, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except OSError:
            logger.exception("Could not save configuration to %s", self.config_file)
            return False
        return True

    def load(self) -> dict:
        if not self.config_file.exists():
            return DEFAULT_CONFIG.copy()
        try:
            config = json.loads(self.config_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.exception("Could not load configuration from %s", self.config_file)
            raise
        if not isinstance(config, dict):
            logger.error("Configuration must contain a JSON object: %s", self.config_file)
            raise ValueError(f"Configuration must be a JSON object: {self.config_file}")
        return {**DEFAULT_CONFIG, **config}

    def save_config(self, config: dict) -> bool:
        return self.save(config)

    def load_config(self) -> dict:
        return self.load()


DataManager = ConfigStore
