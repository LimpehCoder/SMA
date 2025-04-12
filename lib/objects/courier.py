import	pygame
from pygame.math import Vector2  # Import Vector2 for 2D vector math
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from loadimage import load_image  # Import image loading function

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

class Courier:
    def __init__(self, id, position, image_path):
        self.id = id
        self.status = "Reporting"
        self.position = position
        self.target_position = Vector2(0, 0)
        self.grid_assigned = False
        self.carrying = []
        self.shift = None
        self.speed = 300
        self.queue_index = None
        self.assigned_vehicle = None
        self.font = pygame.font.SysFont("Arial", 16)
        self.image = load_image(image_path, (32, 32))

    def request_slot(self, box_pile):
        for i, slot in enumerate(box_pile.occupied_slots):
            if slot is None:
                box_pile.occupied_slots[i] = self
                self.target_position = box_pile.queue_slots[i]
                self.queue_index = i
                self.status = "Move_to_Queue"
                print(f"{self.id} assigned to queue slot {i}")
                return True
        return False

    def pickup_box(self, box_pile):
        if not box_pile.is_empty():
            self.carrying.append("Box")
            box_pile.decrement()
            box_pile.occupied_slots[self.queue_index] = None
            self.queue_index = None
            self.status = "Move_to_Vehicle"
            if self.assigned_vehicle:
                self.target_position = self.assigned_vehicle.target_position
            print(f"{self.id} picked up a box and is moving to vehicle")

    def deliver_box(self):
        if self.assigned_vehicle and self.carrying:
            self.assigned_vehicle.load_box()
            self.carrying.clear()
            self.status = "Idle"
            print(f"{self.id} delivered a box to vehicle")

    def update(self, dt):
        if self.status in ["Entering", "Forming", "Move_to_Queue", "Move_to_Vehicle"]:
            direction = self.target_position - self.position
            if direction.length() < 2:
                if self.status == "Entering":
                    self.status = "Idle"
                elif self.status == "Forming":
                    self.status = "Ready"
                elif self.status == "Move_to_Queue":
                    self.status = "Queuing"
                elif self.status == "Move_to_Vehicle":
                    self.deliver_box()
            else:
                direction.normalize_ip()
                self.position += direction * self.speed * (dt / 1000.0)

    def render(self, screen):
        screen.blit(self.image, self.position)
        if self.carrying:
            label = self.font.render(str(len(self.carrying)), True, (255, 255, 255))
            screen.blit(label, (self.position.x + 8, self.position.y - 18))

class StaffCourier(Courier):
    def __init__(self, id):
        entry_point = Vector2(640, -40)  # From top
        super().__init__(id=id, position=entry_point, image_path="courier_staff.png")
        self.type = "Courier_Staff"

class SubconCourier(Courier):
    def __init__(self, id):
        entry_point = Vector2(640, SCREEN_HEIGHT + 40)  # From bottom
        super().__init__(id=id, position=entry_point, image_path="courier_subcon.png")
        self.type = "Courier_Subcon"
