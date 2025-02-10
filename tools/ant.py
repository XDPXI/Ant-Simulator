import settings
from entities import worker


def draw(eventPos, threshold_slider, seed_button, speed_slider, start_button):
    if not settings.ui_visible:
        x, y = eventPos
        grid_x = (x + settings.camera_x) // 10
        grid_y = (y + settings.camera_y) // 10
        if not threshold_slider.is_hovered or not seed_button.is_hovered or not speed_slider.is_hovered or not settings.ant_slider.is_hovered or not start_button.is_hovered:
            settings.ant_slider.value += 1
            settings.ants.append(worker.Ant(grid_x, grid_y, settings.nest_location,
                                settings.pheromone_map, speed_slider.value))
        else:
            settings.drawing_ant = False
