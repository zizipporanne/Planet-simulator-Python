#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Earth Simulator Enhanced v2.0 (optimized version)
Author: Adrian Lesniak
Description: Advanced interactive 3D Earth simulator
Features: globe rotation, texture switching, interactive menu, save/load system
"""

# Import compatibility fix at the start
try:
    import compatibility_fix
except ImportError:
    print("Warning: compatibility_fix.py not found")

import sys
import os
import json
import logging
import time
import math
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Import Pygame and OpenGL after dependency check
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image

# Configuration logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('earth_simulator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TextureType(Enum):
    """Enum for texture types"""
    DEFAULT = "Default"
    POLITICAL = "Political"
    DETAILED = "Detailed"


class ViewMode(Enum):
    """Enum for view modes"""
    NORMAL = "Normal"
    WIREFRAME = "Wireframe"
    POINTS = "Points"
    NIGHT = "Night"


class AnimationType(Enum):
    """Enum for animation types"""
    ROTATION = "Rotation"
    ORBIT = "Orbit"
    ZOOM = "Zoom"
    FLYBY = "Flyby"


@dataclass
class SimulationConfig:
    """Simulation configuration class"""
    resolution: Tuple[int, int] = (1280, 720)
    fov: float = 45.0
    mouse_sensitivity: float = 0.2
    zoom_sensitivity: float = 0.1
    auto_rotate_speed: float = 0.1
    rotation_momentum: float = 0.92


class ColorScheme:
    """Color scheme for the UI"""
    # Light colors for better visibility
    BACKGROUND = (240, 240, 245)
    MENU_BG = (255, 255, 255)
    MENU_HEADER = (100, 150, 255)
    BUTTON_NORMAL = (180, 200, 255)
    BUTTON_HOVER = (150, 180, 255)
    BUTTON_BORDER = (100, 130, 200)
    TEXT_PRIMARY = (50, 50, 50)
    TEXT_SECONDARY = (80, 80, 80)
    TEXT_ACCENT = (255, 255, 255)
    SUCCESS = (100, 200, 100)
    WARNING = (255, 200, 100)
    ERROR = (255, 100, 100)
    INFO = (100, 150, 255)
    # Colors for the top bar
    TOPBAR_BG = (70, 130, 180)
    TOPBAR_TEXT = (255, 255, 255)
    TOPBAR_BUTTON = (90, 150, 200)
    TOPBAR_BUTTON_HOVER = (110, 170, 220)


class TopMenuBar:
    """Top bar with equal-width buttons that always fit the window."""

    HEIGHT = 40
    MARGIN = 10
    GAP = 6
    ITEMS = [
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
    ]

    def __init__(self, display_width: int):
        self.display_width = display_width
        self.font = pygame.font.Font(None, 24)
        count = len(self.ITEMS)
        width = (display_width - 2 * self.MARGIN - (count - 1) * self.GAP) // count
        self.buttons = []
        for i, (label, action) in enumerate(self.ITEMS):
            x = self.MARGIN + i * (width + self.GAP)
            self.buttons.append((pygame.Rect(x, 5, width, self.HEIGHT - 10), label, action))

    def draw(self, surface, colors: ColorScheme, mouse_pos):
        """Draws the top bar."""
        pygame.draw.rect(surface, colors.TOPBAR_BG, (0, 0, self.display_width, self.HEIGHT))
        pygame.draw.line(surface, colors.BUTTON_BORDER,
                         (0, self.HEIGHT - 1), (self.display_width, self.HEIGHT - 1), 2)
        for rect, label, _action in self.buttons:
            hovered = rect.collidepoint(mouse_pos)
            color = colors.TOPBAR_BUTTON_HOVER if hovered else colors.TOPBAR_BUTTON
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, colors.TEXT_ACCENT, rect, 1, border_radius=6)
            text = self.font.render(label, True, colors.TEXT_ACCENT)
            surface.blit(text, text.get_rect(center=rect.center))

    def handle_click(self, pos):
        """Returns the action of the clicked button, or None."""
        for rect, _label, action in self.buttons:
            if rect.collidepoint(pos):
                return action
        return None



    def __init__(self, display_width: int):
        self.display_width = display_width
        self.height = 40
        self.buttons = []
        self.font = pygame.font.Font(None, 24)
        self.setup_buttons()

    def setup_buttons(self):
        """Konfiguruje przyciski paska menu"""
        button_width = 120
        spacing = 10
        x = 10

        self.buttons = [
            {"text": "View", "action": "view_mode", "x": x},
            {"text": "Animation", "action": "animation", "x": x + (button_width + spacing) * 1},
            {"text": "Stats", "action": "stats", "x": x + (button_width + spacing) * 2},
            {"text": "Effects", "action": "effects", "x": x + (button_width + spacing) * 3},
            {"text": "Atmosphere", "action": "atmosphere", "x": x + (button_width + spacing) * 4},
            {"text": "Screenshot", "action": "screenshot", "x": x + (button_width + spacing) * 5},
            {"text": "Sound", "action": "sound", "x": x + (button_width + spacing) * 6},
            {"text": "Settings", "action": "settings", "x": x + (button_width + spacing) * 7},
            {"text": "Help", "action": "help", "x": x + (button_width + spacing) * 8},
            {"text": "Exit", "action": "exit", "x": x + (button_width + spacing) * 9}
        ]

    def draw(self, surface, colors: ColorScheme):
        """Draws the top bar"""
        topbar_rect = pygame.Rect(0, 0, self.display_width, self.height)
        pygame.draw.rect(surface, colors.TOPBAR_BG, topbar_rect)

        pygame.draw.line(surface, colors.BUTTON_BORDER,
                         (0, self.height), (self.display_width, self.height), 2)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button_rect = pygame.Rect(button["x"], 5, 120, 30)
            hovered = button_rect.collidepoint(mouse_pos[0], mouse_pos[1])

            color = colors.TOPBAR_BUTTON_HOVER if hovered else colors.TOPBAR_BUTTON
            pygame.draw.rect(surface, color, button_rect)
            pygame.draw.rect(surface, colors.TEXT_ACCENT, button_rect, 1)

            text_surface = self.font.render(button["text"], True, colors.TEXT_ACCENT)
            text_rect = text_surface.get_rect(center=button_rect.center)
            surface.blit(text_surface, text_rect)

    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Handles clicks w pasek menu"""
        for button in self.buttons:
            button_rect = pygame.Rect(button["x"], 5, 120, 30)
            if button_rect.collidepoint(pos[0], pos[1]):
                return button["action"]
        return None


