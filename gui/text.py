import pygame


def none(text, color, font=pygame.font.Font(None, 36)):
    text_surface = font.render(text, True, color)
    return text_surface


def border(
        text, color, border_color=(0, 0, 0), border_size=2, font=pygame.font.Font(None, 36)
):
    text_surface = font.render(text, True, color)
    border_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        border_surface.blit(
            font.render(text, True, border_color), (dx * border_size, dy * border_size)
        )
    border_surface.blit(text_surface, (0, 0))
    return border_surface
