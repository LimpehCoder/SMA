import pygame
import random
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pygame.math import Vector2

from objects.courier import Courier, StaffCourier, SubconCourier  # Import Courier class from courier module
from objects.van import Van
from objects.car import Car  # Import vehicle classes from vehicles module
from objects.box import Box  # Import Box class from box module
from objects.truck import Truck  # Import Truck class from truck module

CYCLE_TIMES = {
    "ACycle": 8,
    "BCycle": 13,
    "NCycle": 18
}

COURIER_ENTRY_POINT = pygame.Vector2(-50, 300)  # Starting position (offscreen)
COURIER_ENTRY_TARGET = pygame.Vector2(150, 300)  # Entry target position on screen
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720  # Dimensions used throughout the GUI

# --- Spawner Functions ---

def spawn_vans(vans_list):
    vans_list.clear()
    spacing = 50
    right_x = SCREEN_WIDTH - 50
    top_y = 60

    van_cols = 8
    van_rows = 5
    van_start_x = right_x
    van_start_y = top_y

    for row in range(van_rows):
        for col in range(van_cols):
            x = van_start_x - col * spacing
            y = van_start_y + row * spacing
            vans_list.append(Van(position=Vector2(x, y)))

    print(f"Spawned {len(vans_list)} vans")

def spawn_cars(cars_list):
    cars_list.clear()
    spacing = 50
    right_x = SCREEN_WIDTH - 50
    top_y = 60

    car_cols = 8
    car_rows = 5
    gap = 50
    car_start_x = right_x
    car_start_y = top_y + (5 * spacing) + gap  # below the vans

    for row in range(car_rows):
        for col in range(car_cols):
            x = car_start_x - col * spacing
            y = car_start_y + row * spacing
            cars_list.append(Car(position=Vector2(x, y)))

    print(f"Spawned {len(cars_list)} cars")

def spawn_staff(day, available_vans):
    result = []
    entry_point = Vector2(640, -40)
    for i in range(5):
        courier = StaffCourier(f"S_{day}_{i}")

        courier.scene = "SortingArea_Daily"
        if available_vans:
            for van in available_vans:
                if not van.occupied:
                    courier.assigned_vehicle = van
                    van.occupied = True
                    van.driver = courier
                    break
        result.append(courier)
    return result

def spawn_subcon(day, available_cars):
    result = []
    entry_point = Vector2(640, -40)
    for i in range(3):
        courier = SubconCourier(f"SC_{day}_{i}")
        courier.scene = "SortingArea_Daily"
        if available_cars:
            for car in available_cars:
                if not car.occupied:
                    courier.assigned_vehicle = car
                    car.occupied = True
                    car.driver = courier
                    break
        result.append(courier)
    return result

def spawn_truck(cycle_name):
    start_y = 300  # Y-position where the truck will enter horizontally
    return Truck(start_y=start_y, cycle_name=cycle_name)