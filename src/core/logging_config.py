# src/core/logging_config.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


def setup_logging(
    *,
    level: str = "INFO",
    log_file: Optional[Path] = None,
    quiet: bool = False,
) -> None:
    """
    Configure root logging for the application.

    - Console handler (stderr) by default
    - Optional file handler (UTF-8)
    - Friendly format with timestamps + logger name + level
    """
    # Normalize level
    level_name = level.upper().strip()
    numeric_level = getattr(logging, level_name, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level!r} (use DEBUG/INFO/WARNING/ERROR)")

    handlers: list[logging.Handler] = []

    if not quiet:
        console = logging.StreamHandler()
        console.setLevel(numeric_level)
        console.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        handlers.append(console)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        handlers.append(file_handler)

    # If quiet=True and no log_file -> still configure logging to avoid "No handlers" warnings
    if not handlers:
        handlers.append(logging.NullHandler())

    # IMPORTANT: force=True to override any prior basicConfig (useful in scripts/tests)
    logging.basicConfig(level=numeric_level, handlers=handlers, force=True)
