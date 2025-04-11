import pygame
from lib.spawner import Courier, Box, spawn_couriers, spawn_boxes, spawn_vehicles, Van, Car

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
class BaseScene:
    def handle_event(self, event): pass  # Placeholder: to be overridden in derived scenes
    def update(self, dt, clock): pass  # Placeholder: updates scene logic each frame
    def render(self, screen): pass  # Placeholder: draws scene visuals each frame