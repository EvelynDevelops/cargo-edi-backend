import logging
import os
import inspect


def create_logger():
    logger = logging.getLogger("EDIService")
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        return logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # File handler
    log_file_path = os.path.join(os.getcwd(), "edi.log")
    file_handler = logging.FileHandler(log_file_path, mode="a")
    file_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s][%(funcName)s][%(lineno)d] - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = create_logger()


def log_edi(level: str, message: str):
    frame = inspect.currentframe().f_back
    filename = os.path.basename(frame.f_code.co_filename)
    function_name = frame.f_code.co_name
    line_number = frame.f_lineno

    formatted = f"[{filename}][{function_name}][{line_number}] - {message}"

    level = level.lower()
    if level == "debug":
        logger.debug(formatted)
    elif level == "info":
        logger.info(formatted)
    elif level == "warning":
        logger.warning(formatted)
    elif level == "error":
        logger.error(formatted)
    else:
        logger.info(formatted)  # default fallback
