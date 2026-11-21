"""Non-blocking transient notifications."""

import time


class Notification:
    def __init__(self, duration: float = 2.5):
        self.duration = duration
        self.message = ""
        self.expires_at = 0.0

    @property
    def visible(self) -> bool:
        return bool(self.message) and time.monotonic() < self.expires_at

    def show(self, message: str) -> None:
        self.message = message
        self.expires_at = time.monotonic() + self.duration
