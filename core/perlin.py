import logging

import numpy as np
from perlin_noise import PerlinNoise

from core import settings


class PerlinNoiseSettings:
    def __init__(self, scale=40.0, threshold=0.1, seed=0):
        self.scale = scale
        self.threshold = threshold
        self.seed = seed
        self.noise_generator = PerlinNoise(octaves=1, seed=self.seed)
        self.map_data = self.generate_map()
        logging.info(f"Perlin noise initialized with seed {self.seed}")

    def generate_map(self):
        return np.array([
            [1 if self.noise_generator([X / self.scale, Y / self.scale]) > self.threshold else 0
             for Y in range(settings.MAP_HEIGHT)] for X in range(settings.MAP_WIDTH)
        ])
