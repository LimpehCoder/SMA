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
    def generate_staff_idle_grid():
        return [
            Vector2(SCREEN_WIDTH - 50 - col * 40, 80 + row * 40)
            for row in range(3)
            for col in range(10)
        ]

    @staticmethod
    def generate_subcon_idle_grid():
        return [
            Vector2(SCREEN_WIDTH - 50 - col * 40, SCREEN_HEIGHT - 200 + row * 40)
            for row in range(3)
            for col in range(10)
        ]

    def reset_daily_state(self, day):
        self.spawned = False
        self.sorting_area.spawned_today = False
        self.last_day = day

        if self.courier_type == "Courier_Staff":
            StaffCourier.idle_grid = self.generate_staff_idle_grid()
        elif self.courier_type == "Courier_Subcon":
            SubconCourier.idle_grid = self.generate_subcon_idle_grid()

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
        if courier.queue_index == 0 and not self.sorting_area.box_pile.is_empty():
            if (courier.position - courier.target_position).length() < 5:
                courier.carrying.append("Box")
                courier.status = "SORTING"
                self.sorting_area.box_pile.decrement()
                self.sorting_area.box_pile.occupied_slots[courier.queue_index] = None
                courier.queue_index = None
                self.shift_queue()

    def _sorting(self, courier, dt):
        if courier.assigned_vehicle:
            courier.target_position = courier.assigned_vehicle.target_position
            if self._move_towards(courier, courier.target_position, dt):
                courier.assigned_vehicle.load_box()
                courier.carrying.clear()
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