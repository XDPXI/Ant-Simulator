import math
import random

import pygame

import settings
from core import logging, collision


class Ant:
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
        logging.debug(f"Enemy spawned at ({self.x}, {self.y})")

    def check_food_in_vision(self, food_locations):
        for food in food_locations:
            dx = food[0] - self.x
            dy = food[1] - self.y
            distance = math.hypot(dx, dy)
            if distance <= self.vision_range:
                angle = math.atan2(dy, dx)
                angle_diff = (angle - self.angle + math.pi) % (2 * math.pi) - math.pi
                if abs(angle_diff) <= self.vision_angle / 2:
                    if not self.check_line_of_sight(food):
                        return food
        return None

    def check_line_of_sight(self, target):
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = math.hypot(dx, dy)
        steps = int(distance * 2)
        for i in range(1, steps):
            x = self.x + dx * i / steps
            y = self.y + dy * i / steps
            if collision.check_collision(x, y):
                return True
        return False

    def move(self):
        food_in_vision = self.check_food_in_vision(settings.food_locations)
        if food_in_vision:
            self.move_towards(food_in_vision)
        else:
            self.random_walk()

    def move_towards(self, target):
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = math.hypot(dx, dy)

        if distance > self.speed:
            dx = dx / distance * self.speed
            dy = dy / distance * self.speed

        new_x = self.x + dx
        new_y = self.y + dy

        if not collision.check_collision(new_x, new_y):
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

            if not collision.check_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y
                break
        else:
            pass

    def find_food(self, food_locations):
        for food in food_locations:
            if math.hypot(self.x - food[0], self.y - food[1]) < 1:
                food_locations.remove(food)
                self.has_food = True
                return True
        return False
