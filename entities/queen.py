import math
import random

import pygame

import settings
from core import logging, collision, map


class Queen:
    def __init__(self, x, y, nest_location, pheromone_map, speed):
        self.x = x
        self.y = y
        self.nest_location = nest_location
        self.has_food = False
        self.pheromone_map = pheromone_map
        self.color = pygame.Color(settings.ANT_COLOR)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = speed
        self.vision_range = 15
        self.vision_angle = math.pi / 3
        logging.debug(f"Soldier spawned at ({self.x}, {self.y})")

    def move(self):
        self.random_walk()
        self.stay_within_range()

        try:
            if self.y >= 0:
                map.data[round(self.x), round(self.y)] = 0
        except IndexError:
            logging.error(
                f"Invalid grid position: ({self.x}, {self.y}) | Camera: ({settings.camera_x}, {settings.camera_y}) | Entity: Queen"
            )

    def stay_within_range(self):
        nest_x, nest_y = settings.nest_location[0], settings.nest_location[1]
        if settings.enemies_found:
            radius = 10
        else:
            radius = 30

        dx = self.x - nest_x
        dy = self.y - nest_y
        distance = math.hypot(dx, dy)

        if distance > radius:
            scale = radius / distance
            self.x = nest_x + dx * scale
            self.y = nest_y + dy * scale

        if collision.check_collision(self.x, self.y):
            self.x = nest_x + dx * (radius - 1) / distance
            self.y = nest_y + dy * (radius - 1) / distance

    def random_walk(self):
        for _ in range(10):
            self.angle += random.uniform(-0.5, 0.5)
            new_x = self.x + math.cos(self.angle) * self.speed
            new_y = self.y + math.sin(self.angle) * self.speed

            if not collision.check_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y
                break
        else:
            pass
