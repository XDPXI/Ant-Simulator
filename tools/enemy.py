import settings
from entities import enemy_soldier
from core import perlin


def draw(eventPos, threshold_slider, seed_button, speed_slider, start_button):
    if not settings.ui_visible:
        x, y = eventPos
        grid_x = (x + settings.camera_x) // 10
        grid_y = (y + settings.camera_y) // 10
        if not threshold_slider.is_hovered or not seed_button.is_hovered or not speed_slider.is_hovered or not settings.ant_slider.is_hovered or not start_button.is_hovered:
            try:
                if not perlin.perlin_settings.map_data[grid_x][grid_y] and grid_y >= -4:
                    settings.enemies.append(enemy_soldier.EnemySoldier(grid_x, grid_y, (settings.MONITOR_WIDTH // 2, settings.MONITOR_HEIGHT // 2),
                                        settings.pheromone_map, speed_slider.value))
            except IndexError:
                print("Invalid grid position")
        else:
            settings.drawing_enemy = False
