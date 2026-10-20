"""Configure one named logger without changing third-party root logging."""
import logging
from pathlib import Path
import time

from shared.utils.paths import LOG_DIR


def setup_logging(level: str = "INFO", log_dir: Path = LOG_DIR) -> logging.Logger:
    """Append UTC-stamped messages to a file and display them in the terminal.

    Reconfiguration replaces this logger's handlers to avoid duplicate messages.
    Call once at program startup. Never pass secrets or full response bodies to logs.
    """
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        raise ValueError("Unsupported logging level.")
    directory = Path(log_dir)
    directory.mkdir(parents=True, exist_ok=True)
    # Open the file first; preserve any existing logger if opening fails.
    file_handler = logging.FileHandler(directory / "research.log", encoding="utf-8")
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)sZ | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    formatter.converter = time.gmtime
    logger = logging.getLogger("authenticity")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    logger.setLevel(level)
    logger.propagate = False
    for handler in (console_handler, file_handler):
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
