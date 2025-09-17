# app/core/logging.py
import logging
import sys
from app.core.config import settings

def setup_logging():
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = []
    root.addHandler(handler)
