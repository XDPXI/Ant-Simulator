import settings
from core import logging, perlin, map


def check_collision(x, y, enemy=False, assignment=0):
    grid_x, grid_y = int(x), int(y)
    collision = (
        grid_x < 0
        or grid_x >= settings.MAP_WIDTH
        or grid_y < -4.5
        or grid_y >= settings.MAP_HEIGHT
        or (grid_y >= 0 and perlin.perlin_settings.map_data[grid_x][grid_y] == 1)
        or (enemy and (grid_y >= 0 and map.data[grid_x][grid_y] == 1))
        or (assignment == 0 and (grid_y >= 0 and map.data[grid_x][grid_y] == 1))
    )
    logging.debug(f"Collision at ({grid_x}, {grid_y}): {collision}")
    return collision
