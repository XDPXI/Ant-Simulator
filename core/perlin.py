import random

import numpy as np
from perlin_noise import PerlinNoise

import settings
from core import logging


class PerlinNoiseSettings:
    def __init__(self, scale: float = 40.0, threshold: float = 0.1, seed: int = None):
        self.seed = seed if seed is not None else random.randint(-2147483647, 2147483647)
        self.scale = scale
        self.threshold = threshold
        self.noise_generator = PerlinNoise(octaves=1, seed=self.seed)
        self.map_data = self.generate_map()

        logging.info(f"Perlin noise initialized with seed {self.seed}, scale {self.scale}, threshold {self.threshold}")

    def generate_map(self) -> np.ndarray:
        map_data = np.zeros((settings.MAP_WIDTH, settings.MAP_HEIGHT), dtype=int)

        for X in range(settings.MAP_WIDTH):
            for Y in range(settings.MAP_HEIGHT):
                noise_value = self.noise_generator([X / self.scale, Y / self.scale])
                map_data[X, Y] = 1 if noise_value > self.threshold else 0

        return map_data


perlin_settings = PerlinNoiseSettings()
