"""Window-independent simulation state and transitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ViewMode(Enum):
    NORMAL = "Normal"
    WIREFRAME = "Wireframe"
    POINTS = "Points"
    NIGHT = "Night"


class AnimationType(Enum):
    ROTATION = "Rotation"
    ORBIT = "Orbit"
    ZOOM = "Zoom"
    FLYBY = "Flyby"


TEXTURES = ("Default", "Political", "Detailed")


@dataclass
class SimulatorState:
    rotation_x: float = 0.0
    rotation_y: float = 180.0
    distance: float = -5.0
    texture: str = "Default"
    auto_rotate: bool = True
    mouse_sensitivity: float = 0.2
    zoom_sensitivity: float = 0.1
    view_mode: ViewMode = ViewMode.NORMAL
    animation_enabled: bool = False
    effects_enabled: bool = True
    sound_enabled: bool = True
    atmosphere_enabled: bool = False
    stats_enabled: bool = False
    animation_type: AnimationType = AnimationType.ROTATION
    animation_speed: float = 1.0
    animation_time: float = 0.0
    rotation_velocity: list[float] = field(default_factory=lambda: [0.0, 0.0])

    def cycle_texture(self, available: tuple[str, ...] = TEXTURES) -> str:
        if not available:
            return self.texture
        current = available.index(self.texture) if self.texture in available else -1
        self.texture = available[(current + 1) % len(available)]
        return self.texture

    def cycle_view_mode(self) -> ViewMode:
        modes = tuple(ViewMode)
        self.view_mode = modes[(modes.index(self.view_mode) + 1) % len(modes)]
        return self.view_mode

    def reset_view(self) -> None:
        self.rotation_x = 0.0
        self.rotation_y = 180.0
        self.distance = -5.0
        self.auto_rotate = True
        self.rotation_velocity = [0.0, 0.0]

    def to_config(self) -> dict:
        return {
            "texture": self.texture,
            "auto_rotate": self.auto_rotate,
            "mouse_sensitivity": self.mouse_sensitivity,
            "last_position": {
                "x": self.rotation_x,
                "y": self.rotation_y,
                "distance": self.distance,
            },
            "view_mode": self.view_mode.value,
            "animation_enabled": self.animation_enabled,
            "effects_enabled": self.effects_enabled,
            "sound_enabled": self.sound_enabled,
            "atmosphere_enabled": self.atmosphere_enabled,
        }

    def load_config(self, config: dict) -> None:
        position = config.get("last_position", {})
        self.rotation_x = float(position.get("x", self.rotation_x))
        self.rotation_y = float(position.get("y", self.rotation_y))
        self.distance = float(position.get("distance", self.distance))
        texture = config.get("texture", self.texture)
        if texture not in TEXTURES:
            raise ValueError(f"Unsupported Earth texture: {texture}")
        self.texture = texture
        self.auto_rotate = bool(config.get("auto_rotate", self.auto_rotate))
        self.mouse_sensitivity = float(
            config.get("mouse_sensitivity", self.mouse_sensitivity)
        )
        self.zoom_sensitivity = float(
            config.get("zoom_sensitivity", self.zoom_sensitivity)
        )
        self.view_mode = ViewMode(config.get("view_mode", self.view_mode.value))
        for key in (
            "animation_enabled",
            "effects_enabled",
            "sound_enabled",
            "atmosphere_enabled",
        ):
            if key in config:
                setattr(self, key, bool(config[key]))
