import random

import settings
from core import logging, map, perlin
from entities import worker


def draw(event_pos, threshold_slider, seed_button, speed_slider, start_button):
    if settings.ui_visible:
        return

    mouse_x, mouse_y = event_pos
    grid_x = (mouse_x + settings.camera_x) // settings.GRID_SIZE
    grid_y = (mouse_y + settings.camera_y) // settings.GRID_SIZE

    try:
        if (
            not perlin.perlin_settings.map_data[grid_x][grid_y]
            and grid_y >= 1
            and not map.data[grid_x][grid_y]
        ):
            settings.ant_slider.value += 1
            settings.ants.append(
                worker.Ant(
                    grid_x,
                    grid_y,
                    settings.nest_location,
                    settings.pheromone_map,
                    speed_slider.value,
                    random.choices([0, 1, 2], weights=[4, 2, 1])[0],
                )
            )
    except IndexError:
        logging.error(
            f"Invalid grid position: ({grid_x}, {grid_y}) | Camera: ({settings.camera_x}, {settings.camera_y})"
        )
