from os import getenv
from pathlib import Path
from dotenv import load_dotenv


ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(dotenv_path=None if not ROOT_ENV.exists() else ROOT_ENV)


class Settings:
    N_AGENTS: int = -1

    # --- GRID ---
    GRID_SIZE: int = 48
    CELL_PX = 8

    # --- Windows ---
    WINDOW_W = GRID_SIZE * CELL_PX
    WINDOW_H = GRID_SIZE * CELL_PX
    FPS = 30
    TITLE = "Fire Simulator"

    # --- Simulation ---
    SIM_TICK_MS        = 200    # ms entre ticks de simulación
    FIRE_BURN_DURATION = 8      # ticks que una celda arde antes de quemarse
    FIRE_SPREAD_PROB   = 0.25    # probabilidad base de propagación por tick
    WIND_INFLUENCE     = 0.4   # cuánto amplifica el viento la probabilidad

    # --- Colors (R, G, B) ---
    # Se usan como fallback si PatternRegistry no tiene color para un tipo
    COLOR_FALLBACK   = (80, 80, 80)
    COLOR_BURNING    = (220, 80, 10)
    COLOR_SMOLDERING = (160, 40, 10)
    COLOR_BURNED     = (30, 20, 10)

    

    ROOT_PATH = Path(__file__).resolve().parents[1]

    @classmethod
    def get_setting(cls: 'Settings', const: str) -> any:
        return getattr(cls, const, None)