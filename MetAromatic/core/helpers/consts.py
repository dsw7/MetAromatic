from typing import TypeVar

T = TypeVar('T')

#### Exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

#### Logging
LOGRECORD_FORMAT = '%(asctime)s %(levelname)s [ %(funcName)s ] %(message)s'
ISO_8601_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

#### General met aromatic algorithm parameters
MINIMUM_CUTOFF_DIST = 0.00
MINIMUM_CUTOFF_ANGLE = 0.00
MAXIMUM_CUTOFF_ANGLE = 360.00

#### Database stuff
DEFAULT_MONGO_HOST = 'localhost'
DEFAULT_MONGO_PORT = 27017
DEFAULT_SERVER_TIMEOUT_SEC = 1.00
