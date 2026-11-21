"""Action dispatch and keyboard mappings."""

from __future__ import annotations

from collections.abc import Callable

import pygame


class InputController:
    KEY_ACTIONS = {
        pygame.K_l: "cycle_texture",
        pygame.K_r: "reset_view",
        pygame.K_v: "view_mode",
        pygame.K_a: "animation",
        pygame.K_s: "stats",
        pygame.K_e: "effects",
        pygame.K_t: "screenshot",
        pygame.K_m: "toggle_menu",
        pygame.K_ESCAPE: "exit",
    }

    def __init__(self, actions: dict[str, Callable[[], None]]):
        self.actions = actions

    def dispatch(self, action: str) -> bool:
        callback = self.actions.get(action)
        if callback is None:
            return False
        callback()
        return True

    def handle_key(self, key: int) -> bool:
        action = self.KEY_ACTIONS.get(key)
        return self.dispatch(action) if action else False
