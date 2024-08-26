import logging
from logging.config import dictConfig
from .consts import PATH_BATCH_LOG
from .get_pair import get_pairs_from_pdb, get_pairs_from_file

logging.addLevelName(logging.ERROR, "E")
logging.addLevelName(logging.WARNING, "W")
logging.addLevelName(logging.INFO, "I")
logging.addLevelName(logging.DEBUG, "D")

dictConfig(
    {
        "version": 1,
        "formatters": {
            "debug": {
                "datefmt": "%Y-%m-%dT%H:%M:%S",
                "format": "%(asctime)s %(threadName)s %(levelname)s %(message)s",
            }
        },
        "handlers": {
            "stream": {
                "class": "logging.StreamHandler",
                "formatter": "debug",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": PATH_BATCH_LOG,
                "formatter": "debug",
                "mode": "a",
            },
        },
        "loggers": {
            "met-aromatic": {
                "handlers": ["stream", "file"],
                "level": "INFO",
            },
        },
    }
)
