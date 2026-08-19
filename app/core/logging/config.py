import logging.config

from app.core.config import settings

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": "app.core.logging.middleware.RequestIDLogFilter",
        },
    },
    "formatters": {
        "simple": {
            "format": "{levelname} {asctime} [req={request_id}] {message}",
            "style": "{",
        },
        "json": {
            "()": "app.core.logging.formatters.JSONLogFormatter",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json" if settings.LOG_FORMAT == "json" else "simple",
            "filters": ["request_id"],
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def setup_logging() -> None:
    logging.config.dictConfig(LOGGING)
