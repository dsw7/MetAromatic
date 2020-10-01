#### exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_GENERAL_PROGRAM_FAILURES = 2

#### general met aromatic algorithm parameters
MINIMUM_CUTOFF_DIST = 0.00
MINIMUM_CUTOFF_ANGLE = 0.00
MAXIMUM_CUTOFF_ANGLE = 360.00
MINIMUM_VERTICES = 3

#### threading
MAXIMUM_WORKERS = 15

#### database stuff
DEFAULT_MONGO_HOST = 'localhost'
DEFAULT_MONGO_PORT = 27017

#### logging stuff
DEFAULT_LOGFILE_NAME = 'met_aromatic.log'
LOG_LEVEL = 20
# CRITICAL 50
# ERROR    40
# WARNING  30
# INFO     20
# DEBUG    10
# NOTSET    0

#### other
LEN_PDB_CODE = 4

#### terminal UI header
HEADER_TEXT = '*** MET-AROMATIC RESULTS ***'
FOOTER_TEXT = "Press 'q' to exit | Use KEY_UP and KEY_DOWN to scroll through parameters"
