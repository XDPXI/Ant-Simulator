import logging

import numpy as np
import pygame
import screeninfo

version = "1.2.0"
FPS = 60

BG_COLOR = (118, 97, 77)
WALL_COLOR = (77, 62, 49)
ANT_COLOR = "#000000"
NEST_COLOR = "#9c8065"
FOOD_COLOR = "#D2042D"
0
MONITOR_WIDTH = screeninfo.get_monitors()[0].width
MONITOR_HEIGHT = screeninfo.get_monitors()[0].height
MAP_WIDTH = MONITOR_WIDTH // 10
MAP_HEIGHT = MONITOR_HEIGHT // 10

logging.info("Fonts loaded.")

camera_x, camera_y = 0, 0
camera_speed = 10

nest_location = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
food_locations = set()
pheromone_map = np.zeros((MAP_WIDTH, MAP_HEIGHT))

clock = pygame.time.Clock()
running = True
ui_visible = True
ants = []
drawing_food = False
total_food = 0
old_total_food = 0
collected_food = 0
button_type = True
