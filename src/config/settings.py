from os import getenv
from pathlib import Path
from dotenv import load_dotenv


ROOT_ENV = Path(__file__).resolve().parents[2]

if ROOT_ENV.exists():
    load_dotenv(dotenv_path=ROOT_ENV)

else:
    load_dotenv()


class Settings:
    GRID_SIZE = getenv("GRID_SIZE", -1)
    N_AGENTS = getenv("N_AGENTS", -1)
    
    APP_NAME = getenv("APP_NAME", "")
    APP_VERSION = getenv("APP_VERSION", "-1")

    ROOT_PATH = Path(__file__).resolve().parents[1]