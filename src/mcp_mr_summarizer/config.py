"""Simple configuration for the MCP merge request summarizer."""

import os
import logging


def setup_logging():
    """Setup logging with environment variables."""
    # Get log level from environment variable, default to INFO
    log_level_str = os.getenv("LOG_LEVEL", "DEBUG").upper() # Set to DEBUG

    # Map string log levels to logging constants
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = log_level_map.get(log_level_str, logging.INFO)

    # Get log format from environment variable
    log_format = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Define log file path
    log_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "mcp_mr_summarizer.log")

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ],
    )

    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level_str}")
    logger.info(f"Log file: {log_file}")