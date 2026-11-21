"""Main menu panel and its explicit actions."""

from __future__ import annotations

import pygame

from ui.buttons import Button


class SidePanel:
    WIDTH = 340
    HEIGHT = 600
    MENU_ACTIONS = (
        ("About", "about"),
        ("Instructions", "instructions"),
        ("Settings", "settings"),
        ("Save State", "save_state"),
        ("Load State", "load_state"),
        ("Reset View", "reset_view"),
        ("Exit", "exit"),
    )

    def __init__(self, display: tuple[int, int]):
        self.display = display
        self.visible = False
        self.x = float(display[0])
        self.section: str | None = None
        self.menu_buttons = [
            Button(pygame.Rect(16, 86 + i * 58, self.WIDTH - 32, 46), label, action)
            for i, (label, action) in enumerate(self.MENU_ACTIONS)
        ]
        self.back_button = Button(pygame.Rect(16, 78, self.WIDTH - 32, 44), "Back", "back")
        self.toggle_button = Button(
            pygame.Rect(display[0] - 116, 50, 100, 38), "Menu", "toggle_menu"
        )
        self.layer_button = Button(
            pygame.Rect(display[0] - 232, 50, 100, 38), "Layer", "cycle_texture"
        )

    def target_x(self) -> int:
        return self.display[0] - self.WIDTH if self.visible else self.display[0]

    def update_position(self) -> bool:
        target = self.target_x()
        old_x = self.x
        self.x += (target - self.x) * 0.3
        if abs(target - self.x) < 0.5:
            self.x = float(target)
        return self.x != old_x

    def action_at(self, position) -> str | None:
        if self.toggle_button.contains(position):
            return self.toggle_button.action
        if self.layer_button.contains(position):
            return self.layer_button.action
        local = (position[0] - int(self.x), position[1] - 120)
        if self.visible and self.section:
            return "back" if self.back_button.contains(local) else None
        if self.visible:
            return next(
                (button.action for button in self.menu_buttons if button.contains(local)),
                None,
            )
        return None

    def draw(self, surface, font, state, mouse_position) -> None:
        self.toggle_button.draw(surface, font, self.toggle_button.contains(mouse_position))
        self.layer_button.draw(surface, font, self.layer_button.contains(mouse_position))
        if not self.visible and abs(self.x - self.target_x()) < 0.5:
            return
        panel = pygame.Rect(int(self.x), 120, self.WIDTH, self.HEIGHT)
        pygame.draw.rect(surface, (255, 255, 255), panel)
        pygame.draw.rect(surface, (100, 130, 200), panel, 3)
        header = pygame.Rect(panel.x, panel.y, panel.width, 60)
        pygame.draw.rect(surface, (100, 150, 255), header)
        title = font.render("Main Menu", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=header.center))

        if self.section:
            self.back_button.draw(surface, font, self.back_button.contains(
                (mouse_position[0] - panel.x, mouse_position[1] - panel.y)
            ))
            lines = self._section_lines(state)
            for index, line in enumerate(lines):
                if line:
                    text = pygame.font.Font(None, 24).render(line, True, (50, 50, 50))
                    surface.blit(text, (panel.x + 18, panel.y + 142 + index * 30))
        else:
            for button in self.menu_buttons:
                screen_rect = button.rect.move(panel.x, panel.y)
                button.draw(surface, font, screen_rect.collidepoint(mouse_position))

    def _section_lines(self, state) -> list[str]:
        if self.section == "About":
            return [
                "Earth Simulator Enhanced v2.0",
                "Author: Adrian Lesniak",
                "Interactive 3D globe",
                "Three Earth textures",
                "Save and load view state",
            ]
        if self.section == "Instructions":
            return [
                "Drag to rotate the globe",
                "Use the wheel to zoom",
                "Double-click to reset",
                "L: change texture",
                "V: change view mode",
                "R: reset view",
                "Escape: exit",
            ]
        return [
            f"Texture: {state.texture}",
            f"View mode: {state.view_mode.value}",
            f"Auto-rotation: {'On' if state.auto_rotate else 'Off'}",
            f"Animation: {'On' if state.animation_enabled else 'Off'}",
            f"Effects: {'On' if state.effects_enabled else 'Off'}",
            f"Sound: {'On' if state.sound_enabled else 'Off'}",
        ]
