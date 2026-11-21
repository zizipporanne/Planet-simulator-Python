#!/usr/bin/env python3
"""Application entry point for Earth Simulator Enhanced."""

from __future__ import annotations

import logging
import math
import time
from datetime import datetime
from pathlib import Path

import pygame
from OpenGL.GL import (
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_FILL,
    GL_FRONT_AND_BACK,
    GL_LINE,
    GL_LINEAR,
    GL_MODELVIEW,
    GL_PACK_ALIGNMENT,
    GL_POINT,
    GL_PROJECTION,
    GL_QUADS,
    GL_RGBA,
    GL_RGB,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_UNSIGNED_BYTE,
    glBegin,
    glBindTexture,
    glBlendFunc,
    glCallList,
    glClear,
    glDisable,
    glEnable,
    glEnd,
    glMatrixMode,
    glLoadIdentity,
    glOrtho,
    glPopMatrix,
    glPixelStorei,
    glPolygonMode,
    glReadPixels,
    glPushMatrix,
    glTexCoord2f,
    glTexImage2D,
    glTexParameteri,
    glTexSubImage2D,
    glVertex2f,
    glColor4f,
)
from OpenGL.error import GLError
from PIL import Image

from core.config import ConfigStore
from core.input import InputController
from core.state import AnimationType, SimulatorState, ViewMode
from render.camera import Camera
from render.globe import GlobeRenderer
from render.texture import TEXTURE_FILES, TextureManager
from ui.notifications import Notification
from ui.side_panel import SidePanel
from ui.top_bar import TopBar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("earth_simulator.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)
SCRIPT_DIR = Path(__file__).resolve().parent
DISPLAY_SIZE = (1280, 720)


class EnhancedEarthSimulator:
    """Owns the event loop and connects the UI, state, and renderers."""

    def __init__(self, config_file: str | Path | None = None):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            logger.info("Audio device unavailable; sound control remains disabled.")
        pygame.display.set_caption("Earth Simulator Enhanced v2.0 - Adrian Lesniak")
        self.display = DISPLAY_SIZE
        self.screen = pygame.display.set_mode(self.display, pygame.DOUBLEBUF | pygame.OPENGL)
        self.state = SimulatorState()
        self.running = True
        self.ui_dirty = True
        self._hovered_action = None
        self.menu_font = pygame.font.Font(None, 28)
        self.text_font = pygame.font.Font(None, 23)
        self.small_font = pygame.font.Font(None, 20)
        self.top_bar = TopBar(self.display[0])
        self.side_panel = SidePanel(self.display)
        self.notification = Notification()
        self._notification_visible = False
        self.config = ConfigStore(config_file or "simulator_config.json")
        self.state.load_config(self.config.load())
        self.textures = TextureManager(SCRIPT_DIR)
        self.texture_ids = self.textures.load_all()
        self.camera = Camera(self.display)
        self.globe = GlobeRenderer()
        self.frame_count = 0
        self.fps = 0
        self.fps_started = time.monotonic()
        self.last_click_time = 0
        self.last_position = None
        self.double_click_delay = 300
        self.rotation_momentum = 0.92
        self.auto_rotate_speed = 0.1
        self.min_zoom = -15.0
        self.max_zoom = -2.0
        self.animation_speed = 1.0
        self.screenshot_counter = 0

        self._setup_opengl()
        self.globe.compile()
        self._setup_ui_texture()
        self.actions = {
            "view_mode": self.toggle_view_mode,
            "animation": self.toggle_animation,
            "stats": self.toggle_stats,
            "effects": self.toggle_effects,
            "atmosphere": self.toggle_atmosphere,
            "screenshot": self.take_screenshot,
            "sound": self.toggle_sound,
            "settings": lambda: self.open_section("Settings"),
            "help": lambda: self.open_section("Instructions"),
            "about": lambda: self.open_section("About"),
            "instructions": lambda: self.open_section("Instructions"),
            "save_state": self.save_state,
            "load_state": self.load_state,
            "reset_view": self.reset_view,
            "cycle_texture": self.cycle_texture,
            "toggle_menu": self.toggle_menu,
            "back": self.back_to_menu,
            "exit": self.quit_program,
        }
        self.input = InputController(self.actions)
        logger.info("Earth simulator initialized")

    def _setup_opengl(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.camera.setup_projection()

    def _setup_ui_texture(self) -> None:
        self.ui_surface = pygame.Surface(self.display, pygame.SRCALPHA)
        from OpenGL.GL import glGenTextures

        self.ui_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.ui_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, *self.display, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, None,
        )

    def mark_ui_dirty(self) -> None:
        self.ui_dirty = True

    def notify(self, message: str) -> None:
        self.notification.show(message)
        self._notification_visible = True
        self.mark_ui_dirty()

    def toggle_menu(self) -> None:
        self.side_panel.visible = not self.side_panel.visible
        self.side_panel.section = None
        self.mark_ui_dirty()

    def back_to_menu(self) -> None:
        self.side_panel.section = None
        self.mark_ui_dirty()

    def open_section(self, section: str) -> None:
        self.side_panel.visible = True
        self.side_panel.section = section
        self.mark_ui_dirty()

    def cycle_texture(self) -> None:
        self.state.cycle_texture(tuple(self.texture_ids))
        self.notify(f"Texture: {self.state.texture}")

    def toggle_view_mode(self) -> None:
        self.state.cycle_view_mode()
        self.notify(f"View mode: {self.state.view_mode.value}")

    def toggle_animation(self) -> None:
        self.state.animation_enabled = not self.state.animation_enabled
        if self.state.animation_enabled:
            self.state.animation_time = 0.0
        self.notify(f"Animation {'enabled' if self.state.animation_enabled else 'disabled'}")

    def toggle_stats(self) -> None:
        self.state.stats_enabled = not self.state.stats_enabled
        self.notify(f"Statistics {'enabled' if self.state.stats_enabled else 'disabled'}")

    def toggle_effects(self) -> None:
        self.state.effects_enabled = not self.state.effects_enabled
        self.notify(f"Effects {'enabled' if self.state.effects_enabled else 'disabled'}")

    def toggle_atmosphere(self) -> None:
        self.state.atmosphere_enabled = not self.state.atmosphere_enabled
        self.notify(f"Atmosphere {'enabled' if self.state.atmosphere_enabled else 'disabled'}")

    def toggle_sound(self) -> None:
        self.state.sound_enabled = not self.state.sound_enabled
        self.notify(f"Sound {'enabled' if self.state.sound_enabled else 'disabled'}")

    def save_state(self) -> None:
        if self.config.save(self.state.to_config()):
            self.notify("State saved")
        else:
            self.notify("Could not save state")

    def load_state(self) -> None:
        try:
            config = self.config.load()
            SimulatorState().load_config(config)
            self.state.load_config(config)
        except (OSError, TypeError, ValueError) as error:
            logger.exception("Configuration contains invalid simulator state")
            self.notify(f"Could not load state: {error}")
            return
        self.notify("State loaded")

    def reset_view(self) -> None:
        self.state.reset_view()
        self.notify("View reset")

    def quit_program(self) -> None:
        self.save_state()
        self.running = False

    def take_screenshot(self) -> None:
        self.screenshot_counter += 1
        filename = (
            f"screenshot_{datetime.now():%Y%m%d_%H%M%S}_"
            f"{self.screenshot_counter}.png"
        )
        try:
            glPixelStorei(GL_PACK_ALIGNMENT, 1)
            pixels = glReadPixels(
                0, 0, *self.display, GL_RGB, GL_UNSIGNED_BYTE
            )
            Image.frombytes("RGB", self.display, pixels).transpose(
                Image.Transpose.FLIP_TOP_BOTTOM
            ).save(filename)
        except (GLError, OSError, ValueError) as error:
            logger.exception("Could not save screenshot")
            self.notify(f"Screenshot failed: {error}")
            return
        self.notify(f"Screenshot saved: {filename}")

    def _handle_click(self, position) -> bool:
        action = self.top_bar.action_at(position) if position[1] < TopBar.HEIGHT else None
        if action is None:
            action = self.side_panel.action_at(position)
        return self.input.dispatch(action) if action else False

    def _hover_action_at(self, position) -> str | None:
        action = self.top_bar.action_at(position) if position[1] < TopBar.HEIGHT else None
        return action or self.side_panel.action_at(position)

    def _handle_mouse(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self._handle_click(event.pos):
                return
            if event.button == 1:
                now = pygame.time.get_ticks()
                if now - self.last_click_time < self.double_click_delay:
                    self.reset_view()
                self.last_click_time = now
                self.last_position = event.pos
                self.state.rotation_velocity = [0.0, 0.0]
            elif event.button in (4, 5):
                self._zoom(1 if event.button == 4 else -1)
        elif event.type == pygame.MOUSEWHEEL:
            self._zoom(event.y)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.last_position is not None:
                dx = (event.pos[0] - self.last_position[0]) * self.state.mouse_sensitivity
                dy = (event.pos[1] - self.last_position[1]) * self.state.mouse_sensitivity
                self.state.rotation_velocity = [dy * 0.1, dx * 0.1]
            self.last_position = None
        elif event.type == pygame.MOUSEMOTION:
            if self.last_position is not None:
                zoom_factor = self._zoom_rotation_factor()
                dx = (event.pos[0] - self.last_position[0]) * self.state.mouse_sensitivity * zoom_factor
                dy = (event.pos[1] - self.last_position[1]) * self.state.mouse_sensitivity * zoom_factor
                self.state.rotation_y += dx
                self.state.rotation_x = max(-85.0, min(85.0, self.state.rotation_x + dy))
                self.last_position = event.pos
                if self.state.stats_enabled:
                    self.mark_ui_dirty()
            hovered_action = self._hover_action_at(event.pos)
            if hovered_action != self._hovered_action:
                self._hovered_action = hovered_action
                self.mark_ui_dirty()

    def _zoom(self, direction: int) -> None:
        distance = self.state.distance + direction * self.state.zoom_sensitivity
        if self.min_zoom <= distance <= self.max_zoom:
            self.state.distance = distance
            if self.state.stats_enabled:
                self.mark_ui_dirty()

    def _zoom_rotation_factor(self) -> float:
        fraction = (self.state.distance - self.min_zoom) / (self.max_zoom - self.min_zoom)
        return max(0.05, 0.2 * fraction)

    def _update_state(self, dt: float) -> None:
        state = self.state
        if self.last_position is not None:
            if state.auto_rotate:
                state.auto_rotate = False
                if self.side_panel.section == "Settings":
                    self.mark_ui_dirty()
        elif state.auto_rotate:
            state.rotation_y += self.auto_rotate_speed
        if any(abs(value) > 1e-3 for value in state.rotation_velocity):
            state.rotation_x += state.rotation_velocity[0]
            state.rotation_y += state.rotation_velocity[1]
            state.rotation_velocity = [value * self.rotation_momentum for value in state.rotation_velocity]
        else:
            state.rotation_velocity = [0.0, 0.0]
        state.rotation_x = max(-85.0, min(85.0, state.rotation_x))
        if state.animation_enabled:
            state.animation_time += dt
            if state.animation_type == AnimationType.ROTATION:
                state.rotation_y += self.animation_speed * 0.5
            elif state.animation_type == AnimationType.ORBIT:
                state.rotation_x = math.sin(state.animation_time) * 30
                state.rotation_y += self.animation_speed * 0.3
            elif state.animation_type == AnimationType.ZOOM:
                state.distance = -5 + math.sin(state.animation_time * 0.5) * 2
            elif state.animation_type == AnimationType.FLYBY:
                state.rotation_x = math.sin(state.animation_time * 0.3) * 45
                state.rotation_y += self.animation_speed * 0.4
                state.distance = -5 + math.sin(state.animation_time * 0.2) * 3

    def _update_fps(self) -> None:
        self.frame_count += 1
        now = time.monotonic()
        if now - self.fps_started >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_started = now
            if self.state.stats_enabled:
                self.mark_ui_dirty()

    def _draw_stats(self, surface) -> None:
        lines = (
            f"FPS: {self.fps}",
            f"Mode: {self.state.view_mode.value}",
            f"Animation: {'ON' if self.state.animation_enabled else 'OFF'}",
            f"Effects: {'ON' if self.state.effects_enabled else 'OFF'}",
            f"Atmosphere: {'ON' if self.state.atmosphere_enabled else 'OFF'}",
            f"Position: X={self.state.rotation_x:.1f} Y={self.state.rotation_y:.1f}",
            f"Zoom: {abs(self.state.distance):.1f}",
        )
        for index, line in enumerate(lines):
            text = self.small_font.render(line, True, (255, 255, 255))
            rect = text.get_rect(topright=(self.display[0] - 12, 96 + index * 23))
            pygame.draw.rect(surface, (0, 0, 0, 170), rect.inflate(12, 6))
            surface.blit(text, rect)

    def _render_ui(self) -> None:
        surface = self.ui_surface
        surface.fill((0, 0, 0, 0))
        mouse = pygame.mouse.get_pos()
        self.top_bar.draw(surface, self.menu_font, mouse)
        self.side_panel.draw(surface, self.menu_font, self.state, mouse)
        if self.state.stats_enabled:
            self._draw_stats(surface)
        if self.notification.visible:
            text = self.text_font.render(self.notification.message, True, (255, 255, 255))
            panel = pygame.Rect(10, self.display[1] - 54, text.get_width() + 28, 38)
            pygame.draw.rect(surface, (40, 70, 95, 220), panel, border_radius=5)
            surface.blit(text, (panel.x + 14, panel.y + 9))
        glBindTexture(GL_TEXTURE_2D, self.ui_texture)
        glTexSubImage2D(
            GL_TEXTURE_2D, 0, 0, 0, *self.display,
            GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(surface, "RGBA", False),
        )
        self.ui_dirty = False

    def _draw_ui(self) -> None:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], self.display[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.ui_texture)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(self.display[0], 0)
        glTexCoord2f(1, 1); glVertex2f(*self.display)
        glTexCoord2f(0, 1); glVertex2f(0, self.display[1])
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def draw(self) -> None:
        if self.ui_dirty:
            self._render_ui()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self.state.effects_enabled:
            glEnable(GL_BLEND)
        else:
            glDisable(GL_BLEND)
        if self.state.view_mode == ViewMode.WIREFRAME:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        elif self.state.view_mode == ViewMode.POINTS:
            glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        Camera.apply(self.state)
        self.globe.draw(self.texture_ids.get(self.state.texture))
        self._draw_ui()
        pygame.display.flip()

    def run(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            dt = min(clock.tick(60) / 1000.0, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_program()
                elif event.type == pygame.KEYDOWN:
                    if self.input.handle_key(event.key):
                        continue
                elif event.type in (
                    pygame.MOUSEBUTTONDOWN,
                    pygame.MOUSEBUTTONUP,
                    pygame.MOUSEMOTION,
                    pygame.MOUSEWHEEL,
                ):
                    self._handle_mouse(event)
            self._update_state(dt)
            if self.side_panel.update_position():
                self.mark_ui_dirty()
            visible = self.notification.visible
            if visible != self._notification_visible:
                self._notification_visible = visible
                self.mark_ui_dirty()
            self._update_fps()
            self.draw()
        pygame.quit()


def check_dependencies() -> bool:
    """Return whether all runtime dependencies can be imported."""
    for module in ("pygame", "OpenGL", "numpy", "PIL"):
        try:
            __import__(module)
        except ImportError as error:
            print(f"Missing dependency {module}: {error}")
            print("Install dependencies with: pip install -r requirements.txt")
            return False
    return True


def check_texture_files() -> bool:
    """Return whether all required texture files exist next to the script."""
    missing = [name for name in TEXTURE_FILES.values() if not (SCRIPT_DIR / name).is_file()]
    if missing:
        print(f"Missing texture files: {', '.join(missing)}")
        return False
    return True


def main() -> None:
    if not check_dependencies() or not check_texture_files():
        raise SystemExit(1)
    try:
        EnhancedEarthSimulator().run()
    except Exception as error:
        logger.exception("Fatal simulator error")
        print(f"Error: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
