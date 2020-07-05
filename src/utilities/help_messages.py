#### top level mutually exclusive options
MSG_AI = 'Run a single Met-aromatic calculation on a PDB structure.'
MSG_BI = 'Run a single bridging interaction query on a PDB structure.'
MSG_BATCH = 'Run a batch job.'
MSG_TEST = 'Run Pytest over this project.'
MSG_TEST_COV = 'Run Pytest over this project with a coverage report.'

#### low level met aromatic algorithm options for ai, bi and batch jobs
MSG_CUTOFF = 'Set a Euclidean cutoff.'
MSG_ANGLE = 'Set Met-theta/Met-phi angle.'
MSG_MODEL = 'Set a lone pair interpolation model.'
MSG_CHAIN = 'Choose a protein chain identifier.'
MSG_VERTICES = 'Choose number of vertices for bridging interactions.'

#### log files
MSG_PATH_TO_LOG_FILE = (
    'Enter a path / log file name.\n'
    'The default path is /tmp/met_aromatic.log'
)

#### mongodb batch job parameters
MSG_PORT = 'Set a MongoDB port.'
MSG_HOST = 'Set a MongoDB host.'
MSG_DB = 'Choose a MongoDB export database name.'
MSG_COL = 'Choose a MongoDB export collection name.'
MSG_THREADS = (
    'Choose number of threads to use for batch job.\n'
    'Default number of threads is 5.'
)

#### testing
MSG_TEST_EXPRESSION = (
    'Run a subset of tests matching expression.\n'
    'Expression can match filename, test class name or test function name.'
)
MSG_EXIT_ON_FAILURE = 'Exit on first test failure.'
MSG_QUIET = 'Disable test verbosity.'
