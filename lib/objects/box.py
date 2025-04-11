import random
from loadimage import load_image  # Import image loading function
from pygame.math import Vector2  # Import Vector2 for 2D vector math
import pygame

class Box:
    def __init__(self, id, position=None):
        self.id = id
        self.status = "Waiting"
        self.position = position or (random.randint(100, 600), random.randint(100, 600))
        self.image = load_image("box.png")

    def render(self, screen):
        screen.blit(self.image, self.position)  # Draw box at current location

class BoxPile:
    def __init__(self, position):
        self.position = Vector2(position)
        self.count = 0
        self.font = pygame.font.SysFont("Arial", 20)

    def set_count(self, count):
        self.count = max(0, count)

    def increment(self, count=1):
        self.count += count

    def decrement(self):
        self.count = max(0, self.count - 1)

    def is_empty(self):
        return self.count == 0

    def render(self, screen):
        if self.count > 0:
            box_img = load_image("box.png")
            screen.blit(box_img, (self.position.x, self.position.y))

            # Draw counter
            label = self.font.render(str(self.count), True, (255, 255, 255))
            screen.blit(label, (self.position.x + 20, self.position.y - 15))
