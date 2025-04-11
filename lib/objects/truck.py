from pygame.math import Vector2
from loadimage import load_image  # Custom utility for loading and scaling images

from pygame.math import Vector2
from loadimage import load_image

class Truck:
    def __init__(self, start_y=360, cycle_name=None):
        self.target_position = Vector2(-150 + 96 * 2, start_y)  # Final stop position (on screen)
        self.position = Vector2(-150, self.target_position.y)  # Off-screen left
        self.exit_position = Vector2(-150, self.target_position.y)  # Exit back to the left
        self.speed = 120  # Movement speed in pixels/sec
        self.image = load_image("truck.png", (96, 48))
        self.boxes = []
        self.loaded = False
        self.arrived = False
        self.departing = False
        self.despawned = False
        self.cycle = cycle_name

        if self.cycle:
            self.spawn_boxes_for_cycle(self.cycle)

    def spawn_boxes_for_cycle(self, cycle_name):
        count = 20 if cycle_name == "ACycle" else 30 if cycle_name == "BCycle" else 40  # Example logic
        for i in range(count):
            self.boxes.append(f"Box_{cycle_name}_{i}")  # You can replace with actual Box objects
        self.loaded = True

    def update(self, dt):
        if not self.arrived:
            direction = self.target_position - self.position
            if direction.length() > 1:
                direction.normalize_ip()
                self.position += direction * self.speed * (dt / 1000.0)
            else:
                self.arrived = True
        elif self.departing:
            direction = self.exit_position - self.position
            if direction.length() > 1:
                direction.normalize_ip()
                self.position += direction * self.speed * (dt / 1000.0)
            else:
                self.despawned = True

    def render(self, screen):
        screen.blit(self.image, self.position)
        if self.arrived and self.loaded:
            # Render only one box image as visual placeholder
            box_img = load_image("box.png")
            screen.blit(box_img, (self.position.x + 40, self.position.y - 20))

    def unload_all(self):
        self.boxes.clear()
        self.loaded = False
        self.departing = True  # Trigger departure after unloading

    def is_ready_to_unload(self):
        return self.arrived and self.loaded

    def is_ready_to_despawn(self):
        return self.despawned

