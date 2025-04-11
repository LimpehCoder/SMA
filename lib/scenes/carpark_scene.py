from base_scene import BaseScene
import pygame
from objects import Courier, Box, spawn_couriers, spawn_boxes, spawn_vehicles, Van, Car

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
class CarparkScene(BaseScene):  # Inherits from BaseScene
    def __init__(self):
        self.bg_color = (30, 80, 60)  # Set background color (dark greenish)
        self.name = "Carpark"  # Scene name for labeling
        self.vans = []  # List to store van objects
        self.cars = []  # List to store car objects
        self.spawned_today = False  # Tracks if today's vehicles have been spawned

    def render(self, screen):  # Draws everything on this scene
        screen.fill(self.bg_color)  # Fill background with carpark color
        font = pygame.font.SysFont("Arial", 48)  # Load font
        label = font.render(self.name, True, (255, 255, 255))  # Render scene name text
        screen.blit(label, (50, 50))  # Display scene name at top-left

        for van in self.vans:  # Draw each van
            van.render(screen)

        for car in self.cars:  # Draw each car
            car.render(screen)