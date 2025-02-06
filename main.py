import logging
import math
import os
import platform
import random

import numpy as np
import pygame
import screeninfo
from perlin_noise import PerlinNoise

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pygame.init()
logging.info("Pygame initialized.")

version = "1.1.8"

BG_COLOR = (118, 97, 77)
WALL_COLOR = (77, 62, 49)
ANT_COLOR = "#000000"
NEST_COLOR = "#9c8065"
FOOD_COLOR = "#D2042D"
FPS = 60

MONITOR_WIDTH = screeninfo.get_monitors()[0].width
MONITOR_HEIGHT = screeninfo.get_monitors()[0].height
pygame.display.set_caption("Ant Simulator")
screen = pygame.display.set_mode((MONITOR_WIDTH, MONITOR_HEIGHT), pygame.NOFRAME)

if platform.system() == "Darwin":
    screen = pygame.display.set_mode((MONITOR_WIDTH, MONITOR_HEIGHT), pygame.FULLSCREEN)
if platform.system() == "Windows":
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    os.environ["NVD_BACKEND"] = "dx11"

icon = pygame.image.load("icon.png").convert_alpha()
pygame.display.set_icon(icon)
logging.info("Window and icon initialized.")

MAP_WIDTH = screen.get_width() // 10
MAP_HEIGHT = screen.get_height() // 10


class PerlinNoiseSettings:
    def __init__(self, scale=40.0, threshold=0.1, seed=0):
        self.scale = scale
        self.threshold = threshold
        self.seed = seed
        self.noise_generator = PerlinNoise(octaves=1, seed=self.seed)
        self.map_data = self.generate_map()
        logging.info(f"Perlin noise settings initialized with seed: {self.seed}, threshold: {self.threshold}")

    def generate_map(self):
        logging.info("Generating Perlin noise map.")
        return np.array([[1 if self.noise_generator([x / self.scale, y / self.scale]) > self.threshold else 0
                          for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)])


perlin_settings = PerlinNoiseSettings()

font = pygame.font.Font(None, 36)
logging.info("Fonts loaded.")


class Slider:
    def __init__(self, x, y, width, min_value, max_value, initial_value):
        self.y = y
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.slider_rect = pygame.Rect(x + (initial_value - min_value) / (max_value - min_value) * width, y, 10, 20)
        self.dragging = False
        logging.info(f"Slider initialized at ({x}, {y}) with value {self.value}")

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(4, 4))
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        pygame.draw.rect(surface, (0, 128, 255), self.slider_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.slider_rect.collidepoint(event.pos):
            self.dragging = True
            logging.info("Slider drag started.")
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            logging.info(f"Slider value set to {self.value}")
            return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width - self.slider_rect.width))
            self.slider_rect.x = new_x
            self.value = self.min_value + (new_x - self.rect.x) / self.rect.width * (self.max_value - self.min_value)
        return False


