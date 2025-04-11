import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_scene import BaseScene
import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
class SortingAreaScene(BaseScene):
    def __init__(self, carpark_ref):
        self.carpark = carpark_ref  # Reference to the carpark scene (used to access vans/cars)
        self.bg_color = (60, 70, 90)  # Background color for the canvas
        self.name = "SortingArea"  # Scene identifier
        self.couriers = []  # List of couriers in this scene
        self.boxes = []  # List of boxes currently in the sorting area
        self.truck = None
        self.box_pile = None
        self.spawned_today = False  # Tracks whether couriers have been spawned today
        self.spawned_cycles = set()  # Tracks which box spawn cycles have run
        self.pending_couriers = []  # Queue of couriers waiting to enter the canvas
        self.courier_spawn_timer = 0  # Timer used to space out entry of couriers
        self.courier_spawn_interval = 300  # Delay between courier entries (ms)

    def assign_idle_positions(self):
        start_x = SCREEN_WIDTH - 50  # Start forming couriers from the right side of screen
        start_y = 80  # Top margin for the grid
        spacing = 35  # Distance between couriers in grid

        cols = 15  # Number of columns in the idle grid
        for index, courier in enumerate(self.couriers):
            if courier.status == "Idle" and not courier.grid_assigned:
                col = index % cols  # Column position based on index
                row = index // cols  # Row position based on index
                target_x = start_x - (col * spacing)  # Horizontal offset from the right
                target_y = start_y + (row * spacing)  # Vertical offset from the top
                courier.target_position = pygame.Vector2(target_x, target_y)  # Set movement goal
                courier.status = "Forming"  # Begin forming into grid
                courier.grid_assigned = True  # Prevent reassignment

    def render(self, screen):
        screen.fill(self.bg_color)  # Fill background
        font = pygame.font.SysFont("Arial", 36)  # Set font
        screen.blit(font.render(self.name, True, (255, 255, 255)), (50, 50))  # Draw scene name

        for c in self.couriers:
            c.render(screen)  # Draw each courier
        if self.truck:
            self.truck.render(screen)
        if self.box_pile:
            self.box_pile.render(screen)
        