import pygame
import random
from render import Renderer
from typing import TYPE_CHECKING
from simulation.fire import Fire
from simulation.wind import Wind
from settings.settings import Settings
from environment.wfc import WaveFunctionCollapse


if TYPE_CHECKING:
    from environment.terrain import Terrain


def _start_fire_random(fire: Fire, terrain: 'Terrain', grid_size: int) -> None:
    """Enciende una celda inflamable aleatoria del terreno."""

    candidates = [
        (col, row)
        for col in range(grid_size)
        for row in range(grid_size)
        if terrain.get_cell(row, col).is_flammable
    ]

    if candidates:
        x, y = random.choice(candidates)
        fire.ignite(x, y)


def main() -> None:
    settings = Settings()

    # --- 1. Generate world
    wfc = WaveFunctionCollapse(grid_size=settings.GRID_SIZE, seed=None)

    if not wfc.generate():
        print("No se pudo generar el terreno")
        return
    
    terrain = wfc.terrain

    # --- 2. Create simulation
    directions = [0, 45, 90, 180, 270]
    direction = random.choice(directions)
    print('Direction deg wind', direction)
    
    wind = Wind(direction_deg=direction, speed=1.5)
    fire = Fire(terrain, wind, seed=None)

    # --- 3. Render
    renderer = Renderer(settings)

    # --- 4. Game Loop
    running = True
    sim_timer_ms = 0
    fire_started = False

    while running:
        dt_ms = renderer.clock.get_time()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # regenerate world
                elif event.key == pygame.K_r:
                    wfc = WaveFunctionCollapse(grid_size=settings.GRID_SIZE, seed=None)

                    if wfc.generate():
                        terrain = wfc.terrain
                        fire = Fire(terrain, wind, seed=None)
                        fire_started = False
                
                elif event.key == pygame.K_SPACE:
                    if not fire_started:
                        _start_fire_random(fire, terrain, settings.GRID_SIZE)
                        fire_started = True
        
        # Update sim
        sim_timer_ms += dt_ms

        if fire_started and sim_timer_ms >= settings.SIM_TICK_MS:
            fire.step()
            sim_timer_ms = 0
        
        # Render
        renderer.draw(terrain)
        renderer.present()
        renderer.tick()
    
    pygame.quit()


if __name__ == '__main__':
    main()