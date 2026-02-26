import math
import random

import pygame

import settings
from core import collision, logging


class EnemySoldier:
    def __init__(self, x, y, nest_location, pheromone_map, speed):
        self.x = x
        self.y = y
        self.color = pygame.Color(settings.ENEMY_COLOR)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = speed
        self.vision_range = 10
        self.vision_angle = math.pi / 3
        logging.debug(f"Enemy spawned at ({self.x}, {self.y})")

    def check_ants_in_vision(self):
        try:
            entities = [
                ("ant", settings.ants),
                ("soldier", settings.soldiers),
                ("queen", settings.queen),
            ]
            for name, entity_list in entities:
                for entity in entity_list.copy():
                    dx = entity.x - self.x
                    dy = entity.y - self.y
                    distance = math.hypot(dx, dy)
                    if distance <= self.vision_range:
                        angle = math.atan2(dy, dx)
                        angle_diff = (angle - self.angle + math.pi) % (
                            2 * math.pi
                        ) - math.pi
                        if abs(angle_diff) <= self.vision_angle / 2:
                            if not self.check_line_of_sight(entity):
                                return entity
                    return None
        except AttributeError as e:
            logging.error("Error while checking ants in vision: " + str(e))
            return None

    def check_line_of_sight(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.hypot(dx, dy)
        steps = int(distance * 10)
        for i in range(1, steps):
            x = self.x + dx * i / steps
            y = self.y + dy * i / steps
            if collision.check_collision(x, y, True):
                return True
        return False

    def move(self):
        ant_in_vision = self.check_ants_in_vision()
        if ant_in_vision:
            self.move_towards(ant_in_vision)
        else:
            self.random_walk()

    def move_towards(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.hypot(dx, dy)

        if distance > self.speed:
            dx = dx / distance * self.speed
            dy = dy / distance * self.speed

        new_x = self.x + dx
        new_y = self.y + dy

        if not collision.check_collision(new_x, new_y, True):
            self.x = new_x
            self.y = new_y
            self.angle = math.atan2(dy, dx)
        else:
            self.random_walk()

    def random_walk(self):
        for _ in range(10):
            self.angle += random.uniform(-0.5, 0.5)
            new_x = self.x + math.cos(self.angle) * self.speed
            new_y = self.y + math.sin(self.angle) * self.speed

            if not collision.check_collision(new_x, new_y, True):
                self.x = new_x
                self.y = new_y
                break
        else:
            pass

    def find_ant(self):
        try:
            entities = [
                ("ant", settings.ants),
                ("soldier", settings.soldiers),
                ("queen", settings.queen),
            ]
            for name, entity_list in entities:
                for entity in entity_list.copy():
                    if math.hypot(self.x - entity.x, self.y - entity.y) < 1:
                        entity_list.remove(entity)
        except Exception as e:
            logging.error("Error while finding ants: " + str(e))
