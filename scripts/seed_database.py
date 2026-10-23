import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.simulation.generator import VehicleSimulator

def main():
    print(f"Initializing SQLite database at: {settings.DATABASE_PATH}...")
    init_db()
    sim = VehicleSimulator(vehicle_id=settings.SIMULATION_VEHICLE_ID, seed=settings.SIMULATION_SEED)
    counts = sim.generate_comprehensive_dataset()
    print("Database seeding completed successfully:")
    for k, v in counts.items():
        print(f"  • {k.capitalize()}: {v}")

if __name__ == "__main__":
    main()
