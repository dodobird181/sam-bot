from __future__ import annotations

import logging

import settings


class CustomFormatter(logging.Formatter):
    """
    Formatting for application logging. 
    Modified from: https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output.
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(asctime)s][%(name)s-%(levelname)s](%(filename)s:%(lineno)d): %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# create logger with 'spam_application'
_logger = logging.getLogger('Sam-bot')
_logger.setLevel(settings.CONSOLE_LOGGING_LEVEL)

# create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(CustomFormatter())

_logger.addHandler(console_handler)


def logger() -> logging.Logger:
    """
    Expose the logger to other modules.
    """
    return _logger