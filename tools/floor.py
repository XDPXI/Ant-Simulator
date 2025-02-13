import settings
from core import perlin, logging

def draw(eventPos, threshold_slider, seed_button, speed_slider, start_button):
    x, y = eventPos
    grid_x = (x + settings.camera_x) // 10
    grid_y = (y + settings.camera_y) // 10

    if not (threshold_slider.is_hovered or seed_button.is_hovered or speed_slider.is_hovered or settings.ant_slider.is_hovered or start_button.is_hovered):
        try:
            if grid_y >= 0:
                perlin.perlin_settings.map_data[grid_x, grid_y] = 0
        except IndexError:
            logging.error(f"Invalid grid position: ({grid_x}, {grid_y})")
    else:
        settings.drawing_floor = False