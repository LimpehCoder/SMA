import pygame
import random
import os
from pygame.math import Vector2

IMAGE_CACHE = {}  # Cache to store loaded and scaled images
CYCLE_TIMES = {
    "ACycle": 8,
    "BCycle": 13,
    "NCycle": 18
}
def load_image(name, size=(32, 32)):
    path = os.path.join("..", "images", name)  # Resolve relative path to image

    if (name, size) in IMAGE_CACHE:
        return IMAGE_CACHE[(name, size)]  # Return cached version if already loaded

    if pygame.display.get_surface() is None:
        raise RuntimeError(f"Cannot load '{name}' before display is initialized.")  # Prevent loading before display

    raw_image = pygame.image.load(path).convert_alpha()  # Load image and preserve alpha channel
    scaled = pygame.transform.scale(raw_image, size)  # Resize image to desired size
    IMAGE_CACHE[(name, size)] = scaled  # Store scaled image in cache
    return scaled  # Return image

COURIER_ENTRY_POINT = pygame.Vector2(-50, 300)  # Starting position (offscreen)
COURIER_ENTRY_TARGET = pygame.Vector2(150, 300)  # Entry target position on screen

# --- Entity Classes ---







# --- Spawner Functions ---

def spawn_vehicles(vans_list, cars_list):
    vans_list.clear()  # Clear any previously spawned vans
    cars_list.clear()  # Clear any previously spawned cars
    spacing = 50  # Distance between vehicles in the grid

    left_x = 50  # X offset from the left edge of the screen
    top_y = 60  # Y offset from the top edge of the screen

    van_cols = 8  # Number of van columns
    van_rows = 5  # Number of van rows
    van_start_x = left_x  # Top-left starting X for vans
    van_start_y = top_y  # Top-left starting Y for vans

    # Create van grid (5 rows x 8 cols)
    for row in range(van_rows):
        for col in range(van_cols):
            x = van_start_x + col * spacing  # Calculate X position
            y = van_start_y + row * spacing  # Calculate Y position
            vans_list.append(Van(position=Vector2(x, y)))  # Spawn a Van and add to list

    car_cols = 8  # Number of car columns (same as vans)
    car_rows = 5  # Number of car rows
    gap = 50  # Vertical space between vans and cars
    car_start_x = left_x  # Top-left starting X for cars
    car_start_y = van_start_y + (van_rows * spacing) + gap  # Y below van grid

    # Create car grid (5 rows x 8 cols)
    for row in range(car_rows):
        for col in range(car_cols):
            x = car_start_x + col * spacing  # Calculate X position
            y = car_start_y + row * spacing  # Calculate Y position
            cars_list.append(Car(position=Vector2(x, y)))  # Spawn a Car and add to list

    print(f"Spawned {len(vans_list)} vans and {len(cars_list)} cars")  # Log how many vehicles were spawned

def spawn_couriers(day, available_vans, available_cars):
    result = []  # List of spawned couriers
    entry_point = Vector2(640, -40)  # Spawn point above screen center

    # Spawn 5 Courier_Staff and assign to vans
    for i in range(5):
        courier = Courier("Courier_Staff", f"S_{day}_{i}", position=entry_point.copy())  # Create new courier
        courier.scene = "SortingArea_Daily"  # Assign to sorting area scene
        if available_vans:  # If vans exist
            for van in available_vans:
                if not van.occupied:  # Find an available van
                    courier.assigned_vehicle = van  # Assign van to courier
                    van.occupied = True  # Mark van as taken
                    van.driver = courier  # Link courier to van
                    break
        result.append(courier)  # Add to result list

    # Spawn 3 Courier_Subcon and assign to cars
    for i in range(3):
        courier = Courier("Courier_Subcon", f"SC_{day}_{i}", position=entry_point.copy())  # Create new courier
        courier.scene = "SortingArea_Daily"  # Assign to sorting area
        if available_cars:  # If cars exist
            for car in available_cars:
                if not car.occupied:  # Find an available car
                    courier.assigned_vehicle = car  # Assign car to courier
                    car.occupied = True  # Mark car as taken
                    car.driver = courier  # Link courier to car
                    break
        result.append(courier)  # Add to result list
    return result  # Return the full list of couriers

def spawn_boxes(cycle, box_list):
    for i in range(20):  # 20 boxes per cycle
        box_list.append(Box(f"B_{cycle}_{len(box_list)+i}"))  # Assign unique ID and append to list