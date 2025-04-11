import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spawner import spawn_vehicles, spawn_couriers, spawn_truck, CYCLE_TIMES
from pygame.math import Vector2
from box import BoxPile  # Import BoxPile class from box module

class SceneManager:
    def __init__(self):
        self.current_scene = None  # Currently active scene name
        self.scenes = {}  # Dictionary to hold all scenes

    def add_scene(self, name, scene):
        self.scenes[name] = scene  # Add a scene to the dictionary
        if self.current_scene is None:
            self.current_scene = name  # Set the first added scene as default

    def switch_scene(self, name):
        if name in self.scenes:
            self.current_scene = name  # Switch the active scene

    def handle_event(self, event):
        if self.current_scene:
            self.scenes[self.current_scene].handle_event(event)  # Forward events to current scene
    
    def handle_event_all(self, event):
        for scene in self.scenes.values():
            scene.handle_event(event)
    
    def update_all(self, dt, clock):
        for scene in self.scenes.values():
            scene.update(dt, clock)  # Update all scenes, not just the current one

    def render(self, screen):
        if self.current_scene:
            self.scenes[self.current_scene].render(screen)  # Render only the current scene

class SimulationClock:
    def __init__(self):
        self.day = "Monday"
        self.hour = 6
        self.minute = 0
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.speed_multiplier = 1  # Multiplier to speed up or slow down time

    def update(self, dt):
        self.minute += int((dt / 1000.0) * self.speed_multiplier * 60)  # Convert real time to sim minutes
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1
        while self.hour >= 24:
            self.hour = 0
            current_day_index = self.days.index(self.day)
            self.day = self.days[(current_day_index + 1) % len(self.days)]  # Loop to next day

    def get_time_str(self):
        return f"{self.day} {self.hour:02d}:{self.minute:02d}"  # String for display

class SimulationController:
    def __init__(self, sorting_area, carpark):
        self.sorting_area = sorting_area  # Reference to SortingAreaScene
        self.carpark = carpark  # Reference to CarparkScene
        self.couriers_spawned = False
        self.vehicles_spawned = False
        self.spawned_cycles = set()  # Tracks which box cycles have run

    def shift_courier_queue(self, box_pile):
        for i in range(1, len(box_pile.occupied_slots)):
            courier = box_pile.occupied_slots[i]
            if courier:
                box_pile.occupied_slots[i] = None
                box_pile.occupied_slots[i - 1] = courier
                courier.queue_index = i - 1
                courier.target_position = box_pile.queue_slots[i - 1]

    def update(self, dt, sim_clock):
        hour = sim_clock.hour
        minute = sim_clock.minute
        day = sim_clock.day

        # --- Reset daily states at 06:00 ---
        if hour == 6 and minute == 0:
            self.couriers_spawned = False
            self.vehicles_spawned = False  # Optional: Reset only on Monday?
            self.sorting_area.spawned_today = False
            self.sorting_area.spawned_cycles.clear()
            self.carpark.spawned_today = False

        # --- Spawn vehicles once on Monday at 06:01 ---
        if day == "Monday" and hour == 6 and minute == 1 and not self.vehicles_spawned:
            spawn_vehicles(self.carpark.vans, self.carpark.cars)
            self.vehicles_spawned = True
            self.carpark.spawned_today = True

        # --- Spawn couriers daily at 07:00 ---
        if hour == 7 and not self.couriers_spawned:
            self.sorting_area.pending_couriers = spawn_couriers(day, self.carpark.vans, self.carpark.cars)
            self.sorting_area.spawned_today = True
            self.couriers_spawned = True

        # --- Stream couriers one by one ---
        self.sorting_area.courier_spawn_timer += dt
        if self.sorting_area.pending_couriers and self.sorting_area.courier_spawn_timer >= self.sorting_area.courier_spawn_interval:
            next_courier = self.sorting_area.pending_couriers.pop(0)
            self.sorting_area.couriers.append(next_courier)
            self.sorting_area.courier_spawn_timer = 0

        # --- Spawn truck at scheduled cycle times ---
        for cycle_name in ["ACycle", "BCycle"]:
            if hour == CYCLE_TIMES[cycle_name] and cycle_name not in self.sorting_area.spawned_cycles:
                self.sorting_area.truck = spawn_truck(cycle_name)  # Create and store truck in sorting area
                self.sorting_area.spawned_cycles.add(cycle_name)  # Prevent re-spawn for the same cycle

        # --- Continue updating all entities globally ---
        for courier in self.sorting_area.couriers:
            courier.update(dt)

        for van in self.carpark.vans:
            van.update(dt)

        for car in self.carpark.cars:
            car.update(dt)

        if self.sorting_area.truck:
            self.sorting_area.truck.update(dt)
            # Drop boxes into the sorting area once truck arrives
            if self.sorting_area.truck.is_ready_to_unload():
                pile_position = Vector2(
                    self.sorting_area.truck.target_position.x + 40,
                    self.sorting_area.truck.target_position.y - 20
                )

                # Create a new BoxPile only if one doesn't exist
                if not self.sorting_area.box_pile:
                    self.sorting_area.box_pile = BoxPile(position=pile_position)
                else:
                    # Optional: if truck pulls up to a new position, update pile location
                    self.sorting_area.box_pile.position = pile_position
                # Increment the box pile count cumulatively
                self.sorting_area.box_pile.increment(count=len(self.sorting_area.truck.boxes))
                # Add boxes to the global box list (e.g., for courier access or rendering)
                self.sorting_area.boxes.extend(self.sorting_area.truck.boxes)
                # Trigger the truck to depart
                self.sorting_area.truck.unload_all()


            if self.sorting_area.truck.is_ready_to_despawn():
                self.sorting_area.truck = None
        # --- Maintain idle grid positions ---
        self.sorting_area.assign_idle_positions()

        for courier in self.sorting_area.couriers:
            courier.update(dt)

            if courier.status in ["Idle", "Ready"] and self.sorting_area.box_pile:
                courier.request_slot(self.sorting_area.box_pile)

            if courier.status == "QueuedIdle" and hasattr(courier, "queue_index"):
                if courier.queue_index == 0 and not self.sorting_area.box_pile.is_empty():
                    # Attempt pickup
                    distance = (courier.position - courier.target_position).length()
                    if distance < 5:
                        courier.carrying.append("Box")
                        courier.status = "Carrying"
                        self.sorting_area.box_pile.decrement()
                        self.sorting_area.box_pile.occupied_slots[courier.queue_index] = None
                        courier.queue_index = None
                        self.shift_courier_queue(self.sorting_area.box_pile)
        
        for courier in self.sorting_area.couriers:
            if self.sorting_area.door_to_carpark_rect.collidepoint(courier.position):
                print(f"{courier.id} is teleporting to Carpark.")
                self.couriers.remove(courier)
                self.carpark.receive_courier(courier)
                
        for courier in self.sorting_area.couriers[:]:
            if self.sorting_area.door_to_carpark_rect.collidepoint(courier.position):
                print(f"{courier.id} teleports to Carpark")
                self.sorting_area.couriers.remove(courier)
                self.carpark.receive_courier(courier)




