import logging
import os
from pathlib import Path


# Vercel's deployment filesystem is read-only.
# /tmp is writable during a serverless invocation.
if os.getenv("VERCEL"):
    LOG_DIR = Path("/tmp")
else:
    LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)


LOG_FILE = LOG_DIR / "app.log"


logger = logging.getLogger("product_catalog_assistant")
logger.setLevel(logging.INFO)


if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Always log to stdout so Vercel can capture logs.
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Keep the local app.log behavior during normal local development.
    if not os.getenv("VERCEL"):
        file_handler = logging.FileHandler(
            LOG_FILE,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)