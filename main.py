import math
import os
import platform
import random

import pygame
import screeninfo
from colorama import init
from noise import snoise2

from core import perlin, settings, update_checker, logging
from gui import slider, button

init(autoreset=True)

update_checker.check_updates()

pygame.init()

logging.info("Pygame initialized.")
font = pygame.font.Font(None, 36)

pygame.display.set_caption("Ant Simulator")
screen = pygame.display.set_mode((settings.MONITOR_WIDTH, settings.MONITOR_HEIGHT), pygame.NOFRAME)

if platform.system() == "Darwin":
    screen = pygame.display.set_mode((settings.MONITOR_WIDTH, settings.MONITOR_HEIGHT), pygame.FULLSCREEN)
    settings.FULLSCREEN = True
if platform.system() == "Windows":
    if settings.MONITOR_WIDTH < 1920 and settings.MONITOR_HEIGHT < 1080:
        screen = pygame.display.set_mode((settings.MONITOR_WIDTH, settings.MONITOR_HEIGHT), pygame.NOFRAME)
        settings.FULLSCREEN = True
    else:
        screen = pygame.display.set_mode((settings.MONITOR_WIDTH, settings.MONITOR_HEIGHT), pygame.RESIZABLE)
        settings.FULLSCREEN = False
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    os.environ["NVD_BACKEND"] = "dx11"

perlin_settings = perlin.PerlinNoiseSettings()
threshold_slider = slider.Slider(10, 10, 300, 0.0, 1.0, perlin_settings.threshold)
seed_slider = slider.Slider(10, 50, 300, 0, 1000, perlin_settings.seed)
ant_slider = slider.Slider(10, 90, 300, 1, 1000, 10)
speed_slider = slider.Slider(10, 130, 300, 0.0, 10.0, 0.5)
start_button = button.Button(10, 170, 300, 50, "Start")

icon = pygame.image.load("assets/icon.png").convert_alpha()
pygame.display.set_icon(icon)
logging.info("Window and icon initialized.")

sun_image = pygame.image.load("assets/sun.png").convert_alpha()
sun_image = pygame.transform.scale(sun_image, (300, 300))

ant_nest = pygame.image.load("assets/nest.png").convert_alpha()
ant_nest = pygame.transform.scale(ant_nest, (153, 69))


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
        logging.debug(f"Ant spawned at ({self.x}, {self.y})")

    def check_collision(self, x, y):
        grid_x, grid_y = int(x), int(y)
        collision = (grid_x < 0 or grid_x >= settings.MAP_WIDTH or
                     grid_y < -4.5 or grid_y >= settings.MAP_HEIGHT or
                     (grid_y >= 0 and perlin_settings.map_data[grid_x][grid_y] == 1))
        logging.debug(f"Collision at ({grid_x}, {grid_y}): {collision}")
        return collision

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
                if 0 <= x < settings.MAP_WIDTH and 0 <= y < settings.MAP_HEIGHT:
                    pheromone = self.pheromone_map[x][y]
                    if pheromone > strongest_pheromone:
                        strongest_pheromone = pheromone
                        strongest_direction = (dx, dy)

        if strongest_direction != (0, 0):
            target_angle = math.atan2(strongest_direction[1], strongest_direction[0])
            angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += angle_diff * 0.1

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

