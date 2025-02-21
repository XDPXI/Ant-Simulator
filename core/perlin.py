import random

import numpy as np
from perlin_noise import PerlinNoise

import settings
from core import logging, map


class PerlinNoiseSettings:
    def __init__(self, scale: float = 40.0, threshold: float = 0.1, seed: int = None):
        self.seed = (
            seed if seed is not None else random.randint(-2147483647, 2147483647)
        )
        self.scale = scale
        self.threshold = threshold
        self.noise_generator = PerlinNoise(octaves=1, seed=self.seed)
        self.map_data = self.generate_map()

        logging.info(
            f"Perlin noise initialized with seed {self.seed}, scale {self.scale}, threshold {self.threshold}"
        )

    def generate_map(self) -> np.ndarray:
        map_data = np.zeros((settings.MAP_WIDTH, settings.MAP_HEIGHT), dtype=int)

        for X in range(settings.MAP_WIDTH):
            for Y in range(settings.MAP_HEIGHT):
                noise_value = self.noise_generator([X / self.scale, Y / self.scale])
                map_data[X, Y] = 1 if noise_value > self.threshold else 0

        return map_data


perlin_settings = PerlinNoiseSettings()


def regenerate(seed_button_value, threshold_slider):
    new_threshold = threshold_slider.value
    new_seed = int(seed_button_value)

    if perlin_settings.threshold != new_threshold or perlin_settings.seed != new_seed:
        perlin_settings.threshold = new_threshold
        perlin_settings.seed = new_seed
        perlin_settings.noise_generator = PerlinNoise(octaves=1, seed=new_seed)
        perlin_settings.map_data = perlin_settings.generate_map()

        if not settings.ui_visible:
            nest_x, nest_y = settings.nest_location

            for entity_group in (settings.ants, settings.soldiers, settings.queen):
                for entity in entity_group:
                    entity.x, entity.y = nest_x, nest_y

            for enemy in settings.enemies:
                enemy.x, enemy.y = (
                    settings.MONITOR_WIDTH // 2,
                    settings.MONITOR_HEIGHT // 2,
                )

        for x in range(settings.MAP_WIDTH):
            for y in range(settings.MAP_HEIGHT):
                map.data[x, y] = 1

        for x in range(settings.MAP_WIDTH):
            if x < settings.MAP_WIDTH // 2 - 4 or x > settings.MAP_WIDTH // 2 + 4:
                perlin_settings.map_data[x, 0] = 1
