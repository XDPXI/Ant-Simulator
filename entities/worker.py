import math
import random

import pygame

import settings
from core import logging, collision, map


class Ant:
    def __init__(self, x, y, nest_location, pheromone_map, speed, assignment):
        self.x = x
        self.y = y
        self.assignment = assignment
        self.nest_location = nest_location
        self.has_food = False
        self.pheromone_map = pheromone_map
        self.color = pygame.Color(settings.ANT_COLOR)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = speed
        self.vision_range = 10
        self.vision_angle = math.pi / 3
        logging.debug(f"Ant spawned at ({self.x}, {self.y})")

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
            if collision.check_collision(x, y, None, self.assignment):
                return True
        return False

    def move(self):
        food_in_vision = self.check_food_in_vision(settings.food_locations)
        if food_in_vision:
            self.move_towards(food_in_vision)
        else:
            self.random_walk()

        self.x = max(0, min(self.x, settings.MAP_WIDTH - 1))
        self.y = max(0, min(self.y, settings.MAP_HEIGHT - 1))
        x, y = round(self.x), round(self.y)
        try:
            if 0 <= x < settings.MAP_WIDTH and 0 <= y < settings.MAP_HEIGHT:
                if self.assignment == 1:
                    map.data[x, y] = 0
                elif self.assignment == 2:
                    for dx in range(-1, 1):
                        for dy in range(-1, 1):
                            nx, ny = x + dx, y + dy
                            if (
                                0 <= nx < settings.MAP_WIDTH
                                and 0 <= ny < settings.MAP_HEIGHT
                            ):
                                map.data[nx, ny] = 0
            else:
                logging.warn(
                    f"Ant position out of bounds: ({x}, {y}) | Camera: ({settings.camera_x}, {settings.camera_y}) | Entity: Worker | Assignment: {self.assignment}"
                )
        except IndexError:
            logging.error(
                f"Invalid grid position: ({x}, {y}) | Camera: ({settings.camera_x}, {settings.camera_y}) | Entity: Worker | Assignment: {self.assignment}"
            )

    def move_towards(self, target):
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = math.hypot(dx, dy)

        if distance > self.speed:
            dx = dx / distance * self.speed
            dy = dy / distance * self.speed

        new_x = self.x + dx
        new_y = self.y + dy

        if not collision.check_collision(new_x, new_y, None, self.assignment):
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

            if not collision.check_collision(new_x, new_y, None, self.assignment):
                self.x = new_x
                self.y = new_y
                break
        else:
            pass

        pheromone_strength = self.get_pheromone_strength(int(self.x), int(self.y))
        if pheromone_strength > 0:
            self.follow_pheromone()

    def follow_pheromone(self):
        strongest_pheromone = 0
        strongest_direction = None

        for dx, dy in [
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, -1),
            (-1, 0),
            (-1, 1),
        ]:
            x = int(self.x + dx)
            y = int(self.y + dy)
            if 0 <= x < settings.MAP_WIDTH and 0 <= y < settings.MAP_HEIGHT:
                pheromone = self.pheromone_map[x][y]
                if pheromone > strongest_pheromone:
                    strongest_pheromone = pheromone
                    strongest_direction = (dx, dy)

        if strongest_direction:
            target_angle = math.atan2(strongest_direction[1], strongest_direction[0])
            self.angle = self.angle + (target_angle - self.angle) * 0.1

    def get_pheromone_strength(self, x, y):
        return self.pheromone_map[x % settings.MAP_WIDTH][y % settings.MAP_HEIGHT]

    def leave_pheromone(self):
        x, y = int(self.x), int(self.y)
        self.pheromone_map[x % settings.MAP_WIDTH][y % settings.MAP_HEIGHT] = 1

    def find_food(self, food_locations):
        for food in food_locations:
            if math.hypot(self.x - food[0], self.y - food[1]) < 1:
                food_locations.remove(food)
                self.has_food = True
                return True
        return False

    def return_to_nest(self):
        dx = self.nest_location[0] - self.x
        dy = self.nest_location[1] - self.y
        distance = math.hypot(dx, dy)

        if distance < 1:
            if self.has_food:
                self.has_food = False
                return True
        else:
            self.move_towards(self.nest_location)
            self.leave_pheromone()
        return False
