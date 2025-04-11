class Courier:
    def __init__(self, courier_type, id, position=None):
        self.type = courier_type  # "Courier_Staff" or "Courier_Subcon"
        self.id = id  # Unique ID string like "S_Monday_0"
        self.status = "Entering"  # Initial status, used for animation state
        self.position = position or COURIER_ENTRY_POINT.copy()  # Starting position (off-screen by default)
        self.carrying = []  # List of boxes currently held by the courier
        self.shift = None  # Placeholder for shift assignment (e.g., ACycle, BCycle)
        self.speed = 300  # Movement speed in pixels per second
        self.target_position = pygame.Vector2(0, 0)  # Position the courier will move toward
        self.grid_assigned = False  # Has the courier been assigned a final idle location?

        if courier_type == "Courier_Staff":
            self.image = load_image("courier_staff.png", (32, 32))  # Load the staff sprite
        else:
            self.image = load_image("courier_subcon.png", (32, 32))  # Load the subcontractor sprite

    def update(self, dt):
        if self.status in ["Entering", "Forming"]:  # Only animate if in movement states
            direction = self.target_position - self.position  # Vector to destination
            distance = direction.length()  # Length of that vector

            if distance < 2:  # Close enough to consider arrival
                if self.status == "Entering":
                    self.status = "Idle"  # Arrived in staging area
                elif self.status == "Forming":
                    self.status = "Ready"  # Finished forming into grid
            else:
                direction.normalize_ip()  # Normalize to unit vector
                self.position += direction * self.speed * (dt / 1000.0)  # Move based on speed and delta time

    def render(self, screen):
        screen.blit(self.image, self.position)  # Draw courier at current position