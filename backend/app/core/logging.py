import logging
import sys
from backend.app.core.config import settings

def setup_logging():
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
