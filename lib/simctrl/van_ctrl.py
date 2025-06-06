import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spawner import spawn_vans, spawn_cars, spawn_staff, spawn_subcon, spawn_truck, CYCLE_TIMES
from pygame.math import Vector2
from objects.box import BoxPile  # Import BoxPile class from box module

class VanController:
    def __init__(self, carpark):
        self.carpark = carpark
        self.spawned = False
        self.last_day = None  # To track reset per new day

    def update(self, dt, sim_clock):
        hour = sim_clock.hour
        minute = sim_clock.minute
        day = sim_clock.day

        # --- Daily reset at 06:00 ---
        if hour == 6 and minute == 0 and day != self.last_day:
            self.spawned = False
            self.carpark.spawned_today = False
            self.last_day = day

        # --- Spawn on Monday 06:01 ---
        if day == "Monday" and hour == 6 and minute == 1 and not self.spawned:
            spawn_vans(self.carpark.vans)
            self.spawned = True
            self.carpark.spawned_today = True

        # --- Animate van movement ---
        for van in self.carpark.vans:
            van.update(dt)