import math
import random

import pygame

import settings
from core import collision, logging, map


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
        self.vision_range = 30
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
                f"Invalid grid position: ({self.x}, {self.y}) | Camera: ({settings.camera_x}, {settings.camera_y}) | Entity: Soldier"
            )

    def stay_within_range(self):
        for queen in settings.queen:
            try:
                queen_x, queen_y = queen.x, queen.y
                radius = 10

                dx = self.x - queen_x
                dy = self.y - queen_y
                distance = math.hypot(dx, dy)

                if distance > radius:
                    scale = radius / distance
                    self.x = queen_x + dx * scale
                    self.y = queen_y + dy * scale

                if collision.check_collision(self.x, self.y):
                    self.x = queen_x + dx * (radius - 1) / distance
                    self.y = queen_y + dy * (radius - 1) / distance
            except Exception as e:
                logging.error(f"Error while staying within range: {e}")

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

    def find_ant(self):
        try:
            entities = [("enemy", settings.enemies)]
            for name, entity_list in entities:
                for entity in entity_list.copy():
                    if math.hypot(self.x - entity.x, self.y - entity.y) < 1:
                        entity_list.remove(entity)
        except Exception as e:
            logging.error("Error while finding enemies: " + str(e))
