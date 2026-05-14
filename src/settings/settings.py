from os import getenv
from pathlib import Path
from dotenv import load_dotenv


ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(dotenv_path=None if not ROOT_ENV.exists() else ROOT_ENV)

class Settings:
    GRID_SIZE = getenv("GRID_SIZE", -1)
    N_AGENTS = getenv("N_AGENTS", -1)

    ROOT_PATH = Path(__file__).resolve().parents[1]