class EnhancedButton:
    """Button class with hover animation"""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 icon: Optional[str] = None, tooltip: Optional[str] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.tooltip = tooltip
        self.hovered = False
        self.clicked = False
        self.animation_time = 0
        self.original_y = y

    def draw(self, surface, font, colors: ColorScheme):
        if self.hovered:
            self.animation_time = min(self.animation_time + 0.2, 1.0)
        else:
            self.animation_time = max(self.animation_time - 0.2, 0.0)
        y_offset = int(5 * self.animation_time)

        color = colors.BUTTON_HOVER if self.hovered else colors.BUTTON_NORMAL
        border_color = colors.BUTTON_BORDER

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        shadow_rect = self.rect.copy()
        shadow_rect.y += 2
        pygame.draw.rect(surface, (200, 200, 200), shadow_rect)

        text_surface = font.render(self.text, True, colors.TEXT_PRIMARY)
        shadow_surface = font.render(self.text, True, colors.TEXT_SECONDARY)

        text_rect = text_surface.get_rect(center=self.rect.center)
        text_rect.y -= y_offset

        surface.blit(shadow_surface, (text_rect.x + 1, text_rect.y + 1))
        surface.blit(text_surface, text_rect)

        if self.hovered and self.tooltip:
            self.draw_tooltip(surface, font, colors)

    def draw_tooltip(self, surface, font, colors):
        tooltip_surface = font.render(self.tooltip, True, colors.TEXT_ACCENT)
        tooltip_bg = pygame.Surface((tooltip_surface.get_width() + 10,
                                     tooltip_surface.get_height() + 6))
        tooltip_bg.fill(colors.TEXT_PRIMARY)
        tooltip_bg.set_alpha(200)

        tooltip_rect = tooltip_bg.get_rect()
        tooltip_rect.centerx = self.rect.centerx
        tooltip_rect.bottom = self.rect.top - 5

        surface.blit(tooltip_bg, tooltip_rect)
        surface.blit(tooltip_surface, (tooltip_rect.x + 5, tooltip_rect.y + 3))

    def handle_event(self, event, menu_pos: Tuple[int, int] = (0, 0)) -> bool:
        adjusted_pos = (event.pos[0] - menu_pos[0], event.pos[1] - menu_pos[1])

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(adjusted_pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(adjusted_pos):
                self.clicked = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.clicked = False

        return False


class DataManager:
    """Data manager - save/load configuration"""

    def __init__(self, config_file: str = "simulator_config.json"):
        self.config_file = config_file
        self.default_config = {
            "resolution": [1280, 720],
            "texture": "Default",
            "auto_rotate": True,
            "mouse_sensitivity": 0.2,
            "zoom_sensitivity": 0.1,
            "last_position": {"x": 0, "y": 180, "distance": -5},
            "view_mode": "Normal",
            "animation_enabled": False,
            "sound_enabled": True,
            "effects_enabled": True
        }

    def save_config(self, config: Dict) -> bool:
        """Saves the configuration to a file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False

    def load_config(self) -> Dict:
        """Loads the configuration from a file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_file}")
                return config
            else:
                logger.info("No config file found, using default settings")
                return self.default_config.copy()
        except Exception as e:
            logger.error(f"Error reading configuration: {e}")
            return self.default_config.copy()


