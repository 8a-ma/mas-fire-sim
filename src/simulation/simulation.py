import pygame
import random
import numpy as np
from render import Renderer
from simulation.wind import Wind
from simulation.fire import Fire
from simulation.engine import Engine
from settings.settings import Settings
from typing import TYPE_CHECKING, List
from settings.event_logger import EventLogger
from environment.wfc import WaveFunctionCollapse
from simulation.agents.base_agents import BaseAgent
from simulation.agents.drone_agent import DroneAgent


if TYPE_CHECKING:
    from environment.terrain import Terrain


class Simulation:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._logger = EventLogger()
        self._renderer = Renderer(settings)

        self._fire_started = False
        self._sim_timer_ms = 0

        self._wfc: WaveFunctionCollapse | None = None
        self._terrain: 'Terrain' | None = None

        self._wind: Wind | None = None
        self._fire: Fire | None = None

        self._agents: List[BaseAgent | None] = []
        self._engine: Engine | None = None

        self._build_world()
        self._build_agents()
    
    def run(self) -> None:
        """Game loop"""
        running = True

        while running:
            dt_ms = self._renderer.clock.get_time()

            running = self._handle_events()
        
            # Update
            self._update(dt_ms)

            # Render
            self._render()

            # Tick
            # self._renderer.tick()
        
        pygame.quit()

    def _build_world(self) -> None:
        # --- 1. Generate world
        self._wfc = WaveFunctionCollapse(grid_size=self._settings.GRID_SIZE, seed=None)

        if not self._wfc.generate(): return

        self._terrain = self._wfc.terrain

        directions = [0, 90, 180, 270]
        direction, speed = random.choice(directions), round(random.uniform(0.0, 2.0), 1)
    
        self._wind = Wind(direction, speed=speed)
        self._fire = Fire(self._terrain, self._wind, seed=None)
    
    def _build_agents(self) -> None:
        """Instancia los agentes según configuración."""

        self._agents = []

        for i in range(self._settings.N_AGENTS):
            self._agents.append(DroneAgent(
                i,
                np.array([random.randint(0, self._terrain.grid_size - 1), random.randint(0, self._terrain.grid_size - 1)])
            ))

        self._engine = Engine(
            self._terrain,
            self._fire,
            self._wind,
            self._agents,
            self._logger
        )

    def _start_fire_random(self) -> None:
        """Enciende una celda inflamable aleatoria del terreno."""

        candidates = [
            (col, row)
            for col in range(self._terrain.grid_size)
            for row in range(self._terrain.grid_size)
            if self._terrain.get_cell(row, col).is_flammable
        ]

        if candidates:
            x, y = random.choice(candidates)
            self._fire.ignite(x, y)
    
    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return False

                # Regenrate world
                elif event.key == pygame.K_r:
                    self._reset_world()
                
                # Ignition
                elif event.key == pygame.K_SPACE:
                    self._ignite_fire()
        
        return True
    
    def _reset_world(self) -> None:
        self._wfc = WaveFunctionCollapse(grid_size=self._settings.GRID_SIZE, seed=None)

        if self._wfc.generate():
            self._terrain = self._wfc.terrain
            self._fire = Fire(self._terrain, self._wind, seed=None)
            self._fire_started = False
            self._build_agents()
    
    def _ignite_fire(self) -> None:
        if not self._fire_started:
            self._start_fire_random()
            self._fire_started = True

    def _update(self, dt_ms: int) -> None:
        self._sim_timer_ms += dt_ms

        if self._fire_started and self._sim_timer_ms >= self._settings.SIM_TICK_MS:
            self._fire.step()
            self._engine.step()
            self._sim_timer_ms = 0

    def _render(self) -> None:
        self._renderer.draw(self._terrain, self._agents)
        self._renderer.present() # dirty_rects punto 4
        self._renderer.tick()