"""Centralized logging configuration."""

import logging
import sys
from pathlib import Path

from backend.core.config import config, ROOT_DIR


def setup_logger(
    name: str = "document_assistant",
    level: str | None = None,
    log_file: str | None = None,
) -> logging.Logger:
    """Create and configure a logger instance."""
    log_config = config.logging
    level = level or log_config.get("level", "INFO")
    log_file = log_file or log_config.get("file")

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_path = ROOT_DIR / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
