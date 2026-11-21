"""Reusable button geometry and drawing."""

from __future__ import annotations

import pygame


class Button:
    def __init__(self, rect: pygame.Rect, label: str, action: str):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action

    def draw(self, surface, font, hovered: bool = False) -> None:
        fill = (110, 160, 215) if hovered else (90, 145, 200)
        pygame.draw.rect(surface, fill, self.rect, border_radius=5)
        pygame.draw.rect(surface, (245, 245, 245), self.rect, 1, border_radius=5)
        text = font.render(self.label, True, (255, 255, 255))
        surface.blit(text, text.get_rect(center=self.rect.center))

    def contains(self, position: tuple[int, int]) -> bool:
        return self.rect.collidepoint(position)