class Button:
    def __init__(self, x, y, width, height, text):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (0, 128, 255)

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(4, 4))
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surface, (
            self.rect.centerx - text_surface.get_width() // 2,
            self.rect.centery - text_surface.get_height() // 2))

    def handle_event(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class Ant:
    def __init__(self, x, y, nest_location, pheromone_map, speed):
        self.x = x
        self.y = y
        self.nest_location = nest_location
        self.has_food = False
        self.pheromone_map = pheromone_map
        self.color = pygame.Color(ANT_COLOR)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = speed
        self.vision_range = 10
        self.vision_angle = math.pi / 3
        logging.info(f"Ant spawned at ({self.x}, {self.y})")

    def check_collision(self, x, y):
        grid_x, grid_y = int(x), int(y)
        return (grid_x < 0 or grid_x >= MAP_WIDTH or
                grid_y < 0 or grid_y >= MAP_HEIGHT or
                perlin_settings.map_data[grid_x][grid_y] == 1)

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
            if self.check_collision(x, y):
                return True
        return False

    def move(self):
        food_in_vision = self.check_food_in_vision(food_locations)
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

        if not self.check_collision(new_x, new_y):
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

            if not self.check_collision(new_x, new_y):
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
        strongest_direction = (0, 0)

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x = int(self.x + dx)
                y = int(self.y + dy)
                if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                    pheromone = self.pheromone_map[x][y]
                    if pheromone > strongest_pheromone:
                        strongest_pheromone = pheromone
                        strongest_direction = (dx, dy)

        if strongest_direction != (0, 0):
            target_angle = math.atan2(strongest_direction[1], strongest_direction[0])
            angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += angle_diff * 0.1

    def get_pheromone_strength(self, x, y):
        return self.pheromone_map[x % MAP_WIDTH][y % MAP_HEIGHT]

    def leave_pheromone(self):
        x, y = int(self.x), int(self.y)
        self.pheromone_map[x % MAP_WIDTH][y % MAP_HEIGHT] = 1

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


camera_x, camera_y = 0, 0
camera_speed = 10

threshold_slider = Slider(10, 10, 300, 0.0, 1.03, perlin_settings.threshold)
seed_slider = Slider(10, 50, 300, 0, 1035, perlin_settings.seed)
ant_slider = Slider(10, 90, 300, 1, 1035, 10)
speed_slider = Slider(10, 130, 300, 0.0, 5.17, 0.5)
start_button = Button(10, 170, 300, 50, "Start")

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

sun_image = pygame.image.load("sun.png").convert_alpha()
sun_image = pygame.transform.scale(sun_image, (300, 300))


def draw_vision_cone(surface, ant):
    start_angle = ant.angle - ant.vision_angle / 2
    end_angle = ant.angle + ant.vision_angle / 2
    points = [
        (ant.x * 10, ant.y * 10),
        (ant.x * 10 + math.cos(start_angle) * ant.vision_range * 10,
         ant.y * 10 + math.sin(start_angle) * ant.vision_range * 10),
        (ant.x * 10 + math.cos(end_angle) * ant.vision_range * 10,
         ant.y * 10 + math.sin(end_angle) * ant.vision_range * 10),
    ]
    cone_surface = pygame.Surface((MONITOR_WIDTH, MONITOR_HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(cone_surface, (255, 255, 255, 128), points)
    surface.blit(cone_surface, (0, 0))


logging.info("Game loop started.")
while running:
    screen.fill("#87CEEB")
    pygame.draw.rect(screen, BG_COLOR, (0 - camera_x, 0 - camera_y, MONITOR_WIDTH, MONITOR_HEIGHT))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            logging.info("Quit event received.")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                logging.info("Escape key pressed, exiting.")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                drawing_food = True
                x, y = event.pos
                grid_x = (x + camera_x) // 10
                grid_y = (y + camera_y) // 10
                try:
                    if not perlin_settings.map_data[grid_x][grid_y] and grid_y >= 0:
                        food_locations.add((grid_x, grid_y))
                        total_food += 1
                except:
                    print("Invalid grid position")
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing_food = False
        elif event.type == pygame.MOUSEMOTION:
            if drawing_food:
                x, y = event.pos
                grid_x = (x + camera_x) // 10
                grid_y = (y + camera_y) // 10
                try:
                    if not perlin_settings.map_data[grid_x][grid_y] and grid_y >= 0:
                        food_locations.add((grid_x, grid_y))
                        total_food += 1
                except:
                    print("Invalid grid position")
        elif event.type == pygame.MOUSEWHEEL:
            new_camera_y = camera_y - (event.y * 20)

            if new_camera_y > 0:
                camera_y = 0
            elif new_camera_y < -960:
                camera_y = -960
            else:
                camera_y = new_camera_y

        if ui_visible:
            if threshold_slider.handle_event(event) or seed_slider.handle_event(event):
                if perlin_settings.threshold != threshold_slider.value or perlin_settings.seed != int(
                        seed_slider.value):
                    perlin_settings.threshold = threshold_slider.value
                    perlin_settings.seed = int(seed_slider.value)
                    perlin_settings.noise_generator = PerlinNoise(octaves=1, seed=perlin_settings.seed)
                    perlin_settings.map_data = perlin_settings.generate_map()

            ant_slider.handle_event(event)
            speed_slider.handle_event(event)

            if start_button.handle_event(event) and button_type:
                ui_visible = False
                ants = [Ant(nest_location[0], nest_location[1], nest_location, pheromone_map, speed_slider.value)
                        for _ in range(int(ant_slider.value))]
                total_food = len(food_locations)
                collected_food = 0

    if not ui_visible:
        for ant in ants:
            if ant.has_food:
                if ant.return_to_nest():
                    collected_food += 1
            else:
                ant.move()
                if ant.find_food(food_locations):
                    ant.leave_pheromone()
        pheromone_map *= 0.99

    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if perlin_settings.map_data[x, y] == 1:
                pygame.draw.rect(screen, WALL_COLOR, ((x * 10) - camera_x, (y * 10) - camera_y, 10, 10))

    pygame.draw.rect(screen, pygame.Color(NEST_COLOR),
                     ((nest_location[0] * 10) - camera_x, (nest_location[1] * 10) - camera_y, 10, 10))

    for food in food_locations:
        pygame.draw.rect(screen, pygame.Color(FOOD_COLOR),
                         ((food[0] * 10) - camera_x, (food[1] * 10) - camera_y, 10, 10))

    for ant in ants:
        ant_color = pygame.Color(FOOD_COLOR) if ant.has_food else pygame.Color(ANT_COLOR)
        pygame.draw.circle(screen, ant_color,
                           (int(ant.x * 10) - camera_x, int(ant.y * 10) - camera_y), 3)

    pheromone_surface = pygame.Surface((MAP_WIDTH * 10, MAP_HEIGHT * 10), pygame.SRCALPHA)
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            intensity = int(pheromone_map[x, y] * 255)
            if intensity > 0:
                pygame.draw.rect(pheromone_surface, (255, 255, 0, intensity),
                                 ((x * 10), (y * 10), 10, 10))

    screen.blit(pheromone_surface, (-camera_x, -camera_y))


    def render_text_with_border(text, color, border_color=(0, 0, 0), border_size=2):
        text_surface = font.render(text, True, color)
        border_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            border_surface.blit(font.render(text, True, border_color), (dx * border_size, dy * border_size))
        border_surface.blit(text_surface, (0, 0))
        return border_surface


    screen.blit(sun_image, ((MONITOR_WIDTH - 400) - camera_x, -900 - camera_y))
    pygame.draw.rect(screen, "#4F7942", (0 - camera_x, -50 - camera_y, MONITOR_WIDTH, 50))

    if ui_visible:
        threshold_slider.draw(screen)
        seed_slider.draw(screen)
        ant_slider.draw(screen)
        start_button.draw(screen)
        speed_slider.draw(screen)

        text_threshold = render_text_with_border(f"Threshold: {perlin_settings.threshold:.2f}", (255, 255, 255))
        text_seed = render_text_with_border(f"Seed: {perlin_settings.seed}", (255, 255, 255))
        text_ants = render_text_with_border(f"Ants: {int(ant_slider.value)}", (255, 255, 255))
        text_speed = render_text_with_border(f"Speed: {speed_slider.value:.2f}", (255, 255, 255))

        screen.blit(text_threshold, (320, 10))
        screen.blit(text_seed, (320, 50))
        screen.blit(text_ants, (320, 90))
        screen.blit(text_speed, (320, 130))
    else:
        text_food = render_text_with_border(f"Food Collected: {collected_food}/{total_food}", (255, 255, 255))
        screen.blit(text_food, (10, 10))
        if food_locations is None or len(
                food_locations) == 0 or collected_food == total_food and old_total_food < total_food:
            total_food = collected_food
            old_total_food = total_food

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
logging.info("Game closed.")
