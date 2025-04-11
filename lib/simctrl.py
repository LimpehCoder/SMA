import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spawner import spawn_vans, spawn_cars, spawn_staff, spawn_subcon, spawn_truck, CYCLE_TIMES
from pygame.math import Vector2
from objects.box import BoxPile  # Import BoxPile class from box module

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

class TruckController:
    def __init__(self, sorting_area):
        self.sorting_area = sorting_area
        self.active_truck = None
        self.last_day = None  # Used to detect day changes

    def update(self, dt, sim_clock):
        hour = sim_clock.hour
        minute = sim_clock.minute
        day = sim_clock.day

        # --- Reset truck state at 06:00 each day ---
        if hour == 6 and minute == 0 and day != self.last_day:
            print(f"[TruckController] Resetting state at {hour:02d}:{minute:02d} on {day}")
            self.sorting_area.spawned_cycles.clear()
            self.sorting_area.truck = None
            self.active_truck = None
            self.last_day = day

        # --- Spawn truck at scheduled cycle times ---
        for cycle_name in ["ACycle", "BCycle"]:
            if hour == CYCLE_TIMES[cycle_name] and cycle_name not in self.sorting_area.spawned_cycles:
                print(f"[TruckController] Spawning truck for {cycle_name} at hour {hour}")
                self.active_truck = spawn_truck(cycle_name)
                self.sorting_area.truck = self.active_truck
                self.sorting_area.spawned_cycles.add(cycle_name)

        # --- Update truck animation and delivery logic ---
        if self.active_truck:
            self.active_truck.update(dt)

            # Unload boxes into the BoxPile
            if self.active_truck.is_ready_to_unload():
                pile_position = Vector2(
                    self.active_truck.target_position.x + 40,
                    self.active_truck.target_position.y - 20
                )

                if not self.sorting_area.box_pile:
                    self.sorting_area.box_pile = BoxPile(position=pile_position)
                else:
                    self.sorting_area.box_pile.position = pile_position

                box_count = len(self.active_truck.boxes)
                self.sorting_area.box_pile.increment(count=box_count)
                self.sorting_area.boxes.extend(self.active_truck.boxes)
                self.active_truck.unload_all()
                print(f"[TruckController] Unloaded {box_count} boxes")

            # Remove truck if it's fully despawned
            if self.active_truck.is_ready_to_despawn():
                print("[TruckController] Truck has despawned.")
                self.sorting_area.truck = None
                self.active_truck = None

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

class CarController:
    def __init__(self, carpark):
        self.carpark = carpark
        self.spawned = False
        self.last_day = None  # Track day to allow reset

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
            spawn_cars(self.carpark.cars)
            self.spawned = True
            self.carpark.spawned_today = True

        # --- Animate car movement ---
        for car in self.carpark.cars:
            car.update(dt)

class CourierController:
    def __init__(self, sorting_area, carpark, courier_type):
        self.sorting_area = sorting_area
        self.carpark = carpark
        self.courier_type = courier_type  # "Courier_Staff" or "Courier_Subcon"
        self.spawned = False
        self.last_day = None

    def reset_daily_state(self, day):
        self.spawned = False
        self.sorting_area.spawned_today = False
        self.last_day = day

    def spawn(self, day):
        raise NotImplementedError("This method must be implemented by subclasses.")

    def stream_pending(self, dt):
        self.sorting_area.courier_spawn_timer += dt
        if self.sorting_area.pending_couriers and self.sorting_area.courier_spawn_timer >= self.sorting_area.courier_spawn_interval:
            next_courier = self.sorting_area.pending_couriers.pop(0)
            self.sorting_area.couriers.append(next_courier)
            self.sorting_area.courier_spawn_timer = 0

    def report(self, dt, sim_clock):
        hour, minute, day = sim_clock.hour, sim_clock.minute, sim_clock.day

        # Reset daily
        if hour == 6 and minute == 0 and day != self.last_day:
            self.reset_daily_state(day)
        # Spawn
        if hour == 7 and not self.spawned:
            self.spawn(day)
            self.spawned = True
        # Stream into scene
        self.stream_pending(dt)

        # Update all of this type
        for courier in self.sorting_area.couriers:
            if courier.type == self.courier_type:
                courier.update(dt)
       # Ensure idle couriers are positioned visually
        self.sorting_area.assign_idle_positions()  

    def manage_box_pickups(self):
        pile = self.sorting_area.box_pile
        for courier in self.sorting_area.couriers:
            if courier.type != self.courier_type:
                continue
            if courier.queue_index is not None or courier.status in ["Move_to_Queue", "Queuing"]:
                continue
            if courier.status in ["Idle", "Ready"] and pile:
                courier.request_slot(pile)

        for courier in self.sorting_area.couriers:
            if courier.type != self.courier_type:
                continue
            if courier.status == "QueuedIdle" and hasattr(courier, "queue_index"):
                if courier.queue_index == 0 and not pile.is_empty():
                    if (courier.position - courier.target_position).length() < 5:
                        courier.carrying.append("Box")
                        courier.status = "Carrying"
                        pile.decrement()
                        pile.occupied_slots[courier.queue_index] = None
                        courier.queue_index = None
                        self.shift_queue()

    def shift_queue(self):
        pile = self.sorting_area.box_pile
        for i in range(1, len(pile.occupied_slots)):
            courier = pile.occupied_slots[i]
            if courier and courier.type == self.courier_type:
                pile.occupied_slots[i] = None
                pile.occupied_slots[i - 1] = courier
                courier.queue_index = i - 1
                courier.target_position = pile.queue_slots[i - 1]

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

