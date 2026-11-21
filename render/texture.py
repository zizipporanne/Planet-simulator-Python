"""Earth texture loading and GPU upload."""

from __future__ import annotations

import logging
from pathlib import Path

from OpenGL.GL import (
    GL_CLAMP,
    GL_MAX_TEXTURE_SIZE,
    GL_NEAREST,
    GL_RGB,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_UNSIGNED_BYTE,
    glBindTexture,
    glGenTextures,
    glGetIntegerv,
    glTexImage2D,
    glTexParameteri,
)
from PIL import Image

logger = logging.getLogger(__name__)
TEXTURE_FILES = {
    "Default": "earth_texture.png",
    "Political": "earth_political.png",
    "Detailed": "earth_detailed.jpg",
}


class TextureManager:
    def __init__(self, script_dir: Path):
        self.script_dir = Path(script_dir)
        self.textures: dict[str, int] = {}

    def load_all(self) -> dict[str, int]:
        for name, filename in TEXTURE_FILES.items():
            self.textures[name] = self.load_texture(self.script_dir / filename)
        return self.textures

    @staticmethod
    def load_texture(image_path: Path) -> int:
        if not image_path.is_file():
            raise FileNotFoundError(f"Texture file does not exist: {image_path}")
        with Image.open(image_path) as source:
            image = source.convert("RGB")
        max_size = int(glGetIntegerv(GL_MAX_TEXTURE_SIZE))
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size))
            logger.info("Resized %s to the GPU texture limit (%d px)", image_path.name, max_size)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0,
            GL_RGB, GL_UNSIGNED_BYTE, image.tobytes("raw", "RGB", 0, -1),
        )
        return texture_id
