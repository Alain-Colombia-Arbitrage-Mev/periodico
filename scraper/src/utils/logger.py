"""
Logging configuration for the scraper
"""
import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "100 MB",
    retention: str = "30 days"
) -> None:
    """
    Configure loguru logger

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (optional)
        rotation: When to rotate log file
        retention: How long to keep old log files
    """
    # Remove default logger
    logger.remove()

    # Console logging with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # File logging if path provided
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            enqueue=True  # Thread-safe
        )

    logger.info(f"Logger configured with level: {log_level}")


def get_logger(name: str = __name__):
    """Get logger instance"""
    return logger.bind(name=name)
