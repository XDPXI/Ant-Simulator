import numpy as np
from noise import snoise2

import logging
from core import settings


class PerlinNoiseSettings:
    def __init__(self, scale=40.0, threshold=0.1, seed=0):
        self.scale = scale
        self.threshold = threshold
        self.seed = seed
        self.noise_generator = lambda x, y: snoise2(x / self.scale, y / self.scale, octaves=1, base=self.seed)
        self.map_data = self.generate_map()
        logging.info(f"Noise initialized with seed {self.seed}")

    def generate_map(self):
        width, height = settings.MAP_WIDTH, settings.MAP_HEIGHT
        x_indices, y_indices = np.meshgrid(np.arange(width), np.arange(height), indexing="ij")
        noise_values = np.vectorize(self.noise_generator)(x_indices, y_indices)
        map_data = (noise_values > self.threshold).astype(np.uint8)

        assert map_data.shape == (width, height), f"Shape mismatch: {map_data.shape} != ({width}, {height})"

        return map_data
