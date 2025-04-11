from pygame.math import Vector2
from loadimage import load_image  # Import image loading function

class Car:
    def __init__(self, position):
        self.position = position  # Starting position in the scene (usually directly placed, not animated)
        self.occupied = False  # Whether a courier has claimed this car
        self.driver = None  # Reference to the assigned courier
        self.image = load_image("car.png", (32, 24))  # Load and scale the car image
        self.target_position = Vector2(position)  # The in-scene location the van should drive to
        self.speed = 120  # Movement speed in pixels per second

    def update(self, dt):
        direction = self.target_position - self.position  # Get vector to target
        if direction.length() > 1:  # If far enough from destination, move
            direction.normalize_ip()  # Normalize to unit direction vector
            self.position += direction * self.speed * (dt / 1000.0)  # Move based on speed and time delta

    def render(self, screen):
        screen.blit(self.image, self.position)  # Draw car at its current position