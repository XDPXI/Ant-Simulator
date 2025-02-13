import math

from core import logging
import settings

def draw(eventPos):
    x, y = eventPos
    radius = 10
    entities = [
        ('ant', settings.ants),
        ('soldier', settings.soldiers),
        ('queen', settings.queen)
    ]

    for entity_type, entity_list in entities:
        for entity in entity_list.copy():
            try:
                dx = (x + settings.camera_x) - (entity.x * 10)
                dy = (y + settings.camera_y) - (entity.y * 10)
                distance = math.hypot(dx, dy)

                if distance <= radius * 10:
                    logging.debug(f"{entity_type.capitalize()} at ({entity.x}, {entity.y}) attracted")
                    entity.x = (x + settings.camera_x) // 10
                    entity.y = (y + settings.camera_y) // 10
            except ZeroDivisionError:
                logging.error("Invalid camera position")