import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spawner import spawn_vans, spawn_cars, spawn_staff, spawn_subcon, spawn_truck, CYCLE_TIMES
from pygame.math import Vector2
from objects.box import BoxPile  # Import BoxPile class from box module

class CourierController:
    def __init__(self, sorting_area, carpark, courier_type):
        self.sorting_area = sorting_area  # Reference to the sorting area scene
        self.carpark = carpark  # Reference to the carpark scene
        self.courier_type = courier_type  # Type of courier: "Courier_Staff" or "Courier_Subcon"
        self.spawned = False  # Whether couriers have been spawned today
        self.last_day = None  # Last day spawn was triggered

    def reset_daily_state(self, day):
        self.spawned = False  # Reset spawn flag
        self.sorting_area.spawned_today = False  # Reset sorting area's spawn flag
        self.last_day = day  # Update the last spawn day

    def spawn(self, day):
        raise NotImplementedError("This method must be implemented by subclasses.")

    def stream_pending(self, dt):
        self.sorting_area.courier_spawn_timer += dt
        if self.sorting_area.pending_couriers and self.sorting_area.courier_spawn_timer >= self.sorting_area.courier_spawn_interval:
            next_courier = self.sorting_area.pending_couriers.pop(0)
            next_courier.status = "Reporting"  # Initial individual state
            self.sorting_area.couriers.append(next_courier)
            self.sorting_area.courier_spawn_timer = 0

    def report(self, dt, sim_clock):
        hour, minute, day = sim_clock.hour, sim_clock.minute, sim_clock.day

        if not self.sorting_area.couriers:
            self.sorting_area.system_state = "Off_Work"
        else:
            self.sorting_area.system_state = "Active"

        if hour == 6 and minute == 0 and day != self.last_day:
            self.reset_daily_state(day)

        if hour == 7 and not self.spawned:
            self.spawn(day)
            self.spawned = True

        self.stream_pending(dt)

        for courier in self.sorting_area.couriers:
            if courier.type != self.courier_type:
                continue

            if courier.status == "Reporting":
                courier.status = "Forming"
                courier.grid_assigned = False

            elif courier.status == "Forming" and not courier.grid_assigned:
                self.sorting_area.assign_idle_positions()

            elif courier.status == "Ready":
                courier.status = "Idle"

            elif courier.status == "Idle" and self.sorting_area.box_pile:
                courier.status = "Move_to_Queue"

            elif courier.status == "Move_to_Queue" and courier.queue_index is not None:
                courier.status = "Queuing"

            elif courier.status == "Sorting":
                courier.target_position = self.sorting_area.door_to_carpark_rect.center

            courier.update(dt)

class StaffController(CourierController):
    def __init__(self, sorting_area, carpark):
        super().__init__(sorting_area, carpark, courier_type="Courier_Staff")

    def spawn(self, day):
        staff = spawn_staff(day, self.carpark.vans)
        self.sorting_area.pending_couriers += staff

class SubconController(CourierController):
    def __init__(self, sorting_area, carpark):
        super().__init__(sorting_area, carpark, courier_type="Courier_Subcon")

    def spawn(self, day):
        subcons = spawn_subcon(day, self.carpark.cars)
        self.sorting_area.pending_couriers += subcons