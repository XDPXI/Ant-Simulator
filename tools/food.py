import settings
from core import perlin, logging


def draw(event_pos, threshold_slider, seed_button, speed_slider, start_button):
    mouse_x, mouse_y = event_pos
    grid_x = (mouse_x + settings.camera_x) // settings.GRID_SIZE
    grid_y = (mouse_y + settings.camera_y) // settings.GRID_SIZE

    if any(
            widget.is_hovered
            for widget in (
                    threshold_slider,
                    seed_button,
                    speed_slider,
                    settings.ant_slider,
                    start_button,
            )
    ):
        settings.drawing_food = False
        return

    try:
        if not perlin.perlin_settings.map_data[grid_x][grid_y] and grid_y >= 0:
            settings.food_locations.add((grid_x, grid_y))
            settings.total_food += 1
    except IndexError:
        logging.error(
            f"Invalid grid position: ({grid_x}, {grid_y}) | Camera: ({settings.camera_x}, {settings.camera_y})"
        )
