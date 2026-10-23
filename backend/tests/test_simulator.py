from backend.app.simulation.generator import VehicleSimulator

def test_simulator_reproducibility():
    sim1 = VehicleSimulator(seed=123)
    sim2 = VehicleSimulator(seed=123)
    assert sim1.seed == sim2.seed

def test_dataset_generation_structure():
    sim = VehicleSimulator(vehicle_id="VIN-TEST-001", seed=999)
    res = sim.generate_comprehensive_dataset()
    assert "trips" in res
    assert "events" in res
    assert "dtcs" in res
    assert "telemetry" in res
    assert res["trips"] > 20
    assert res["events"] >= 4
    assert res["telemetry"] > 1000
