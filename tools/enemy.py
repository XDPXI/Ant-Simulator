import settings
from core import logging, map, perlin
from entities import enemy_soldier


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
            settings.enemies.append(
                enemy_soldier.EnemySoldier(
                    grid_x,
                    grid_y,
                    (settings.MONITOR_WIDTH // 2, settings.MONITOR_HEIGHT // 2),
                    settings.pheromone_map,
                    speed_slider.value,
                )
            )
    except IndexError:
        logging.error(
            f"Invalid grid position: ({grid_x}, {grid_y}) | Camera: ({settings.camera_x}, {settings.camera_y})"
        )
