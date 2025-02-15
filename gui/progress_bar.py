from typing import Tuple

import pygame

from core import logging

PROGRESSBAR_HEIGHT = 20
BORDER_WIDTH = 2
COLORS = {
    "border": (0, 0, 0),
    "background": (200, 200, 200),
    "fill": (0, 128, 255),
    "text": (0, 0, 0),
}


class ProgressBar:
    def __init__(
            self,
            x: int,
            y: int,
            width: int,
            min_value: float,
            max_value: float,
            initial_value: float,
            label: str = "",
    ):
        self.rect = pygame.Rect(x, y, width, PROGRESSBAR_HEIGHT)
        self.min_value = min_value
        self.max_value = max_value
        self.value = self._clamp_value(initial_value)
        self.label = label
        self.font = pygame.font.Font(None, 24)

        logging.info(
            f"ProgressBar '{label}' initialized at ({x}, {y}) with value {self.value}"
        )

    def _clamp_value(self, value: float) -> float:
        return max(self.min_value, min(self.max_value, value))

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(
            surface,
            COLORS["border"],
            self.rect.inflate(BORDER_WIDTH * 2, BORDER_WIDTH * 2),
        )
        pygame.draw.rect(surface, COLORS["background"], self.rect)

        value_range = self.max_value - self.min_value
        fill_width = (
            (self.rect.width * (self.value - self.min_value)) / value_range
            if value_range > 0
            else self.rect.width
        )

        pygame.draw.rect(
            surface,
            COLORS["fill"],
            pygame.Rect(self.rect.x, self.rect.y, fill_width, PROGRESSBAR_HEIGHT),
        )

    def set_value(self, value: float):
        old_value = self.value
        self.value = self._clamp_value(value)
        if old_value != self.value:
            logging.debug(
                f"ProgressBar '{self.label}' value updated to {self.value:.2f}"
            )

    def get_value(self) -> float:
        return self.value

    def get_dimensions(self) -> Tuple[int, int, int, int]:
        return self.rect.x, self.rect.y, self.rect.width, self.rect.height
