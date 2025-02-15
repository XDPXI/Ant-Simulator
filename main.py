import os
import platform
import random
import sys

import pygame

import settings
from core import perlin, logging
from entities import worker, queen, soldier
from tools import ant as ant2, food as food2, magnet, wall, floor, enemy

logging.setup("INFO")

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

from gui import slider, button, progress_bar, text

icon = pygame.image.load("assets/icon.png").convert_alpha()
pygame.display.set_icon(icon)
logging.info("Window and icon initialized.")


seed_button_value = perlin.perlin_settings.seed


def generate_map():
    global seed_button_value
    seed_button_value = random.randint(-2147483647, 2147483647)
    settings.food_locations = set()
    perlin.regenerate(seed_button_value, threshold_slider)


def start():
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


threshold_slider = slider.Slider(10, 10, 300, 0.0, 1.0, perlin.perlin_settings.threshold)
soldier_slider = slider.Slider(10, 140, 300, 0, 10, 10)
queen_slider = slider.Slider(10, 180, 300, 0, 1, 1)
food_progressbar = progress_bar.ProgressBar(x=10, y=100, width=300, min_value=0, max_value=100, initial_value=0,
                                            label="Food")
speed_slider = slider.Slider(10, 220, 300, 0.0, 10.0, 0.5)

seed_button = button.Button(
    x=10, y=50, width=300, height=30,
    text="Generate New Map",
    font_size=28,
    color=(0, 128, 255),
    text_color=(255, 255, 255),
    on_click=generate_map
)
start_button = button.Button(
    x=10, y=260, width=300, height=50,
    text="Start",
    font_size=40,
    color=(0, 128, 255),
    text_color=(255, 255, 255),
    on_click=start
)

sun_image = pygame.image.load("assets/sun.png").convert_alpha()
sun_image = pygame.transform.scale(sun_image, (300, 300))

ant_nest = pygame.image.load("assets/nest.png").convert_alpha()
ant_nest = pygame.transform.scale(ant_nest, (100, 50))


logging.info("Game loop started.")
while settings.running:
    screen.fill("#87CEEB")
    pygame.draw.rect(screen, settings.BG_COLOR,
                     (0 - settings.camera_x, 0 - settings.camera_y, settings.MONITOR_WIDTH, settings.MONITOR_HEIGHT))

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
            elif pygame.K_1 <= event.key <= pygame.K_6:
                settings.selected_tool = event.key - pygame.K_0

        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            tool_actions = {
                1: "drawing_food",
                2: "drawing_ant",
                3: "drawing_magnet",
                4: "drawing_wall",
                5: "drawing_floor",
                6: "drawing_enemy"
            }
            if event.button == 1 and settings.selected_tool in tool_actions:
                setattr(settings, tool_actions[settings.selected_tool], event.type == pygame.MOUSEBUTTONDOWN)

        elif event.type == pygame.MOUSEMOTION:
            drawing_tools = {
                "drawing_food": food2,
                "drawing_ant": ant2,
                "drawing_magnet": magnet,
                "drawing_wall": wall,
                "drawing_floor": floor,
                "drawing_enemy": enemy
            }
            for tool, obj in drawing_tools.items():
                if getattr(settings, tool, False):
                    obj.draw(event.pos, threshold_slider, seed_button, speed_slider, start_button)

        elif event.type == pygame.MOUSEWHEEL:
            settings.camera_y = max(-960, min(0, settings.camera_y - (event.y * 20)))

        if threshold_slider.handle_event(event):
            perlin.regenerate(seed_button_value, threshold_slider)

        settings.ant_slider.handle_event(event)
        soldier_slider.handle_event(event)
        queen_slider.handle_event(event)
        speed_slider.handle_event(event)
        seed_button.handle_event(event)
        start_button.handle_event(event)

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

        for Enemy in settings.enemies:
            Enemy.move()

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

    screen.blit(sun_image, ((settings.MONITOR_WIDTH - 400) - settings.camera_x, -900 - settings.camera_y))
    pygame.draw.rect(screen, "#4F7942", (0 - settings.camera_x, -50 - settings.camera_y, settings.MONITOR_WIDTH, 50))

    entity_groups = (
        (settings.ants, lambda ant: settings.FOOD_COLOR if ant.has_food else settings.ANT_COLOR, 4),
        (settings.soldiers, lambda _: settings.SOLDIER_COLOR, 6),
        (settings.queen, lambda _: settings.QUEEN_COLOR, 10),
        (settings.enemies, lambda _: settings.ENEMY_COLOR, 6)
    )

    for entity_list, color_func, size in entity_groups:
        for entity in entity_list:
            entity_color = pygame.Color(color_func(entity))
            pygame.draw.circle(
                screen,
                entity_color,
                (int(entity.x * 10) - settings.camera_x, int(entity.y * 10) - settings.camera_y),
                size
            )

    screen.blit(ant_nest, (((settings.MONITOR_WIDTH // 2) - (100 // 2)) - settings.camera_x, -50 - settings.camera_y))

    threshold_slider.draw(screen)
    seed_button.draw(screen)

    text_threshold = text.border(f"Threshold: {perlin.perlin_settings.threshold:.2f}", (255, 255, 255))
    text_seed = text.border(f"Seed: {perlin.perlin_settings.seed}", (255, 255, 255))

    tool_names = {
        1: "Food",
        2: "Ants",
        3: "Magnet",
        4: "Wall",
        5: "Floor",
        6: "Enemy"
    }
    selected_tool_name = tool_names.get(settings.selected_tool, "None")
    text_selected_tool = text.border(f"Tool: {selected_tool_name}", (255, 255, 255))

    screen.blit(text_threshold, (320, 9))
    screen.blit(text_seed, (320, 54))
    screen.blit(text_selected_tool, (10, settings.MONITOR_HEIGHT - 30))

    if settings.ui_visible:
        settings.ant_slider.draw(screen)
        soldier_slider.draw(screen)
        queen_slider.draw(screen)
        speed_slider.draw(screen)
        start_button.draw(screen)

        text_ants = text.border(f"Workers: {int(settings.ant_slider.value)}", (255, 255, 255))
        text_soldiers = text.border(f"Soldiers: {int(soldier_slider.value)}", (255, 255, 255))
        text_queen = text.border(f"Enable Queen: {'Yes' if queen_slider.value >= 0.5 else 'No'}", (255, 255, 255))
        text_speed = text.border(f"Speed: {speed_slider.value:.2f}", (255, 255, 255))

        screen.blit(text_ants, (320, 99))
        screen.blit(text_soldiers, (320, 139))
        screen.blit(text_queen, (320, 179))
        screen.blit(text_speed, (320, 219))
    else:
        food_progressbar.draw(screen)
        food_progressbar.set_value(settings.collected_food)
        food_progressbar.max_value = settings.total_food

        text_food = text.border(f"Food Collected: {settings.collected_food}/{settings.total_food}", (255, 255, 255))
        screen.blit(text_food, (320, 99))

        if not settings.food_locations or settings.collected_food == settings.total_food:
            settings.total_food = settings.collected_food

    pygame.display.flip()
    settings.clock.tick(settings.FPS)

pygame.quit()
logging.info("Game closed.")