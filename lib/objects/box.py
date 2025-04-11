import random
from loadimage import load_image  # Import image loading function

class Box:
    def __init__(self, id):
        self.id = id  # Unique ID for the box, e.g., "B_ACycle_1"
        self.status = "Waiting"  # Current status, can be updated (e.g., "Loaded", "Delivered")
        self.position = (random.randint(100, 600), random.randint(100, 600))  # Random drop location in SortingArea
        self.image = load_image("box.png")  # Load the image for rendering

    def render(self, screen):
        screen.blit(self.image, self.position)  # Draw box at current location