"""OpenGL camera setup and transform."""

from __future__ import annotations

from OpenGL.GL import GL_MODELVIEW, GL_PROJECTION, glLoadIdentity, glMatrixMode
from OpenGL.GL import glRotatef, glTranslatef
from OpenGL.GLU import gluPerspective


class Camera:
    def __init__(self, display: tuple[int, int]):
        self.display = display
        self.fov = 45.0
        self.near = 0.1
        self.far = 50.0

    def setup_projection(self) -> None:
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.display[0] / self.display[1], self.near, self.far)
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def apply(state) -> None:
        glLoadIdentity()
        glTranslatef(0.0, 0.0, state.distance)
        glRotatef(state.rotation_x, 1, 0, 0)
        glRotatef(state.rotation_y, 0, 1, 0)
