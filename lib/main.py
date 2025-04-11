import pygame
import random
import math
import os
from collections import deque
from enum import Enum
import pygame_gui

# --- Import core components from simctrl.py ---
from simctrl import SceneManager, SimulationClock, SimulationController
from scenes import sortingarea_scene, carpark_scene, citydistrict_scene, control_panel_stats

# Initialize scenes and controller
scene_manager = SceneManager()
carpark = carpark_scene.CarparkScene()
sorting_area_scene = sortingarea_scene.SortingAreaScene(carpark)
controller = SimulationController(sorting_area_scene, carpark)

# Initialize Pygame and simulation window
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
sim_clock = SimulationClock()

# Screen and simulation constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60
VAN_CAPACITY = 50
CAR_CAPACITY = 50
CYCLE_TIMES = {
    "ACycle": 8,
    "BCycle": 13,
    "NCycle": 18
}
WORKDAY_START = 6
WORKDAY_END = 22
SPRITE_PATH = "assets/sprites/"
HOUSE_GRID = [(x, y) for x in range(0, 900, 30) for y in range(0, 900, 30)]

# Register scenes
scene_manager.add_scene("Carpark", carpark_scene)
scene_manager.add_scene("SortingArea_Daily", sorting_area_scene)
scene_manager.add_scene("City_District1", citydistrict_scene.CityDistrictScene(1))
scene_manager.add_scene("City_District2", citydistrict_scene.CityDistrictScene(2))
scene_manager.add_scene("City_District3", citydistrict_scene.CityDistrictScene(3))
scene_manager.add_scene("Statistics", control_panel_stats.StatisticsScene())
scene_manager.switch_scene("Carpark")

# UI Manager and scene buttons
ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

button_sorting = pygame_gui.elements.UIButton(pygame.Rect((20, 640), (180, 40)), 'Sorting Area', ui_manager)
button_carpark = pygame_gui.elements.UIButton(pygame.Rect((220, 640), (180, 40)), 'Carpark', ui_manager)
button_city1 = pygame_gui.elements.UIButton(pygame.Rect((420, 640), (180, 40)), 'City District 1', ui_manager)
button_city2 = pygame_gui.elements.UIButton(pygame.Rect((620, 640), (180, 40)), 'City District 2', ui_manager)
button_city3 = pygame_gui.elements.UIButton(pygame.Rect((820, 640), (180, 40)), 'City District 3', ui_manager)
button_stats = pygame_gui.elements.UIButton(pygame.Rect((1020, 640), (180, 40)), 'Statistics', ui_manager)

# Simulation flags
isNPI = False
isSurge = False
current_canvas = "Carpark"

# Entity trackers
all_couriers = []
all_vehicles = []
all_boxes = []
undelivered_boxes = deque()
stat_tracker = {}

# Main game loop
running = True
while running:
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                scene_manager.switch_scene("SortingArea_Daily")
            elif event.key == pygame.K_2:
                scene_manager.switch_scene("Carpark")
            elif event.key == pygame.K_3:
                scene_manager.switch_scene("City_District1")
            elif event.key == pygame.K_4:
                scene_manager.switch_scene("City_District2")
            elif event.key == pygame.K_5:
                scene_manager.switch_scene("City_District3")
            elif event.key == pygame.K_6:
                scene_manager.switch_scene("Statistics")

        ui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button_sorting:
                scene_manager.switch_scene("SortingArea_Daily")
            elif event.ui_element == button_carpark:
                scene_manager.switch_scene("Carpark")
            elif event.ui_element == button_city1:
                scene_manager.switch_scene("City_District1")
            elif event.ui_element == button_city2:
                scene_manager.switch_scene("City_District2")
            elif event.ui_element == button_city3:
                scene_manager.switch_scene("City_District3")
            elif event.ui_element == button_stats:
                scene_manager.switch_scene("Statistics")

        scene_manager.handle_event(event)

    # Run simulation
    sim_clock.update(dt)
    controller.update(dt, sim_clock)  # SimulationController now drives all logic
    scene_manager.update(dt, sim_clock)
    ui_manager.update(dt / 1000.0)

    # Draw scene
    scene_manager.render(screen)

    font = pygame.font.SysFont("Arial", 24)
    time_text = font.render(sim_clock.get_time_str(), True, (255, 255, 255))
    scene_text = font.render(f"Scene: {scene_manager.current_scene}", True, (255, 255, 255))
    screen.blit(time_text, (20, 20))
    screen.blit(scene_text, (20, 50))

    ui_manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()