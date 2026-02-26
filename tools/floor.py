import settings
from core import logging, perlin


def draw(event_pos, threshold_slider, seed_button, speed_slider, start_button):
    mouse_x, mouse_y = event_pos
    grid_x = (mouse_x + settings.camera_x) // settings.GRID_SIZE
    grid_y = (mouse_y + settings.camera_y) // settings.GRID_SIZE

    try:
        if grid_y >= 0:
            perlin.perlin_settings.map_data[grid_x, grid_y] = 0
    except IndexError:
        logging.error(
            f"Invalid grid position: ({grid_x}, {grid_y}) | Camera: ({settings.camera_x}, {settings.camera_y})"
        )
