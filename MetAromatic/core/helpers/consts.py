from typing import TypeVar

T = TypeVar('T')

#### Exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

#### General met aromatic algorithm parameters
MINIMUM_CUTOFF_DIST = 0.00
MINIMUM_CUTOFF_ANGLE = 0.00
MAXIMUM_CUTOFF_ANGLE = 360.00
MINIMUM_VERTICES = 3

#### Database stuff
DEFAULT_MONGO_HOST = 'localhost'
DEFAULT_MONGO_PORT = 27017
DEFAULT_SERVER_TIMEOUT_SEC = 1.00

#### Terminal UI headers and footers
HEADER_TEXT = '*** MET-AROMATIC RESULTS ***'
FOOTER_TEXT = "Press 'q' to exit | Use KEY_UP and KEY_DOWN to scroll through results"
HEADER_RESULTS = [
    'ARO', 'POS', 'MET',
    'NORM', 'MET-PHI', 'MET-THETA'
]
FORMATTED_HEADER = '{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}'.format(*HEADER_RESULTS)
