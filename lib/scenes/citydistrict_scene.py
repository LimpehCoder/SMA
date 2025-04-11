from base_scene import BaseScene
import pygame
from objects import Courier, Box, spawn_couriers, spawn_boxes, spawn_vehicles, Van, Car

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
class CityDistrictScene(BaseScene):  # Inherits from BaseScene
    def __init__(self, district_id):  # Accepts unique district identifier (e.g. 1, 2, 3)
        self.bg_color = (80, 60, 60)  # Background color (dark reddish-brown)
        self.name = f"City_District{district_id}"  # Generate name like "City_District1"
        self.district_id = district_id  # Store the district ID for potential logic use

    def render(self, screen):  # Draw the scene visuals
        screen.fill(self.bg_color)  # Fill with the district's color
        font = pygame.font.SysFont("Arial", 48)  # Load large font
        label = font.render(self.name, True, (255, 255, 255))  # Render the district name
        screen.blit(label, (50, 50))  # Display the name label near the top-left