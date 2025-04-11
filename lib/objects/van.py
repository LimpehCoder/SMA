from pygame.math import Vector2
from loadimage import load_image

class Van:
    def __init__(self, position, scene_name="Carpark"):
        self.position = Vector2(position.x, -100)  # Start off-screen on the left, matching target's Y
        self.target_position = Vector2(position)  # The in-scene location the van should drive to
        self.scene = scene_name  # Track which scene the van belongs to (e.g., "Carpark")
        self.occupied = False  # Whether a courier has claimed this van
        self.driver = None  # Reference to the assigned courier
        self.speed = 120  # Movement speed in pixels per second
        self.image = load_image("van.png", (48, 32))  # Load and scale the van image

    def update(self, dt):
        direction = self.target_position - self.position  # Get vector to target
        if direction.length() > 1:  # If far enough from destination, move
            direction.normalize_ip()  # Normalize to unit direction vector
            self.position += direction * self.speed * (dt / 1000.0)  # Move based on speed and time delta

    def render(self, screen):
        screen.blit(self.image, self.position)  # Draw van at its current position