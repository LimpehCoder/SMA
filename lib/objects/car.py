class Car:
    def __init__(self, position):
        self.position = position  # Starting position in the scene (usually directly placed, not animated)
        self.occupied = False  # Whether a courier has claimed this car
        self.driver = None  # Reference to the assigned courier
        self.image = load_image("car.png", (32, 24))  # Load and scale the car image

    def render(self, screen):
        screen.blit(self.image, self.position)  # Draw car at its current position