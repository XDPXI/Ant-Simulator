import os

file_path = 'args\\no-install-required-packages.'
if not os.path.exists(file_path):
    os.system("pip install --upgrade pip")
    os.system("pip install -r requirements.txt")

import platform
import random
import sys

import pygame
import screeninfo
import argparse

from tools import ant as ant2, food as food2, magnet, wall, floor
from entities import worker, queen, soldier
from core import perlin, update_checker, logging
import settings
from gui import slider, button, progress_bar

logging.setup("INFO")

parser = argparse.ArgumentParser(description="A 2D pixelated game where ants forage for survival in a simulated world.")
parser.add_argument("--no-install", choices=["true", "false"],
                    help="Disables the automatic installation of required packages.")
args = parser.parse_args()

no_install = args.no_install.lower() == "true" if args.no_install else False
if no_install:
    logging.info("Automatic installation is disabled.")
    logging.warn(
        "Please install the required packages manually using the provided requirements.txt file or issues will occur!")
    directory = "args"
    os.makedirs(directory, exist_ok=True)
    with open(file_path, 'w') as file:
        file.write("")
else:
    logging.info("Automatic installation is enabled.")
    if os.path.exists(file_path):
        os.remove(file_path)

update_checker.check_updates()

pygame.init()

logging.info("Pygame initialized.")
font = pygame.font.Font(None, 36)

pygame.display.set_caption("Ant Simulator")
screen = pygame.display.set_mode((settings.MONITOR_WIDTH, settings.MONITOR_HEIGHT), pygame.NOFRAME)
if platform.system() == "Darwin":
    screen = pygame.display.set_mode((settings.MONITOR_WIDTH, settings.MONITOR_HEIGHT), pygame.FULLSCREEN)
if platform.system() == "Windows":
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    os.environ["NVD_BACKEND"] = "dx11"

icon = pygame.image.load("assets/icon.png").convert_alpha()
pygame.display.set_icon(icon)
logging.info("Window and icon initialized.")

threshold_slider = slider.Slider(10, 10, 300, 0.0, 1.0, perlin.perlin_settings.threshold)
seed_button = button.Button(10, 50, 300, 30, "Generate New Map", 28)
seed_button_value = perlin.perlin_settings.seed
soldier_slider = slider.Slider(10, 140, 300, 0, 10, 10)
queen_slider = slider.Slider(10, 180, 300, 0, 1, 1)
food_progressbar = progress_bar.ProgressBar(x=10, y=100, width=300, min_value=0, max_value=100, initial_value=0,
                                            label="Food")
speed_slider = slider.Slider(10, 220, 300, 0.0, 10.0, 0.5)
start_button = button.Button(10, 260, 300, 50, "Start", 40)

sun_image = pygame.image.load("assets/sun.png").convert_alpha()
sun_image = pygame.transform.scale(sun_image, (300, 300))

ant_nest = pygame.image.load("assets/nest.png").convert_alpha()
ant_nest = pygame.transform.scale(ant_nest, (100, 50))


