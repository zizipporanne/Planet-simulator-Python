"""Display-list based Earth geometry."""

from __future__ import annotations

import numpy as np
from OpenGL.GL import (
    GL_COMPILE,
    GL_TRIANGLES,
    GL_TEXTURE_2D,
    glBegin,
    glCallList,
    glDisable,
    glEnable,
    glEnd,
    glEndList,
    glGenLists,
    glNewList,
    glTexCoord2f,
    glVertex3f,
)


class GlobeRenderer:
    def __init__(self, segments: int = 32, radius: float = 2.0):
        self.segments = segments
        self.radius = radius
        self.display_list = 0

    def compile(self) -> None:
        segments = self.segments
        lat = np.pi * (-0.5 + np.arange(segments + 1) / segments)
        lon = 2 * np.pi * np.arange(segments + 1) / segments
        lat_grid, lon_grid = np.meshgrid(lat, lon, indexing="ij")
        x = np.cos(lat_grid) * np.cos(lon_grid) * self.radius
        y = np.sin(lat_grid) * self.radius
        z = np.cos(lat_grid) * np.sin(lon_grid) * self.radius

        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        glBegin(GL_TRIANGLES)
        for i in range(segments):
            for j in range(segments):
                self._vertex(x, y, z, i, j, segments)
                self._vertex(x, y, z, i + 1, j, segments)
                self._vertex(x, y, z, i + 1, j + 1, segments)
                self._vertex(x, y, z, i, j, segments)
                self._vertex(x, y, z, i + 1, j + 1, segments)
                self._vertex(x, y, z, i, j + 1, segments)
        glEnd()
        glEndList()

    @staticmethod
    def _vertex(x, y, z, i: int, j: int, segments: int) -> None:
        glTexCoord2f(1.0 - j / segments, i / segments)
        glVertex3f(x[i, j], y[i, j], z[i, j])

    def draw(self, texture_id: int | None) -> None:
        glEnable(GL_TEXTURE_2D)
        if texture_id:
            from OpenGL.GL import glBindTexture
            glBindTexture(GL_TEXTURE_2D, texture_id)
        glCallList(self.display_list)
        glDisable(GL_TEXTURE_2D)
