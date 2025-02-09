import math
import random

import pygame

import settings
from core import logging, perlin


def check_collision(x, y):
    grid_x, grid_y = int(x), int(y)
    collision = (grid_x < 0 or grid_x >= settings.MAP_WIDTH or
                 grid_y < -4.5 or grid_y >= settings.MAP_HEIGHT or
                 (grid_y >= 0 and perlin.perlin_settings.map_data[grid_x][grid_y] == 1))
    logging.debug(f"Collision at ({grid_x}, {grid_y}): {collision}")
    return collision


class Soldier:
    def __init__(self, x, y, nest_location, pheromone_map, speed):
        self.x = x
        self.y = y
        self.nest_location = nest_location
        self.has_food = False
        self.pheromone_map = pheromone_map
        self.color = pygame.Color(settings.ANT_COLOR)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = speed
        self.vision_range = 10
        self.vision_angle = math.pi / 3
        logging.debug(f"Soldier spawned at ({self.x}, {self.y})")

    def move(self):
        self.random_walk()
        self.stay_within_range()

    def stay_within_range(self):
        for queen in settings.queen:
            queen_x, queen_y = queen.x, queen.y
            radius = 10

            dx = self.x - queen_x
            dy = self.y - queen_y
            distance = math.hypot(dx, dy)

            if distance > radius:
                scale = radius / distance
                self.x = queen_x + dx * scale
                self.y = queen_y + dy * scale

            if check_collision(self.x, self.y):
                self.x = queen_x + dx * (radius - 1) / distance
                self.y = queen_y + dy * (radius - 1) / distance

    def random_walk(self):
        for _ in range(10):
            self.angle += random.uniform(-0.5, 0.5)
            new_x = self.x + math.cos(self.angle) * self.speed
            new_y = self.y + math.sin(self.angle) * self.speed

            if not check_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y
                break
        else:
            pass
