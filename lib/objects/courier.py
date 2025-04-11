import	pygame
from pygame.math import Vector2  # Import Vector2 for 2D vector math
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from loadimage import load_image  # Import image loading function

class Courier:
    def __init__(self, courier_type, id, position=None):
        self.type = courier_type  # "Courier_Staff" or "Courier_Subcon"
        self.id = id  # Unique ID string like "S_Monday_0"
        self.status = "Entering"  # Initial status, used for animation state
        self.position = position or COURIER_ENTRY_POINT.copy()  # Starting position (off-screen by default)
        self.carrying = []  # List of boxes currently held by the courier
        self.shift = None  # Placeholder for shift assignment (e.g., ACycle, BCycle)
        self.speed = 300  # Movement speed in pixels per second
        self.target_position = pygame.Vector2(0, 0)  # Position the courier will move toward
        self.grid_assigned = False  # Has the courier been assigned a final idle location?

        if courier_type == "Courier_Staff":
            self.image = load_image("courier_staff.png", (32, 32))  # Load the staff sprite
        else:
            self.image = load_image("courier_subcon.png", (32, 32))  # Load the subcontractor sprite
    
    def request_slot(self, box_pile):
        for i, slot in enumerate(box_pile.occupied_slots):
            if slot is None:
                box_pile.occupied_slots[i] = self
                self.target_position = box_pile.queue_slots[i]
                self.queue_index = i
                self.status = "Queued"
                print(f"{self.id} joined the pickup queue at slot {i}")
                return True
        return False  # No available slot

    def update(self, dt):
        if self.status in ["Entering", "Forming", "Queued", "QueuedIdle"]:  # Animate movement in any moving state
            direction = self.target_position - self.position
            distance = direction.length()

            if distance < 2:  # Arrived
                if self.status == "Entering":
                    self.status = "Idle"
                elif self.status == "Forming":
                    self.status = "Ready"
                elif self.status == "Queued":
                    self.status = "QueuedIdle"  # New substate: waiting in place
            else:
                direction.normalize_ip()
                self.position += direction * self.speed * (dt / 1000.0)
        # print(f"{self.id} status is {self.status}")	

    def render(self, screen):
        screen.blit(self.image, self.position)  # Draw courier at current position