import pygame
from pygame.math import Vector2  # Import Vector2 for 2D vector math
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from loadimage import load_image  # Import image loading function

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

class Courier:
    def __init__(self, id, position, image_path, idle_position):
        self.id = id
        self.status = "REPORTING"
        self.position = position
        self.idle_position = idle_position
        self.target_position = idle_position  # Will change when moving
        self.grid_assigned = False
        self.carrying = 0
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
                self.status = "MOVE_TO_QUEUE"
                print(f"{self.id} assigned to queue slot {i}")
                return True
        return False

    def pickup_box(self, box_pile):
        if not box_pile.is_empty():
            self.carrying += 1
            box_pile.decrement()
            if self.queue_index is not None:
                box_pile.occupied_slots[self.queue_index] = None
            self.queue_index = None
            self.status = "MOVE_TO_VEHICLE"
            if self.assigned_vehicle:
                self.target_position = self.assigned_vehicle.target_position
            print(f"{self.id} picked up a box and is moving to vehicle")

    def deliver_box(self):
        if self.assigned_vehicle and self.carrying > 0:
            self.assigned_vehicle.load_box()
            self.carrying = 0
            self.status = "IDLE"
            self.target_position = self.idle_position  # Return to idle spot
            print(f"{self.id} delivered a box to vehicle")

    def update(self, dt):
        if self.status in ["REPORTING", "MOVE_TO_QUEUE", "MOVE_TO_VEHICLE"]:
            direction = self.target_position - self.position
            if direction.length() < 2:
                self.position = self.target_position
                if self.status == "REPORTING":
                    self.status = "IDLE"
                elif self.status == "MOVE_TO_QUEUE":
                    self.status = "QUEUING"
                elif self.status == "MOVE_TO_VEHICLE":
                    self.deliver_box()
            else:
                direction.normalize_ip()
                self.position += direction * self.speed * (dt / 1000.0)

    def render(self, screen):
        screen.blit(self.image, self.position)
        if self.carrying:
            label = self.font.render(str(self.carrying), True, (255, 255, 255))
            screen.blit(label, (self.position.x + 8, self.position.y - 18))

# --- Grid generator functions ---
def generate_staff_idle_grid():
    return [
        Vector2(SCREEN_WIDTH - 50 - col * 40, 80 + row * 40)
        for row in range(3)
        for col in range(10)
    ]

def generate_subcon_idle_grid():
    return [
        Vector2(SCREEN_WIDTH - 50 - col * 40, SCREEN_HEIGHT - 200 + row * 40)
        for row in range(3)
        for col in range(10)
    ]

class StaffCourier(Courier):
    idle_grid = []  # This should be populated at the start of each day

    def __init__(self, id):
        entry_point = Vector2(640, -40)  # Entry from the top
        if StaffCourier.idle_grid:
            idle_pos = StaffCourier.idle_grid.pop(0)
        else:
            idle_pos = Vector2(1000, 100)  # Fallback position
        print(f"[Spawn] Assigned idle position {idle_pos} to StaffCourier {id}")
        super().__init__(id=id, position=entry_point, image_path="courier_staff.png", idle_position=idle_pos)
        self.type = "Courier_Staff"

class SubconCourier(Courier):
    idle_grid = []  # Define class-level grid for subcontract couriers

    def __init__(self, id):
        entry_point = Vector2(640, SCREEN_HEIGHT + 40)  # Enters from bottom
        if SubconCourier.idle_grid:
            idle_pos = SubconCourier.idle_grid.pop(0)
        else:
            idle_pos = Vector2(1000, 600)  # Fallback idle position
        print(f"[Spawn] Assigned idle position {idle_pos} to StaffCourier {id}")
        super().__init__(id=id, position=entry_point, image_path="courier_subcon.png", idle_position=idle_pos)
        self.type = "Courier_Subcon"
