import logging

import numpy as np
import pygame
import screeninfo

from gui import slider

with open("version.txt") as f:
    version = f.read()
FPS = 60
view_log_level = "INFO"

BG_COLOR = (118, 97, 77)
WALL_COLOR = (77, 62, 49)
ANT_COLOR = "#bf360c"
SOLDIER_COLOR = "#8c2708"
QUEEN_COLOR = "#722007"
NEST_COLOR = "#9c8065"
FOOD_COLOR = "#D2042D"
MONITOR_WIDTH = screeninfo.get_monitors()[0].width
MONITOR_HEIGHT = screeninfo.get_monitors()[0].height
MAP_WIDTH = MONITOR_WIDTH // 10
MAP_HEIGHT = MONITOR_HEIGHT // 10

logging.info("Fonts loaded.")

camera_x, camera_y = 0, 0
camera_speed = 10

nest_location = (MAP_WIDTH // 2, -3)
food_locations = set()
pheromone_map = np.zeros((MAP_WIDTH, MAP_HEIGHT))

clock = pygame.time.Clock()
running = True
paused = False
ui_visible = True
ants = []
soldiers = []
queen = []
drawing_food = False
drawing_ant = False
drawing_magnet = False
drawing_wall = False
drawing_floor = False
total_food = 0
old_total_food = 0
collected_food = 0
button_type = True
selected_tool = 1

ant_slider = slider.Slider(10, 100, 300, 1, 1000, 50)
