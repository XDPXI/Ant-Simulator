import math

import settings
from core import logging


def draw(event_pos, threshold_slider, seed_button, speed_slider, start_button):
    mouse_x, mouse_y = event_pos
    radius = 10 * settings.GRID_SIZE

    entities = [
        ('ant', settings.ants),
        ('soldier', settings.soldiers),
        ('queen', settings.queen),
        ('enemy', settings.enemies)
    ]

    for entity_type, entity_list in entities:
        for entity in entity_list.copy():
            try:
                dx = (mouse_x + settings.camera_x) - (entity.x * settings.GRID_SIZE)
                dy = (mouse_y + settings.camera_y) - (entity.y * settings.GRID_SIZE)
                distance = math.hypot(dx, dy)

                if distance <= radius:
                    logging.debug(f"{entity_type.capitalize()} at ({entity.x}, {entity.y}) attracted")
                    entity.x = (mouse_x + settings.camera_x) // settings.GRID_SIZE
                    entity.y = (mouse_y + settings.camera_y) // settings.GRID_SIZE
            except Exception as e:
                logging.error(f"Error processing entity: {e}")