class EnhancedEarthSimulator:
    """Earth simulator with advanced features"""

    def __init__(self):
        """Simulator initialization"""
        self.setup_pygame()
        self.setup_opengl()
        self.setup_variables()
        self.setup_ui()
        self.setup_textures()
        self.setup_earth_list()
        self.setup_ui_texture()
        self.setup_new_features()
        self.data_manager = DataManager()
        self.load_saved_config()

        logger.info("Earth simulator initialized successfully")

    def setup_pygame(self):
        """Pygame setup"""
        try:
            pygame.init()
            pygame.mixer.init()

            self.display = (1280, 720)
            pygame.display.set_caption('Earth Simulator Enhanced v2.0 - Adrian Lesniak')

            try:
                icon = pygame.image.load('earth_icon.png')
                pygame.display.set_icon(icon)
            except Exception:
                pass

            self.screen = pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)

        except Exception as e:
            logger.error(f"Pygame initialization error: {e}")
            raise

    def setup_opengl(self):
        """OpenGL setup"""
        try:
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            self.fov = 45
            self.aspect = self.display[0] / self.display[1]
            self.near = 0.1
            self.far = 50.0

            self.update_perspective()

        except Exception as e:
            logger.error(f"OpenGL configuration error: {e}")
            raise

    def setup_variables(self):
        """Simulation variable initialization"""
        self.distance = -5
        self.rotation_x = 0
        self.rotation_y = 180
        self.last_pos = None
        self.rotation_velocity = [0.0, 0.0]
        self.auto_rotate = True
        self.auto_rotate_speed = 0.1
        self.mouse_sensitivity = 0.2
        self.zoom_sensitivity = 0.1
        self.rotation_momentum = 0.92
        self.min_zoom = -15
        self.max_zoom = -2
        self.last_click_time = 0
        self.double_click_delay = 300

        # Stan menu
        self.show_menu = False
        self.current_section = None
        self.menu_position = self.display[0]
        self.menu_width = 400
        self.menu_height = 600
        self.menu_y = 120

        self.colors = ColorScheme()

        self.current_texture = 'Default'
        self.texture_files = {
            'Default': 'earth_texture.png',
            'Political': 'earth_political.png',
            'Detailed': 'earth_detailed.jpg'
        }
        self.textures = {}

        self.view_mode = ViewMode.NORMAL
        self.animation_enabled = False
        self.effects_enabled = True
        self.sound_enabled = True
        self.atmosphere_enabled = False
        self.stats_enabled = False

        self.ui_dirty = True

    def setup_ui(self):
        """User interface setup"""
        self.title_font = pygame.font.Font(None, 48)
        self.menu_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)

        self.top_menu = TopMenuBar(self.display[0])

        self.buttons = {
            'main': [
                EnhancedButton(20, 140, 360, 50, "About",
                               tooltip="About the simulator"),
                EnhancedButton(20, 200, 360, 50, "Instructions",
                               tooltip="How to use the program"),
                EnhancedButton(20, 260, 360, 50, "Settings",
                               tooltip="Simulator configuration"),
                EnhancedButton(20, 320, 360, 50, "Save State",
                               tooltip="Save the current position"),
                EnhancedButton(20, 380, 360, 50, "Load State",
                               tooltip="Load the saved position"),
                EnhancedButton(20, 440, 360, 50, "Reset View",
                               tooltip="Restore the default view"),
                EnhancedButton(20, 500, 360, 50, "Exit",
                               tooltip="Close the program")
            ]
        }

        self.menu_btn = EnhancedButton(self.display[0] - 120, 50, 100, 40, "Menu",
                                       tooltip="Open the main menu")
        self.layer_btn = EnhancedButton(self.display[0] - 240, 50, 100, 40, "Layer",
                                        tooltip="Change the Earth texture")

        self.menu_sections = {
            'About': [
                "Earth Simulator Enhanced v2.0",
                "Author: Adrian Lesniak",
                "Date: 2024",
                "",
                "Features:",
                "• Interactive 3D rotation",
                "• Different Earth textures",
                "• Save/load system",
                "• Advanced interface",
                "• Animations and effects",
                "• Top menu bar",
                "• 10 new features"
            ],
            'Instructions': [
                "Mouse controls:",
                "• Drag - rotate the globe",
                "• Scroll wheel - zoom in/out",
                "• Double click - reset",
                "",
                "Keys:",
                "• M - main menu",
                "• L - change layer",
                "• ESC - exit",
                "• R - reset view",
                "",
                "Top bar:",
                "• View - change display mode",
                "• Animation - toggle animations",
                "• Stats - program information",
                "• Effects - visual effects",
                "• Atmosphere - atmosphere simulation",
                "• Screenshot - take a picture",
                "• Sound - toggle sound",
                "• Settings - configuration",
                "• Help - instructions",
                "• Exit - close the program"
            ],
            'Settings': [
                "Current settings:",
                f"• Resolution: {self.display[0]}x{self.display[1]}",
                f"• Layer: {self.current_texture}",
                f"• View mode: {self.view_mode.value}",
                f"• Auto-rotation: {'On' if self.auto_rotate else 'Off'}",
                f"• Animations: {'On' if self.animation_enabled else 'Off'}",
                f"• Effects: {'On' if self.effects_enabled else 'Off'}",
                f"• Sound: {'On' if self.sound_enabled else 'Off'}",
                "",
                "Available options:",
                "• Change resolution",
                "• Adjust sensitivity",
                "• Toggle features",
                "• Save settings"
            ]
        }

        self.create_menu_surface()

    def setup_textures(self):
        """Texture setup"""
        self.load_all_textures()

    def setup_earth_list(self, radius: float = 2.0, segments: int = 32):
        """Generates the sphere once and keeps it in a display list."""
        lat = np.pi * (-0.5 + np.arange(segments + 1) / segments)
        lon = 2 * np.pi * np.arange(segments + 1) / segments
        lat_g, lon_g = np.meshgrid(lat, lon, indexing='ij')
        X = np.cos(lat_g) * np.cos(lon_g) * radius
        Y = np.sin(lat_g) * radius
        Z = np.cos(lat_g) * np.sin(lon_g) * radius

        def vert(i, j):
            glTexCoord2f(1.0 - j / segments, i / segments)
            glVertex3f(X[i, j], Y[i, j], Z[i, j])

        self.earth_list = glGenLists(1)
        glNewList(self.earth_list, GL_COMPILE)
        glBegin(GL_TRIANGLES)
        for i in range(segments):
            for j in range(segments):
                vert(i, j); vert(i + 1, j); vert(i + 1, j + 1)
                vert(i, j); vert(i + 1, j + 1); vert(i, j + 1)
        glEnd()
        glEndList()

    def setup_ui_texture(self):
        """RGBA texture the pygame UI is drawn onto."""
        w, h = self.display
        self.ui_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.ui_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.ui_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, None)
        self.ui_dirty = True

    def setup_new_features(self):
        """New features setup"""
        self.animation_type = AnimationType.ROTATION
        self.animation_speed = 1.0
        self.animation_time = 0

        self.wireframe_mode = False
        self.points_mode = False
        self.night_mode = False

        self.fps_counter = 0
        self.frame_count = 0
        self.start_time = time.time()

        self.screenshot_counter = 0

        self.sound_volume = 0.5

        self.atmosphere_density = 0.1
        self.clouds_enabled = False

    def load_saved_config(self):
        """Loads the saved configuration"""
        config = self.data_manager.load_config()

        if 'last_position' in config:
            pos = config['last_position']
            self.rotation_x = pos.get('x', 0)
            self.rotation_y = pos.get('y', 180)
            self.distance = pos.get('distance', -5)

        if 'texture' in config:
            self.current_texture = config['texture']

        if 'auto_rotate' in config:
            self.auto_rotate = config['auto_rotate']

        if 'mouse_sensitivity' in config:
            self.mouse_sensitivity = config['mouse_sensitivity']

        if 'view_mode' in config:
            self.view_mode = ViewMode(config['view_mode'])
        if 'animation_enabled' in config:
            self.animation_enabled = config['animation_enabled']
        if 'effects_enabled' in config:
            self.effects_enabled = config['effects_enabled']
        if 'sound_enabled' in config:
            self.sound_enabled = config['sound_enabled']
        if 'atmosphere_enabled' in config:
            self.atmosphere_enabled = config['atmosphere_enabled']

        self.ui_dirty = True

    def update_perspective(self):
        """Updates the OpenGL perspective"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.aspect, self.near, self.far)
        glMatrixMode(GL_MODELVIEW)

    def apply_camera(self):
        """Applies the camera directly (no glGetFloatv)."""
        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.distance)
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)

    def load_all_textures(self):
        """Loads all textures"""
        for name, file in self.texture_files.items():
            try:
                self.textures[name] = self.load_texture(file)
                logger.info(f"Texture {name} loaded successfully")
            except Exception as e:
                logger.error(f"Error loading texture {file}: {e}")

    def load_texture(self, filename: str):
        """Loads the texture keeping the original pixels (no smoothing)."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, filename)

            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Texture file does not exist: {image_path}")

            image = Image.open(image_path).convert('RGB')

            # Only downscale if the image exceeds the GPU limit
            max_size = int(glGetIntegerv(GL_MAX_TEXTURE_SIZE))
            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size))
                logger.info(f"{filename} resized to fit the GPU limit ({max_size}px)")

            image_data = image.tobytes("raw", "RGB", 0, -1)

            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)

            # NEAREST keeps pixels sharp; switch to GL_LINEAR for smoothing
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height,
                         0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

            return texture_id

        except Exception as e:
            logger.error(f"Error loading texture {filename}: {e}")
            raise




    def draw_earth(self):
        """Draws the globe using the precompiled display list"""
        glEnable(GL_TEXTURE_2D)
        tex = self.textures.get(self.current_texture)
        if tex:
            glBindTexture(GL_TEXTURE_2D, tex)
        glCallList(self.earth_list)
        glDisable(GL_TEXTURE_2D)

    def setup_2d_mode(self):
        """Switches to 2D mode for the UI"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], self.display[1], 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def setup_3d_mode(self):
        """Switches back to 3D mode"""
        glDisable(GL_BLEND)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def create_menu_surface(self):
        """Creates the menu surface"""
        self.menu_surface = pygame.Surface((self.menu_width, self.menu_height),
                                           pygame.SRCALPHA)
        self.update_menu_surface()

    def update_menu_surface(self):
        """Updates the menu surface"""
        self.menu_surface.fill(self.colors.MENU_BG)

        header_rect = pygame.Rect(0, 0, self.menu_width, 60)
        pygame.draw.rect(self.menu_surface, self.colors.MENU_HEADER, header_rect)

        pygame.draw.rect(self.menu_surface, self.colors.BUTTON_BORDER,
                         (0, 0, self.menu_width, self.menu_height), 3)

        title_text = self.menu_font.render("Main Menu", True, self.colors.TEXT_ACCENT)
        title_rect = title_text.get_rect(center=(self.menu_width // 2, 30))
        self.menu_surface.blit(title_text, title_rect)

        if self.current_section:
            back_btn = EnhancedButton(20, 80, 360, 50, "Back")
            back_btn.draw(self.menu_surface, self.menu_font, self.colors)

            y = 150
            for line in self.menu_sections[self.current_section]:
                if line.strip():
                    text_surface = self.text_font.render(line, True, self.colors.TEXT_PRIMARY)
                    self.menu_surface.blit(text_surface, (20, y))
                y += 35
        else:
            for button in self.buttons['main']:
                button.draw(self.menu_surface, self.menu_font, self.colors)

        self.ui_dirty = True

    def draw_menu(self, surface):
        """Draws the sliding menu onto the UI surface"""
        target = self.display[0] - self.menu_width
        self.menu_position += (target - self.menu_position) * 0.3
        surface.blit(self.menu_surface, (int(self.menu_position), self.menu_y))

    def draw_stats(self, surface):
        """Draws the stats"""
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.start_time >= 1.0:
            self.fps_counter = self.frame_count
            self.frame_count = 0
            self.start_time = current_time

        stats_text = [
            f"FPS: {self.fps_counter}",
            f"Mode: {self.view_mode.value}",
            f"Animation: {'ON' if self.animation_enabled else 'OFF'}",
            f"Effects: {'ON' if self.effects_enabled else 'OFF'}",
            f"Atmosphere: {'ON' if self.atmosphere_enabled else 'OFF'}",
            f"Position: X={self.rotation_x:.1f}° Y={self.rotation_y:.1f}°",
            f"Zoom: {abs(self.distance):.1f}"
        ]

        y_offset = 100
        for i, text in enumerate(stats_text):
            text_surface = self.small_font.render(text, True, self.colors.TEXT_ACCENT)
            text_rect = text_surface.get_rect()
            text_rect.topright = (self.display[0] - 10, y_offset + i * 20)

            bg_rect = text_rect.inflate(10, 5)
            pygame.draw.rect(surface, (0, 0, 0, 150), bg_rect)
            surface.blit(text_surface, text_rect)

    def render_ui(self):
        """Draws the whole UI onto one Surface and uploads it as a texture (only when it changes)."""
        s = self.ui_surface
        s.fill((0, 0, 0, 0))
        mouse = pygame.mouse.get_pos()
        self.top_menu.draw(s, self.colors, mouse)
        self.menu_btn.hovered = self.menu_btn.rect.collidepoint(mouse)
        self.layer_btn.hovered = self.layer_btn.rect.collidepoint(mouse)
        self.menu_btn.draw(s, self.menu_font, self.colors)
        self.layer_btn.draw(s, self.menu_font, self.colors)
        if self.show_menu:
            self.draw_menu(s)
        if self.stats_enabled:
            self.draw_stats(s)

        data = pygame.image.tostring(s, 'RGBA', False)
        glBindTexture(GL_TEXTURE_2D, self.ui_tex)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.display[0], self.display[1],
                        GL_RGBA, GL_UNSIGNED_BYTE, data)
        self.ui_dirty = False


    def draw_ui_overlay(self):
        """Draws the UI texture as a 2D quad over the scene."""
        w, h = self.display
        self.setup_2d_mode()
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.ui_tex)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(w, 0)
        glTexCoord2f(1, 1); glVertex2f(w, h)
        glTexCoord2f(0, 1); glVertex2f(0, h)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        self.setup_3d_mode()

    def draw(self):
        """Per-frame rendering: camera, globe and UI when needed."""
        if self.ui_dirty:
            self.render_ui()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        self.apply_camera()
        self.draw_earth()
        self.draw_ui_overlay()
        pygame.display.flip()

    def show_message(self, title: str, message: str):
        """Shows a message to the user"""
        self.current_section = None
        self.update_menu_surface()
        self.ui_dirty = True

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    break

            self.draw()
            pygame.time.wait(16)

    def handle_menu(self, event) -> bool:
        """Handles menu events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            menu_x = int(self.menu_position)

            if self.layer_btn.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.cycle_texture()
                return True

            if self.menu_btn.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.show_menu = not self.show_menu
                self.current_section = None
                self.update_menu_surface()
                return True

            if self.show_menu:
                if self.current_section:
                    back_btn = EnhancedButton(20, 80, 360, 50, "Back")
                    back_pos = (mouse_pos[0] - menu_x, mouse_pos[1] - self.menu_y)
                    if back_btn.rect.collidepoint(back_pos):
                        self.current_section = None
                        self.update_menu_surface()
                        return True
                else:
                    adjusted_pos = (mouse_pos[0] - menu_x, mouse_pos[1] - self.menu_y)
                    for i, button in enumerate(self.buttons['main']):
                        if button.rect.collidepoint(adjusted_pos):
                            self.handle_menu_action(i)
                            return True

        return False

    def handle_menu_action(self, button_index: int):
        """Handles menu actions"""
        actions = [
            self.show_about,
            self.show_instructions,
            self.show_settings,
            self.save_state,
            self.load_state,
            self.reset_view,
            self.quit_program
        ]

        if 0 <= button_index < len(actions):
            actions[button_index]()

    def cycle_texture(self):
        """Changes the Earth texture"""
        textures = list(self.textures.keys())
        if textures:
            current_idx = textures.index(self.current_texture)
            next_idx = (current_idx + 1) % len(textures)
            self.current_texture = textures[next_idx]

            self.menu_sections['Settings'][2] = f"• Layer: {self.current_texture}"
            self.update_menu_surface()

            logger.info(f"Texture changed to: {self.current_texture}")

    def show_about(self):
        """Shows program information"""
        self.current_section = 'About'
        self.update_menu_surface()
        self.show_message("About", "Press any key to return to the menu")

    def show_instructions(self):
        """Shows instructions"""
        self.current_section = 'Instructions'
        self.update_menu_surface()
        self.show_message("Instructions", "Press any key to return to the menu")

    def show_settings(self):
        """Shows settings"""
        self.current_section = 'Settings'
        self.update_menu_surface()
        self.show_message("Settings", "Press any key to return to the menu")

    def save_state(self):
        """Saves the current state"""
        config = {
            "last_position": {
                "x": self.rotation_x,
                "y": self.rotation_y,
                "distance": self.distance
            },
            "texture": self.current_texture,
            "auto_rotate": self.auto_rotate,
            "mouse_sensitivity": self.mouse_sensitivity,
            "view_mode": self.view_mode.value,
            "animation_enabled": self.animation_enabled,
            "effects_enabled": self.effects_enabled,
            "sound_enabled": self.sound_enabled,
            "atmosphere_enabled": self.atmosphere_enabled
        }

        if self.data_manager.save_config(config):
            self.show_message("Saved", "State saved successfully!")
        else:
            self.show_message("Error", "Failed to save state!")

    def load_state(self):
        """Loads the saved state"""
        config = self.data_manager.load_config()

        if 'last_position' in config:
            pos = config['last_position']
            self.rotation_x = pos.get('x', 0)
            self.rotation_y = pos.get('y', 180)
            self.distance = pos.get('distance', -5)
            self.show_message("Loaded", "State loaded successfully!")
        else:
            self.show_message("Error", "No saved state!")

    def reset_view(self):
        """Resets the view to the default position"""
        self.rotation_x = 0
        self.rotation_y = 180
        self.distance = -5
        self.auto_rotate = True
        self.show_message("Reset", "View has been reset!")

    def quit_program(self):
        """Closes the program"""
        self.save_state()
        pygame.quit()
        sys.exit(0)

    def handle_top_menu_click(self, action: str):
        """Handles clicks on the top bar"""
        if action == "view_mode":
            self.toggle_view_mode()
        elif action == "animation":
            self.toggle_animation()
        elif action == "stats":
            self.toggle_stats()
        elif action == "effects":
            self.toggle_effects()
        elif action == "atmosphere":
            self.toggle_atmosphere()
        elif action == "screenshot":
            self.take_screenshot()
        elif action == "sound":
            self.toggle_sound()
        elif action == "settings":
            self.show_settings_menu()
        elif action == "help":
            self.show_help_menu()
        elif action == "exit":
            self.exit_program()

    def toggle_view_mode(self):
        """Changes the view mode (Normal/Wireframe/Points/Night)"""
        modes = [ViewMode.NORMAL, ViewMode.WIREFRAME, ViewMode.POINTS, ViewMode.NIGHT]
        current_index = modes.index(self.view_mode)
        next_index = (current_index + 1) % len(modes)
        self.view_mode = modes[next_index]

        if self.view_mode == ViewMode.WIREFRAME:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        elif self.view_mode == ViewMode.POINTS:
            glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        self.show_message("View Mode", f"Changed to: {self.view_mode.value}")
        logger.info(f"View mode changed to: {self.view_mode.value}")

    def toggle_animation(self):
        """Toggles animations"""
        self.animation_enabled = not self.animation_enabled

        if self.animation_enabled:
            self.animation_time = 0
            self.show_message("Animation", "Animations enabled!")
        else:
            self.show_message("Animation", "Animations disabled!")

        logger.info(f"Animations: {'enabled' if self.animation_enabled else 'disabled'}")

    def toggle_stats(self):
        """Toggles the stats display"""
        self.stats_enabled = not self.stats_enabled

        if self.stats_enabled:
            self.show_message("Stats", "Stats enabled!")
        else:
            self.show_message("Stats", "Stats disabled!")

        logger.info(f"Stats: {'enabled' if self.stats_enabled else 'disabled'}")

    def toggle_effects(self):
        """Toggles visual effects"""
        self.effects_enabled = not self.effects_enabled

        if self.effects_enabled:
            glEnable(GL_BLEND)
            glEnable(GL_DEPTH_TEST)
            self.show_message("Effects", "Visual effects enabled!")
        else:
            glDisable(GL_BLEND)
            self.show_message("Effects", "Visual effects disabled!")

        logger.info(f"Effects: {'enabled' if self.effects_enabled else 'disabled'}")

    def toggle_atmosphere(self):
        """Toggles atmosphere simulation"""
        self.atmosphere_enabled = not self.atmosphere_enabled

        if self.atmosphere_enabled:
            self.clouds_enabled = True
            self.show_message("Atmosphere", "Atmosphere simulation enabled!")
        else:
            self.clouds_enabled = False
            self.show_message("Atmosphere", "Atmosphere simulation disabled!")

        logger.info(f"Atmosphere: {'enabled' if self.atmosphere_enabled else 'disabled'}")

    def take_screenshot(self):
        """Takes a screenshot"""
        try:
            self.screenshot_counter += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}_{self.screenshot_counter}.png"

            # Reads the OpenGL framebuffer (the screen is not a pygame Surface)
            width, height = self.display
            glPixelStorei(GL_PACK_ALIGNMENT, 1)
            pixels = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
            img = Image.frombytes("RGB", (width, height), pixels).transpose(Image.FLIP_TOP_BOTTOM)
            img.save(filename)

            self.show_message("Screenshot", f"Saved as: {filename}")
            logger.info(f"Screenshot taken: {filename}")

        except Exception as e:
            self.show_message("Error", f"Failed to take screenshot: {e}")
            logger.error(f"Screenshot error: {e}")

    def toggle_sound(self):
        """Toggles sound"""
        self.sound_enabled = not self.sound_enabled

        if self.sound_enabled:
            pygame.mixer.unpause()
            self.show_message("Sound", "Sound enabled!")
        else:
            pygame.mixer.pause()
            self.show_message("Sound", "Sound disabled!")

        logger.info(f"Sound: {'enabled' if self.sound_enabled else 'disabled'}")

    def show_settings_menu(self):
        """Shows settings"""
        self.current_section = 'Settings'
        self.update_menu_surface()
        self.show_message("Settings", "Press any key to return to the menu")

    def show_help_menu(self):
        """Shows help"""
        self.show_message("Help", "Press any key to return to the menu")

    def exit_program(self):
        """Closes the program"""
        self.save_state()
        pygame.quit()
        sys.exit(0)

    def update_animation(self):
        """Updates animations"""
        if self.animation_enabled:
            self.animation_time += 0.016

            if self.animation_type == AnimationType.ROTATION:
                self.rotation_y += self.animation_speed * 0.5
            elif self.animation_type == AnimationType.ORBIT:
                self.rotation_x = math.sin(self.animation_time) * 30
                self.rotation_y += self.animation_speed * 0.3
            elif self.animation_type == AnimationType.ZOOM:
                zoom_factor = math.sin(self.animation_time * 0.5) * 2
                self.distance = -5 + zoom_factor
            elif self.animation_type == AnimationType.FLYBY:
                self.rotation_x = math.sin(self.animation_time * 0.3) * 45
                self.rotation_y += self.animation_speed * 0.4
                zoom_factor = math.sin(self.animation_time * 0.2) * 3
                self.distance = -5 + zoom_factor

            self.ui_dirty = True

    def handle_mouse(self, event):
        """Handles mouse events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            current_time = pygame.time.get_ticks()

            if event.pos[1] < 40:
                action = self.top_menu.handle_click(event.pos)
                if action:
                    self.handle_top_menu_click(action)
                    return

            if event.button == 1:
                if current_time - self.last_click_time < self.double_click_delay:
                    self.reset_view()
                    self.auto_rotate = True
                self.last_click_time = current_time
                self.last_pos = pygame.mouse.get_pos()
                self.rotation_velocity = [0.0, 0.0]

            elif event.button in (4, 5):
                try:
                    zoom_factor = 1 if event.button == 4 else -1
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.zoom_at_cursor(mouse_x, mouse_y, zoom_factor)
                except Exception as e:
                    logger.error(f"Zoom handling error: {e}")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.last_pos is not None:
                    current_pos = pygame.mouse.get_pos()
                    dx = (current_pos[0] - self.last_pos[0]) * self.mouse_sensitivity
                    dy = (current_pos[1] - self.last_pos[1]) * self.mouse_sensitivity
                    self.rotation_velocity = [float(dy * 0.1), float(dx * 0.1)]
                self.last_pos = None

        elif event.type == pygame.MOUSEMOTION and self.last_pos is not None:
            x, y = pygame.mouse.get_pos()

            rotation_speed = self.get_zoom_factor()
            dx = (x - self.last_pos[0]) * self.mouse_sensitivity * rotation_speed
            dy = (y - self.last_pos[1]) * self.mouse_sensitivity * rotation_speed

            self.rotation_y += dx
            self.rotation_x = max(-85, min(85, self.rotation_x + dy))

            self.last_pos = (x, y)

    def zoom_at_cursor(self, x: int, y: int, zoom_factor: int):
        """Zooms the view at the cursor"""
        try:
            zoom_amount = zoom_factor * self.zoom_sensitivity
            new_distance = self.distance + zoom_amount

            if self.min_zoom <= new_distance <= self.max_zoom:
                self.distance = new_distance
                self.ui_dirty = True

        except Exception as e:
            logger.error(f"Zoom error: {e}")

    def update_rotation(self):
        """Updates rotation"""
        moving = False
        if self.last_pos is not None:
            self.auto_rotate = False
        elif self.auto_rotate:
            self.rotation_y += self.auto_rotate_speed
            moving = True

        if abs(self.rotation_velocity[0]) > 1e-3 or abs(self.rotation_velocity[1]) > 1e-3:
            self.rotation_x += float(self.rotation_velocity[0])
            self.rotation_y += float(self.rotation_velocity[1])
            self.rotation_velocity[0] *= self.rotation_momentum
            self.rotation_velocity[1] *= self.rotation_momentum
            moving = True
        else:
            self.rotation_velocity = [0.0, 0.0]

        self.rotation_x = max(-85, min(85, self.rotation_x))

        if moving:
            self.ui_dirty = True

    def get_zoom_factor(self) -> float:
        """Computes the rotation speed factor from the zoom level"""
        zoom_range = self.max_zoom - self.min_zoom
        current_zoom = self.distance - self.min_zoom
        zoom_factor = current_zoom / zoom_range
        return max(0.05, 0.2 * zoom_factor)

    def run(self):
        """Main program loop"""
        try:
            clock = pygame.time.Clock()
            logger.info("Simulation started")

            while True:
                events = pygame.event.get()
                if events:
                    self.ui_dirty = True

                for event in events:
                    if event.type == pygame.QUIT:
                        self.quit_program()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.quit_program()
                        elif event.key == pygame.K_m:
                            self.show_menu = not self.show_menu
                            self.current_section = None
                            self.update_menu_surface()
                        elif event.key == pygame.K_l:
                            self.cycle_texture()
                        elif event.key == pygame.K_r:
                            self.reset_view()
                        elif event.key == pygame.K_v:
                            self.toggle_view_mode()
                        elif event.key == pygame.K_a:
                            self.toggle_animation()
                        elif event.key == pygame.K_s:
                            self.toggle_stats()
                        elif event.key == pygame.K_e:
                            self.toggle_effects()
                        elif event.key == pygame.K_t:
                            self.take_screenshot()

                    if self.handle_menu(event):
                        continue

                    self.handle_mouse(event)

                self.update_rotation()
                self.update_animation()

                if self.stats_enabled or self.show_menu or \
                   abs(self.menu_position - (self.display[0] - self.menu_width)) > 0.5:
                    self.ui_dirty = True

                self.draw()
                clock.tick(60)

        except Exception as e:
            logger.error(f"Critical error: {e}")
            pygame.quit()
            sys.exit(1)


def check_dependencies():
    """Checks the required dependencies"""
    required_modules = ['pygame', 'OpenGL', 'numpy', 'PIL']

    for module in required_modules:
        try:
            __import__(module)
        except ImportError as e:
            print(f"Error: Missing module {module}")
            print(f"Details: {e}")
            print("Install dependencies: pip install pygame PyOpenGL numpy Pillow")
            return False

    print("All dependencies are available")
    return True


def check_texture_files():
    """Checks the texture files"""
    required_files = ['earth_texture.png', 'earth_political.png', 'earth_detailed.jpg']
    script_dir = os.path.dirname(os.path.abspath(__file__))

    missing_files = []
    for file in required_files:
        file_path = os.path.join(script_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)

    if missing_files:
        print(f"Missing texture files: {', '.join(missing_files)}")
        print("Make sure the texture files are in the program folder")
        return False

    print("All texture files are available")
    return True


def main():
    """Main program function"""
    print("Earth Simulator Enhanced v2.0")
    print("Author: Adrian Lesniak")
    print("=" * 50)

    if not check_dependencies():
        sys.exit(1)

    if not check_texture_files():
        sys.exit(1)

    try:
        simulator = EnhancedEarthSimulator()
        simulator.run()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()