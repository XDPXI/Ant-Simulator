import settings
from entities import worker

def draw(eventPos, threshold_slider, seed_button, speed_slider, start_button):
    if not settings.ui_visible:
        x, y = eventPos
        if not threshold_slider.is_hovered or not seed_button.is_hovered or not speed_slider.is_hovered or not settings.ant_slider.is_hovered or not start_button.is_hovered:
            settings.ant_slider.value += 1
            settings.ants = [worker.Ant(settings.nest_location[0], settings.nest_location[1], settings.nest_location,
                                        settings.pheromone_map, speed_slider.value)
                             for _ in range(int(settings.ant_slider.value))]
        else:
            settings.drawing_ant = False