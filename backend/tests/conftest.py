import pytest
import os
import sys
import tempfile
from fastapi.testclient import TestClient

# Ensure workspace root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.core.config import settings
from backend.app.core.database import init_db, get_db
from backend.app.simulation.generator import VehicleSimulator
from backend.app.main import app

@pytest.fixture(scope="session", autouse=True)
def test_db_setup():
    """Setup a dedicated test database."""
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_vehiclegpt.db")
    settings.DATABASE_PATH = test_db_path
    
    init_db()
    sim = VehicleSimulator(vehicle_id="VIN-TATA-EV-2026-X01", seed=42)
    sim.generate_comprehensive_dataset()

    yield test_db_path

    # Cleanup
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass

@pytest.fixture
def client():
    """FastAPI TestClient instance."""
    with TestClient(app) as c:
        yield c
