from typing import Tuple, Callable, Optional

import pygame

import settings

DEFAULT_FONT_SIZE = 40
BORDER_WIDTH = 2
HOVER_DARKEN_FACTOR = 0.8


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font_size: int = DEFAULT_FONT_SIZE,
        color: Tuple[int, int, int] = (0, 128, 255),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        on_click: Optional[Callable[[], None]] = None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.on_click = on_click
        self.is_hovered = False

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(
            surface, (0, 0, 0), self.rect.inflate(BORDER_WIDTH * 2, BORDER_WIDTH * 2)
        )
        pygame.draw.rect(surface, self._get_current_color(), self.rect)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.on_click:
                settings.drawing_food = False
                self.on_click()
                return True
        return False

    def _get_current_color(self) -> Tuple[int, int, int]:
        return (
            tuple(int(c * HOVER_DARKEN_FACTOR) for c in self.color)
            if self.is_hovered
            else self.color
        )

    def set_text(self, text: str):
        self.text = text

    def set_color(self, color: Tuple[int, int, int]):
        self.color = color

    def set_on_click(self, on_click: Optional[Callable[[], None]]):
        self.on_click = on_click

    def get_dimensions(self) -> Tuple[int, int, int, int]:
        return self.rect.x, self.rect.y, self.rect.width, self.rect.height
