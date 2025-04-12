import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spawner import spawn_vans, spawn_cars, spawn_staff, spawn_subcon, spawn_truck, CYCLE_TIMES
from pygame.math import Vector2
from spawner import spawn_staff, spawn_subcon
from objects.courier import StaffCourier, SubconCourier

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

class CourierController:
    def __init__(self, sorting_area, carpark, courier_type):
        self.sorting_area = sorting_area
        self.carpark = carpark
        self.courier_type = courier_type  # "Courier_Staff" or "Courier_Subcon"
        self.spawned = False
        self.last_day = None

        # State definitions
        self.states = {
            "OFF_WORK": self._off_work,
            "REPORTING": self._reporting,
            "IDLE": self._idle,
            "MOVE_TO_QUEUE": self._move_to_queue,
            "QUEUING": self._queuing,
            "SORTING": self._sorting,
            "LOADING": self._sorting,  # Same as sorting for now
            "DELIVERING": self._delivering  # Optional future state
        }

    @staticmethod
    def initialize_idle_grids():
        StaffCourier.idle_grid = [
            Vector2(SCREEN_WIDTH - 50 - col * 40, 80 + row * 40)
            for row in range(3) for col in range(10)
        ]
        SubconCourier.idle_grid = [
            Vector2(SCREEN_WIDTH - 50 - col * 40, SCREEN_HEIGHT - 200 + row * 40)
            for row in range(3) for col in range(10)
        ]

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

        if hour == 6 and minute == 0 and day != self.last_day:
            self.reset_daily_state(day)

        if hour == 7 and not self.spawned:
            self.spawn(day)
            self.spawned = True

        self.stream_pending(dt)

        for courier in self.sorting_area.couriers:
            if courier.type == self.courier_type:
                self.states.get(courier.status, self._off_work)(courier, dt)

    def _off_work(self, courier, dt):
        pass

    def _reporting(self, courier, dt):
        if self._move_towards(courier, courier.idle_position, dt):
            courier.status = "IDLE"

    def _idle(self, courier, dt):
        pile = self.sorting_area.box_pile
        if pile and courier.queue_index is None:
            courier.request_slot(pile)
            courier.status = "MOVE_TO_QUEUE"

    def _move_to_queue(self, courier, dt):
        if self._move_towards(courier, courier.target_position, dt):
            courier.status = "QUEUING"

    def _queuing(self, courier, dt):
        pile = self.sorting_area.box_pile

        # Only allow specific courier types in specific priority slots
        if courier.queue_index not in [0, 1, 2]:
            return  # Not a high-priority slot

        if (courier.position - courier.target_position).length() < 5:
            # Ensure pickup happens in R0 → T0 → B0 order
            pickup_priority = [0, 1, 2]
            for slot_index in pickup_priority:
                slot_courier = pile.occupied_slots[slot_index]
                if slot_courier == courier and not pile.is_empty():
                    # Pickup logic
                    for _ in range(5):  # Pick up 5 boxes
                        if not pile.is_empty():
                            courier.pickup_box(pile)
                    courier.status = "SORTING"
                    pile.occupied_slots[slot_index] = None
                    courier.queue_index = None
                    self.shift_queue()
                    break  # Only allow one courier pickup per update frame

    def shift_queue(self):
        pile = self.sorting_area.box_pile
        total = len(pile.occupied_slots)

        # Each row has 10 slots; determine starting indices for T and B
        R_start, T_start, B_start = 0, 10, 20
        row_size = 10

        def shift_row(start_index):
            # Only shift if the front slot is empty
            if pile.occupied_slots[start_index] is None:
                for i in range(start_index + 1, start_index + row_size):
                    courier = pile.occupied_slots[i]
                    if courier and courier.type == self.courier_type:
                        # Shift forward
                        pile.occupied_slots[i] = None
                        pile.occupied_slots[i - 1] = courier
                        courier.queue_index = i - 1
                        courier.target_position = pile.queue_slots[i - 1]

        # Shift each row independently
        shift_row(R_start)
        shift_row(T_start)
        shift_row(B_start)


    def _sorting(self, courier, dt):
        if courier.assigned_vehicle:
            courier.target_position = courier.assigned_vehicle.target_position
            if self._move_towards(courier, courier.target_position, dt):
                courier.assigned_vehicle.load_box()
                courier.carrying = 0
                courier.status = "IDLE"

    def _delivering(self, courier, dt):
        pass

    def _move_towards(self, courier, target, dt):
        direction = target - courier.position
        if direction.length() < 2:
            courier.position = target
            return True
        direction.normalize_ip()
        courier.position += direction * courier.speed * (dt / 1000.0)
        return False

class StaffController(CourierController):
    def __init__(self, sorting_area, carpark):
        super().__init__(sorting_area, carpark, courier_type="Courier_Staff")

    def spawn(self, day):
        staff = spawn_staff(day, self.carpark.vans)
        for courier in staff:
            courier.status = "REPORTING"
        self.sorting_area.pending_couriers += staff

class SubconController(CourierController):
    def __init__(self, sorting_area, carpark):
        super().__init__(sorting_area, carpark, courier_type="Courier_Subcon")

    def spawn(self, day):
        subcons = spawn_subcon(day, self.carpark.cars)
        for courier in subcons:
            courier.status = "REPORTING"
        self.sorting_area.pending_couriers += subcons