#!/usr/bin/env python3
"""Compatibility launcher for Earth Simulator Enhanced."""

from main import (
    EnhancedEarthSimulator,
    check_dependencies,
    check_texture_files,
    main,
)
from core.config import ConfigStore as DataManager
from core.state import AnimationType, SimulatorState, ViewMode

__all__ = [
    "AnimationType",
    "DataManager",
    "EnhancedEarthSimulator",
    "SimulatorState",
    "ViewMode",
    "check_dependencies",
    "check_texture_files",
    "main",
]


if __name__ == "__main__":
    main()
