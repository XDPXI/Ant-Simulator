import numpy as np
import pygame
import screeninfo

from gui import slider

# General
FPS = 60
view_log_level = "INFO"

# Colors
BG_COLOR = (118, 97, 77)
WALL_COLOR = (77, 62, 49)
ANT_COLOR = "#bf360c"
ENEMY_COLOR = "#000000"
SOLDIER_COLOR = "#8c2708"
QUEEN_COLOR = "#722007"
NEST_COLOR = "#9c8065"
FOOD_COLOR = "#D2042D"

# Screen
MONITOR_WIDTH = screeninfo.get_monitors()[0].width
MONITOR_HEIGHT = screeninfo.get_monitors()[0].height
MAP_WIDTH = MONITOR_WIDTH // 10
MAP_HEIGHT = MONITOR_HEIGHT // 10
GRID_SIZE = 10

# Camera
camera_x, camera_y = 0, 0
camera_speed = 10

# Locations
nest_location = (MAP_WIDTH // 2, -3)
food_locations = set()

# Entities
ants = []
soldiers = []
queen = []
enemies = []
enemies_found = False
pheromone_map = np.zeros((MAP_WIDTH, MAP_HEIGHT))

# UI
ant_slider = slider.Slider(10, 100, 300, 1, 1000, 50)

# Game Loop
clock = pygame.time.Clock()
running = True
paused = False
ui_visible = True

# Tools
drawing_food = False
drawing_ant = False
drawing_magnet = False
drawing_wall = False
drawing_floor = False
drawing_enemy = False
drawing_soldier = False
selected_tool = 1

# Food
total_food = 0
old_total_food = 0
collected_food = 0

# Version
with open("version.txt") as f:
    version = f.read()
