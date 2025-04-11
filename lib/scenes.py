import pygame
from objects import Courier, Box, spawn_couriers, spawn_boxes, spawn_vehicles, Van, Car

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

class BaseScene:
    def handle_event(self, event): pass  # Placeholder: to be overridden in derived scenes
    def update(self, dt, clock): pass  # Placeholder: updates scene logic each frame
    def render(self, screen): pass  # Placeholder: draws scene visuals each frame

class SortingAreaScene(BaseScene):
    def __init__(self, carpark_ref):
        self.carpark = carpark_ref  # Reference to the carpark scene (used to access vans/cars)
        self.bg_color = (60, 70, 90)  # Background color for the canvas
        self.name = "SortingArea_Daily"  # Scene identifier
        self.couriers = []  # List of couriers in this scene
        self.boxes = []  # List of boxes currently in the sorting area
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

        for b in self.boxes:
            b.render(screen)  # Draw each box

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

class StatisticsScene(BaseScene):  # Inherits from BaseScene to follow the same scene interface
    def __init__(self):
        self.bg_color = (20, 20, 20)  # Very dark background (almost black) for contrast
        self.name = "Statistics"  # Scene name used for rendering and identification

    def render(self, screen):  # Draw method for this scene
        screen.fill(self.bg_color)  # Fill the entire screen with the background color
        font = pygame.font.SysFont("Arial", 48)  # Create a font object for drawing text
        label = font.render(self.name, True, (255, 255, 255))  # Render the scene name in white
        screen.blit(label, (50, 50))  # Draw the label at position (50, 50) on screen