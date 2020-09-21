import sys
import logging
from os import path
from tempfile import gettempdir
from .consts import (
    DEFAULT_LOGFILE_NAME,
    LOG_LEVEL
)


class Logger:
    def __init__(self):
        self.formatter = logging.Formatter(
            '%(levelname)s:%(asctime)s: %(message)s',
            datefmt='%d-%b-%y:%H:%M:%S',
        )

    def handle_log_to_file(self):
        filepath = path.join(gettempdir(), DEFAULT_LOGFILE_NAME)

        print(f'Batch job progress is being logged to: {filepath}')

        handler = logging.FileHandler(filepath, 'w')
        handler.setFormatter(self.formatter)

        logger = logging.getLogger('file')
        logger.setLevel(LOG_LEVEL)
        logger.addHandler(handler)
        return logger

    def handle_log_to_stream(self):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(self.formatter)

        logger = logging.getLogger('stream')
        logger.setLevel(LOG_LEVEL)
        logger.addHandler(handler)
        return logger
