"""Top action bar."""

from __future__ import annotations

import pygame

from ui.buttons import Button


class TopBar:
    ITEMS = (
        ("View", "view_mode"),
        ("Animation", "animation"),
        ("Stats", "stats"),
        ("Effects", "effects"),
        ("Atmosphere", "atmosphere"),
        ("Screenshot", "screenshot"),
        ("Sound", "sound"),
        ("Settings", "settings"),
        ("Help", "help"),
        ("Exit", "exit"),
    )
    HEIGHT = 40

    def __init__(self, width: int):
        self.width = width
        margin, gap = 8, 4
        button_width = (width - 2 * margin - (len(self.ITEMS) - 1) * gap) // len(self.ITEMS)
        self.buttons = [
            Button(
                pygame.Rect(margin + i * (button_width + gap), 5, button_width, 30),
                label,
                action,
            )
            for i, (label, action) in enumerate(self.ITEMS)
        ]

    def draw(self, surface, font, mouse_position) -> None:
        pygame.draw.rect(surface, (70, 130, 180), (0, 0, self.width, self.HEIGHT))
        pygame.draw.line(surface, (100, 130, 200), (0, 39), (self.width, 39), 2)
        for button in self.buttons:
            button.draw(surface, font, button.contains(mouse_position))

    def action_at(self, position) -> str | None:
        return next((button.action for button in self.buttons if button.contains(position)), None)
