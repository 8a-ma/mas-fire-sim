from settings.settings import Settings
from simulation.simulation import Simulation


if __name__ == '__main__':
    settings = Settings()
    Simulation(settings).run()