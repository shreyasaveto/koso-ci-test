import logging.config
from pathlib import Path
from core.config import ENVIRONMENT

LOG_DIR = Path(__file__).resolve().parent.parent / "logger"
LOG_DIR.mkdir(parents=True, exist_ok=True)

ENV = ENVIRONMENT.lower()


class LevelFilter(logging.Filter):
    def __init__(self, min_level=None, exact_level=None):
        super().__init__()  # Calling the super class logging.Filter
        self.min_level = min_level
        self.exact_level = exact_level

    def filter(self, record):                   #Each log level checking for the logging level
        if self.exact_level is not None:
            return record.levelno == self.exact_level
        if self.min_level is not None:
            return record.levelno >= self.min_level
        return True


# formate for the logging
FORMATTERS = {
    "default": {"format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"},
    "detailed": {
        "format": "[%(asctime)s] [%(levelname)s] [%(name)s] "
                  "[%(filename)s:%(lineno)d] - %(message)s",
    },
}


def file_handler(filename, level, formatter="detailed", flt=None,
                 max_bytes=10_000_000, backup_count=5):

    h = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": LOG_DIR / filename,
        "formatter": formatter,
        "level": level,
        "maxBytes": max_bytes,
        "backupCount": backup_count
    }
    if flt:
        h["filters"] = [flt]
    return h


if ENV == "prod":
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": FORMATTERS,
        "filters": {
            "only_info": {"()": LevelFilter, "exact_level": logging.INFO},
            "only_error": {"()": LevelFilter, "min_level": logging.ERROR},
        },
        "handlers": {
            "app_file": file_handler("app.log", "INFO", flt="only_info"),
            "error_file": file_handler("error.log", "ERROR", flt="only_error"),
        },
        "root": {"handlers": ["app_file", "error_file"], "level": "INFO"},
    }

else:  # dev/Staging environment logging config
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": FORMATTERS,
        "filters": {
            "only_info": {"()": LevelFilter, "exact_level": logging.INFO},
            "only_debug": {"()": LevelFilter, "exact_level": logging.DEBUG},
            "only_error": {"()": LevelFilter, "min_level": logging.ERROR},
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "default", "level": "DEBUG"},
            "debug_file": file_handler("debug.log", "DEBUG", flt="only_debug"),
            "app_file": file_handler("app.log", "INFO", flt="only_info"),
            "error_file": file_handler("error.log", "ERROR", flt="only_error"),
        },
        "root": {"handlers": ["console", "debug_file", "app_file", "error_file"], "level": "DEBUG"},
    }

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")
