from backend.app.ingestion.real_data_loader import RealDataLoader

def test_real_data_loader_csv_parsing():
    sample_csv = """timestamp,speed,soc,battery_temp,voltage,current
2026-10-24T08:00:00Z,0.0,85.0,25.0,400.0,0.0
2026-10-24T08:00:05Z,30.0,84.9,25.2,398.0,40.0
2026-10-24T08:00:10Z,60.0,84.7,25.5,395.0,80.0
"""
    result = RealDataLoader.load_csv_content(
        csv_text=sample_csv,
        vehicle_id="VIN-TEST-REAL-01",
        trip_id_prefix="TRIP-TEST-CSV"
    )
    assert result["imported_records"] > 0
    assert result["trips_detected"] == 1
    assert "vehicle_speed_kmh" in result["signals_detected"]
    assert "battery_soc_percent" in result["signals_detected"]
