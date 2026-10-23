import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "VehicleGPT"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Edge profile: constrained (2GB RAM / 2 ARM cores), development, vehicle_hpc
    HARDWARE_PROFILE: Literal["constrained", "development", "vehicle_hpc"] = "development"

    # Database
    DATABASE_PATH: str = str(BASE_DIR / "data" / "vehiclegpt.db")
    DB_TIMEOUT_SECONDS: float = 15.0
    DB_ENABLE_WAL: bool = True

    # Retention Tiers
    RETENTION_HOT_HOURS: int = 72       # Raw high-frequency (10Hz / 1Hz)
    RETENTION_WARM_DAYS: int = 7        # Downsampled 1-second interval
    RETENTION_COLD_WEEKS: int = 12      # Downsampled 1-minute interval
    RETENTION_DTC_MONTHS: int = 6       # Diagnostic fault codes

    # Vehicle Simulation
    SIMULATION_VEHICLE_ID: str = "VIN-TATA-EV-2026-X01"
    SIMULATION_SEED: int = 42
    SIMULATION_AUTO_START: bool = True
    SIMULATION_INTERVAL_MS: int = 1000

    # Local SLM (llama.cpp)
    LLM_MODEL_PATH: str = str(BASE_DIR / "models" / "Llama-3.2-1B-Instruct-Q4_K_M.gguf")
    LLM_CONTEXT_SIZE: int = 2048
    LLM_MAX_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.1
    LLM_ENABLE_FALLBACK: bool = True

    # Safety & Privacy Constraints
    READ_ONLY_VEHICLE_BUS: bool = True
    BLOCK_ACTUATOR_COMMANDS: bool = True
    ALLOW_CLOUD_APIS: bool = False
    TIMEZONE: str = "Asia/Kolkata"

settings = Settings()

# Ensure directories exist
os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)
os.makedirs(str(BASE_DIR / "models"), exist_ok=True)
os.makedirs(str(BASE_DIR / "sample_data"), exist_ok=True)
