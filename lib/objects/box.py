import random
from loadimage import load_image  # Import image loading function
from pygame.math import Vector2  # Import Vector2 for 2D vector math
import pygame

class BoxPile:
    def __init__(self, position):
        self.position = Vector2(position)  # Central position of the pile
        self.count = 0  # Number of boxes currently in the pile
        self.font = pygame.font.SysFont("Arial", 20)  # Font for rendering the counter
        self.right_queue_slots = self.generate_right_queue_positions()
        self.top_queue_slots = self.generate_top_queue_positions()
        self.bottom_queue_slots = self.generate_bottom_queue_positions()
        self.right_occupied = [None] * len(self.right_queue_slots)
        self.top_occupied = [None] * len(self.top_queue_slots)
        self.bottom_occupied = [None] * len(self.bottom_queue_slots)


    def set_count(self, count):
        self.count = max(0, count)  # Set pile count, ensuring non-negative

    def increment(self, count=1):
        self.count += count  # Increase pile count

    def decrement(self):
        self.count = max(0, self.count - 1)  # Decrease pile count, clamping at zero

    def is_empty(self):
        return self.count == 0  # Returns True if no boxes are left

    def render(self, screen):
        if self.count > 0:
            box_img = load_image("box.png")  # Load box icon
            screen.blit(box_img, (self.position.x, self.position.y))  # Draw single icon

            # Draw counter above the box
            label = self.font.render(str(self.count), True, (255, 255, 255))
            screen.blit(label, (self.position.x + 20, self.position.y - 15))

    def generate_right_queue_positions(self, spacing=40, slots=10):
        x, y = self.position.x, self.position.y
        return [Vector2(x + spacing + i * spacing, y) for i in range(slots)]

    def generate_top_queue_positions(self, spacing=40, slots=10):
        x, y = self.position.x, self.position.y
        return [Vector2(x + i * spacing, y - spacing) for i in range(slots)]

    def generate_bottom_queue_positions(self, spacing=40, slots=10):
        x, y = self.position.x, self.position.y
        return [Vector2(x + i * spacing, y + spacing) for i in range(slots)]