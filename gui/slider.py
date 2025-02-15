from typing import Tuple

import pygame

import settings
from core import logging

SLIDER_HEIGHT = 20
HANDLE_WIDTH = 10
BORDER_WIDTH = 2
COLORS = {
    "border": (0, 0, 0),
    "background": (200, 200, 200),
    "handle": (0, 128, 255),
    "text": (0, 0, 0),
}


class Slider:
    def __init__(
            self,
            x: int,
            y: int,
            width: int,
            min_value: float,
            max_value: float,
            initial_value: float,
    ):
        self.rect = pygame.Rect(x, y, width, SLIDER_HEIGHT)
        self.min_value = min_value
        self.max_value = max_value
        self.value = self._clamp_value(initial_value)

        self.handle_rect = self._calculate_handle_rect()
        self.dragging = False
        self.is_hovered = False

        logging.info(f"Slider initialized at ({x}, {y}) with value {self.value:.2f}")

    def _clamp_value(self, value: float) -> float:
        return max(self.min_value, min(self.max_value, value))

    def _calculate_handle_rect(self) -> pygame.Rect:
        handle_x = (
                self.rect.x
                + (self.value - self.min_value)
                / (self.max_value - self.min_value)
                * self.rect.width
        )
        return pygame.Rect(
            handle_x - HANDLE_WIDTH // 2, self.rect.y, HANDLE_WIDTH, SLIDER_HEIGHT
        )

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(
            surface,
            COLORS["border"],
            self.rect.inflate(BORDER_WIDTH * 2, BORDER_WIDTH * 2),
        )
        pygame.draw.rect(surface, COLORS["background"], self.rect)
        pygame.draw.rect(surface, COLORS["handle"], self.handle_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and self.handle_rect.collidepoint(
                event.pos
        ):
            self.dragging = True
            settings.drawing_food = False
            logging.info("Slider drag started.")
            return True
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            logging.info(f"Slider value set to {self.value:.2f}")
            return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self._update_value(event.pos[0])
            return True
        return False

    def _update_value(self, x: int):
        relative_x = max(0, min(x - self.rect.x, self.rect.width))
        self.value = self.min_value + (relative_x / self.rect.width) * (
                self.max_value - self.min_value
        )
        self.handle_rect = self._calculate_handle_rect()

    def get_value(self) -> float:
        return self.value

    def set_value(self, value: float):
        self.value = self._clamp_value(value)
        self.handle_rect = self._calculate_handle_rect()

    def get_dimensions(self) -> Tuple[int, int, int, int]:
        return self.rect.x, self.rect.y, self.rect.width, self.rect.height
