import random
from loadimage import load_image  # Import image loading function
from pygame.math import Vector2  # Import Vector2 for 2D vector math
import pygame

class BoxPile:
    def __init__(self, position):
        self.position = Vector2(position)  # Central position of the pile
        self.count = 0  # Number of boxes currently in the pile
        self.font = pygame.font.SysFont("Arial", 20)  # Font for rendering the counter
        self.queue_slots = self.generate_queue_positions()  # Positions around the pile for couriers
        self.occupied_slots = [None] * len(self.queue_slots)  # Track which couriers are at which slots

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

    def generate_queue_positions(self, spacing=40, slots_per_side=10):
        x, y = self.position.x, self.position.y
        queue_slots = []

        # Top row (horizontal line centered above the pile)
        for i in range(slots_per_side):
            offset = (i - slots_per_side // 2) * spacing
            queue_slots.append(Vector2(x + offset, y - spacing))

        # Bottom row (horizontal line centered below the pile)
        for i in range(slots_per_side):
            offset = (i - slots_per_side // 2) * spacing
            queue_slots.append(Vector2(x + offset, y + spacing))

        # Left row (horizontal line to the left of the pile, offset vertically to align center-ish)
        for i in range(slots_per_side):
            offset = (i - slots_per_side // 2) * spacing
            queue_slots.append(Vector2(x - spacing, y + offset))

        return queue_slots


