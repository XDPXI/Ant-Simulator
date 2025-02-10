import settings
from core import perlin

def draw(eventPos, threshold_slider, seed_button, speed_slider, ant_slider, start_button):
    x, y = eventPos
    grid_x = (x + settings.camera_x) // 10
    grid_y = (y + settings.camera_y) // 10
    if not threshold_slider.is_hovered or not seed_button.is_hovered or not speed_slider.is_hovered or not ant_slider.is_hovered or not start_button.is_hovered:
        try:
            if not perlin.perlin_settings.map_data[grid_x][grid_y] and grid_y >= 0:
                settings.food_locations.add((grid_x, grid_y))
                settings.total_food += 1
        except IndexError:
            print("Invalid grid position")
    else:
        settings.drawing_food = False