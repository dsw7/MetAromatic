from typing import TypeVar

T = TypeVar('T')

#### Logging
LOGRECORD_FORMAT = '%(asctime)s %(levelname)s [ %(funcName)s ] %(message)s'
ISO_8601_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

#### Database stuff
DEFAULT_MONGO_HOST = 'localhost'
DEFAULT_MONGO_PORT = 27017
DEFAULT_SERVER_TIMEOUT_SEC = 1.00
