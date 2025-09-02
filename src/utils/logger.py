from .singleton import SingletonMeta
import logging
from logging.handlers import RotatingFileHandler


class Logger(metaclass=SingletonMeta):
    """
    A singleton logger class that provides a centralized logging mechanism.
    """

    def __init__(self, name="app_logger", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        if not self.logger.hasHandlers():
            ch = logging.StreamHandler()
            ch.setLevel(level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger


def log_debug(message):
    logger = Logger().get_logger()
    logger.debug(message)


def log_info(message):
    logger = Logger().get_logger()
    logger.info(message)


def log_warning(message):
    logger = Logger().get_logger()
    logger.warning(message)


def log_error(message):
    logger = Logger().get_logger()
    logger.error(message)


def log_critical(message):
    logger = Logger().get_logger()
    logger.critical(message)


def set_log_level(level):
    logger = Logger().get_logger()
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def add_file_handler(file_path, level=logging.INFO):
    """
    Adds a file handler to the logger.
    """
    logger = Logger().get_logger()
    fh = RotatingFileHandler(file_path, maxBytes=2**20, backupCount=5)
    fh.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def remove_file_handler(file_path):
    """
    Removes a file handler from the logger.
    """
    logger = Logger().get_logger()
    for handler in logger.handlers:
        if (
            isinstance(handler, RotatingFileHandler)
            and handler.baseFilename == file_path
        ):
            logger.removeHandler(handler)
            handler.close()
            break


def clear_handlers():
    """
    Removes all handlers from the logger.
    """
    logger = Logger().get_logger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
