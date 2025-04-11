from lib.spawner import spawn_vehicles, spawn_couriers, spawn_boxes, CYCLE_TIMES

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

    def update(self, dt, clock):
        if self.current_scene:
            self.scenes[self.current_scene].update(dt, clock)  # Update only the current scene

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

        # --- Spawn boxes at scheduled times ---
        for cycle_name in ["ACycle", "BCycle"]:
            if hour == CYCLE_TIMES[cycle_name] and cycle_name not in self.sorting_area.spawned_cycles:
                spawn_boxes(cycle_name, self.sorting_area.boxes)
                self.sorting_area.spawned_cycles.add(cycle_name)

        # --- Continue updating all entities globally ---
        for courier in self.sorting_area.couriers:
            courier.update(dt)

        for van in self.carpark.vans:
            van.update(dt)

        for car in self.carpark.cars:
            car.update(dt)

        # --- Maintain idle grid positions ---
        self.sorting_area.assign_idle_positions()