def regenerate_perlin_map():
    if perlin.perlin_settings.threshold != threshold_slider.value or perlin.perlin_settings.seed != int(
            seed_button_value):
        perlin.perlin_settings.threshold = threshold_slider.value
        perlin.perlin_settings.seed = int(seed_button_value)
        perlin.perlin_settings.noise_generator = perlin.PerlinNoise(octaves=1, seed=perlin.perlin_settings.seed)
        perlin.perlin_settings.map_data = perlin.perlin_settings.generate_map()
        if not settings.ui_visible:
            for ANT in settings.ants:
                ANT.x = settings.nest_location[0]
                ANT.y = settings.nest_location[1]
            for SOLDIER in settings.soldiers:
                SOLDIER.x = settings.nest_location[0]
                SOLDIER.y = settings.nest_location[1]
            for QUEEN in settings.queen:
                QUEEN.x = settings.nest_location[0]
                QUEEN.y = settings.nest_location[1]


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
                sys.exit(1)
            elif event.key == pygame.K_SPACE:
                settings.paused = not settings.paused
                logging.info("Pause event received.")
            elif event.key == pygame.K_1:
                settings.selected_tool = 1
            elif event.key == pygame.K_2:
                settings.selected_tool = 2
            elif event.key == pygame.K_3:
                settings.selected_tool = 3
            elif event.key == pygame.K_4:
                settings.selected_tool = 4
            elif event.key == pygame.K_5:
                settings.selected_tool = 5
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and settings.selected_tool == 1:
                settings.drawing_food = True
            elif event.button == 1 and settings.selected_tool == 2:
                settings.drawing_ant = True
            elif event.button == 1 and settings.selected_tool == 3:
                settings.drawing_magnet = True
            elif event.button == 1 and settings.selected_tool == 4:
                settings.drawing_wall = True
            elif event.button == 1 and settings.selected_tool == 5:
                settings.drawing_floor = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and settings.selected_tool == 1:
                settings.drawing_food = False
            elif event.button == 1 and settings.selected_tool == 2:
                settings.drawing_ant = False
            elif event.button == 1 and settings.selected_tool == 3:
                settings.drawing_magnet = False
            elif event.button == 1 and settings.selected_tool == 4:
                settings.drawing_wall = False
            elif event.button == 1 and settings.selected_tool == 5:
                settings.drawing_floor = False
        elif event.type == pygame.MOUSEMOTION:
            if settings.drawing_food:
                food2.draw(event.pos, threshold_slider, seed_button, speed_slider, start_button)
            elif settings.drawing_ant:
                ant2.draw(event.pos, threshold_slider, seed_button, speed_slider, start_button)
            elif settings.drawing_magnet:
                magnet.draw(event.pos)
            elif settings.drawing_wall:
                wall.draw(event.pos, threshold_slider, seed_button, speed_slider, start_button)
            elif settings.drawing_floor:
                floor.draw(event.pos, threshold_slider, seed_button, speed_slider, start_button)
        elif event.type == pygame.MOUSEWHEEL:
            new_camera_y = settings.camera_y - (event.y * 20)

            if new_camera_y > 0:
                settings.camera_y = 0
            elif new_camera_y < -960:
                settings.camera_y = -960
            else:
                settings.camera_y = new_camera_y

        if threshold_slider.handle_event(event):
            regenerate_perlin_map()

        if seed_button.handle_event(event):
            seed_button_value = random.randint(-2147483647, 2147483647)
            settings.food_locations = set()
            regenerate_perlin_map()

        settings.ant_slider.handle_event(event)
        soldier_slider.handle_event(event)
        queen_slider.handle_event(event)
        speed_slider.handle_event(event)

        if start_button.handle_event(event) and settings.button_type:
            settings.ui_visible = False
            settings.ants = [worker.Ant(settings.nest_location[0], settings.nest_location[1], settings.nest_location,
                                        settings.pheromone_map, speed_slider.value)
                             for _ in range(int(settings.ant_slider.value))]
            settings.soldiers = [
                soldier.Soldier(settings.nest_location[0], settings.nest_location[1], settings.nest_location,
                                settings.pheromone_map, speed_slider.value)
                for _ in range(int(soldier_slider.value))]
            settings.queen = [queen.Queen(settings.nest_location[0], settings.nest_location[1], settings.nest_location,
                                          settings.pheromone_map, speed_slider.value)
                              for _ in range(1)]
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
        if queen_slider.value >= 0.5:
            for Soldier in settings.soldiers:
                Soldier.move()
            for Queen in settings.queen:
                Queen.move()
        settings.pheromone_map *= 0.99

    for x in range(settings.MAP_WIDTH):
        for y in range(settings.MAP_HEIGHT):
            if perlin.perlin_settings.map_data[x, y] == 1:
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
                           (int(ant.x * 10) - settings.camera_x, int(ant.y * 10) - settings.camera_y), 4)
    for soldier in settings.soldiers:
        ant_color = pygame.Color(settings.SOLDIER_COLOR)
        pygame.draw.circle(screen, ant_color,
                           (int(soldier.x * 10) - settings.camera_x, int(soldier.y * 10) - settings.camera_y), 6)
    for queen in settings.queen:
        ant_color = pygame.Color(settings.QUEEN_COLOR)
        pygame.draw.circle(screen, ant_color,
                           (int(queen.x * 10) - settings.camera_x, int(queen.y * 10) - settings.camera_y), 10)

    screen.blit(ant_nest, (((settings.MONITOR_WIDTH // 2) - (100 // 2)) - +settings.camera_x, -50 - settings.camera_y))

    threshold_slider.draw(screen)
    seed_button.draw(screen)

    text_threshold = render_text_with_border(f"Threshold: {perlin.perlin_settings.threshold:.2f}", (255, 255, 255))
    text_seed = render_text_with_border(f"Seed: {perlin.perlin_settings.seed}", (255, 255, 255))
    text_selected_tool = render_text_with_border(f"Tool: None", (255, 255, 255))
    if settings.selected_tool == 1:
        text_selected_tool = render_text_with_border(f"Tool: Food", (255, 255, 255))
    elif settings.selected_tool == 2:
        text_selected_tool = render_text_with_border(f"Tool: Ants", (255, 255, 255))
    elif settings.selected_tool == 3:
        text_selected_tool = render_text_with_border(f"Tool: Magnet", (255, 255, 255))
    elif settings.selected_tool == 4:
        text_selected_tool = render_text_with_border(f"Tool: Wall", (255, 255, 255))
    elif settings.selected_tool == 5:
        text_selected_tool = render_text_with_border(f"Tool: Floor", (255, 255, 255))

    screen.blit(text_threshold, (320, 9))
    screen.blit(text_seed, (320, 54))
    screen.blit(text_selected_tool, (10, settings.MONITOR_HEIGHT - 30))

    if settings.ui_visible:
        settings.ant_slider.draw(screen)
        soldier_slider.draw(screen)
        queen_slider.draw(screen)
        speed_slider.draw(screen)
        start_button.draw(screen)

        text_ants = render_text_with_border(f"Workers: {int(settings.ant_slider.value)}", (255, 255, 255))
        text_soldiers = render_text_with_border(f"Soldiers: {int(soldier_slider.value)}", (255, 255, 255))
        if queen_slider.value >= 0.5:
            text_queen = render_text_with_border("Enable Queen: Yes", (255, 255, 255))
        else:
            text_queen = render_text_with_border("Enable Queen: No", (255, 255, 255))
        text_speed = render_text_with_border(f"Speed: {speed_slider.value:.2f}", (255, 255, 255))

        screen.blit(text_ants, (320, 99))
        screen.blit(text_soldiers, (320, 139))
        screen.blit(text_queen, (320, 179))
        screen.blit(text_speed, (320, 219))
    else:
        food_progressbar.draw(screen)

        food_progressbar.set_value(settings.collected_food)
        food_progressbar.max_value = settings.total_food

        text_food = render_text_with_border(f"Food Collected: {settings.collected_food}/{settings.total_food}",
                                            (255, 255, 255))

        screen.blit(text_food, (320, 99))

        if settings.food_locations is None or len(
                settings.food_locations) == 0 or settings.collected_food == settings.total_food and settings.old_total_food < settings.total_food:
            settings.total_food = settings.collected_food
            old_total_food = settings.total_food

    pygame.display.flip()
    settings.clock.tick(settings.FPS)

pygame.quit()
logging.info("Game closed.")