logging.info("Game loop started.")
while settings.running:
    screen.fill("#87CEEB")
    pygame.draw.rect(screen, settings.BG_COLOR,
                     (0 - settings.camera_x, 0 - settings.camera_y, settings.MONITOR_WIDTH, settings.MONITOR_HEIGHT))

    settings.MONITOR_WIDTH = screeninfo.get_monitors()[0].width
    settings.MONITOR_HEIGHT = screeninfo.get_monitors()[0].height

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            settings.running = False
            logging.info("Quit event received.")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                settings.running = False
                logging.info("Escape key pressed, exiting.")
            elif event.key == pygame.K_f:
                if settings.MONITOR_WIDTH > 1920 and settings.MONITOR_HEIGHT > 1080 and not settings.FULLSCREEN:
                    screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
                    center_x = (settings.MONITOR_WIDTH - 1920) // 2
                    center_y = (settings.MONITOR_HEIGHT - 1080) // 2
                    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{center_x},{center_y}"
                else:
                    if platform.system() == "Darwin":
                        screen = pygame.display.set_mode((settings.MONITOR_WIDTH, settings.MONITOR_HEIGHT), pygame.FULLSCREEN)
                    if platform.system() == "Windows":
                        screen = pygame.display.set_mode((settings.MONITOR_WIDTH, settings.MONITOR_HEIGHT), pygame.NOFRAME)
                        settings.FULLSCREEN = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                settings.drawing_food = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                settings.drawing_food = False
        elif event.type == pygame.MOUSEMOTION:
            if settings.drawing_food:
                x, y = event.pos
                grid_x = (x + settings.camera_x) // 10
                grid_y = (y + settings.camera_y) // 10
                if not threshold_slider.is_hovered or not seed_slider.is_hovered or not speed_slider.is_hovered or not ant_slider.is_hovered or not start_button.is_hovered:
                    try:
                        if not perlin_settings.map_data[grid_x][grid_y] and grid_y >= 0:
                            settings.food_locations.add((grid_x, grid_y))
                            settings.total_food += 1
                    except:
                        print("Invalid grid position")
                else:
                    settings.drawing_food = False
        elif event.type == pygame.MOUSEWHEEL:
            new_camera_y = settings.camera_y - (event.y * 20)

            if new_camera_y > 0:
                settings.camera_y = 0
            elif new_camera_y < -960:
                settings.camera_y = -960
            else:
                settings.camera_y = new_camera_y

        if settings.ui_visible:
            if threshold_slider.handle_event(event) or seed_slider.handle_event(event):
                if perlin_settings.threshold != threshold_slider.value or perlin_settings.seed != int(
                        seed_slider.value):
                    perlin_settings.threshold = threshold_slider.value
                    perlin_settings.seed = int(seed_slider.value)
                    perlin_settings.noise_generator = lambda x, y: snoise2(x / perlin_settings.scale,
                                                                           y / perlin_settings.scale, octaves=1,
                                                                           base=perlin_settings.seed)
                    perlin_settings.map_data = perlin_settings.generate_map()

            ant_slider.handle_event(event)
            speed_slider.handle_event(event)

            if start_button.handle_event(event) and settings.button_type:
                settings.ui_visible = False
                settings.ants = [Ant(settings.nest_location[0], settings.nest_location[1], settings.nest_location,
                                     settings.pheromone_map, speed_slider.value)
                        for _ in range(int(ant_slider.value))]
                settings.total_food = len(settings.food_locations)
                settings.collected_food = 0

    if not settings.ui_visible:
        for Ant in settings.ants:
            if Ant.has_food:
                if Ant.return_to_nest():
                    settings.collected_food += 1
            else:
                Ant.move()
                if Ant.find_food(settings.food_locations):
                    Ant.leave_pheromone()
        settings.pheromone_map *= 0.99

    for x in range(settings.MAP_WIDTH):
        for y in range(settings.MAP_HEIGHT):
            if perlin_settings.map_data[x, y] == 1:
                pygame.draw.rect(screen, settings.WALL_COLOR,
                                 ((x * 10) - settings.camera_x, (y * 10) - settings.camera_y, 10, 10))

    for food in settings.food_locations:
        pygame.draw.rect(screen, pygame.Color(settings.FOOD_COLOR),
                         ((food[0] * 10) - settings.camera_x, (food[1] * 10) - settings.camera_y, 10, 10))

    pheromone_surface = pygame.Surface((settings.MAP_WIDTH * 10, settings.MAP_HEIGHT * 10), pygame.SRCALPHA)
    for x in range(settings.MAP_WIDTH):
        for y in range(settings.MAP_HEIGHT):
            intensity = int(settings.pheromone_map[x, y] * 255)
            if intensity > 0:
                pygame.draw.rect(pheromone_surface, (255, 255, 0, intensity),
                                 ((x * 10), (y * 10), 10, 10))

    screen.blit(pheromone_surface, (-settings.camera_x, -settings.camera_y))


    def render_text_with_border(text, color, border_color=(0, 0, 0), border_size=2):
        text_surface = font.render(text, True, color)
        border_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            border_surface.blit(font.render(text, True, border_color), (dx * border_size, dy * border_size))
        border_surface.blit(text_surface, (0, 0))
        return border_surface


    screen.blit(sun_image, ((settings.MONITOR_WIDTH - 400) - +settings.camera_x, -900 - settings.camera_y))
    pygame.draw.rect(screen, "#4F7942", (0 - settings.camera_x, -50 - settings.camera_y, settings.MONITOR_WIDTH, 50))

    for ant in settings.ants:
        ant_color = pygame.Color(settings.FOOD_COLOR) if ant.has_food else pygame.Color(settings.ANT_COLOR)
        pygame.draw.circle(screen, ant_color,
                           (int(ant.x * 10) - settings.camera_x, int(ant.y * 10) - settings.camera_y), 3)

    screen.blit(ant_nest, (((settings.MONITOR_WIDTH // 2) - (153 // 2)) - +settings.camera_x, -63 - settings.camera_y))

    if settings.ui_visible:
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
        text_food = render_text_with_border(f"Food Collected: {settings.collected_food}/{settings.total_food}",
                                            (255, 255, 255))
        screen.blit(text_food, (10, 10))
        if settings.food_locations is None or len(
                settings.food_locations) == 0 or settings.collected_food == settings.total_food and settings.old_total_food < settings.total_food:
            settings.total_food = settings.collected_food
            old_total_food = settings.total_food

    pygame.display.flip()
    settings.clock.tick(settings.FPS)

pygame.quit()
logging.info("Game closed.")