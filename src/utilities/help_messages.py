#### top level mutually exclusive options
MSG_AI = 'Run a single Met-aromatic calculation on a PDB structure.'
MSG_BI = 'Run a single bridging interaction query on a PDB structure.'
MSG_BATCH = 'Run a batch job.'
MSG_TEST = 'Run pytest over this project. \nUsage: $ python runner.py --test'
MSG_TEST_COV = 'Run pytest over this project with a coverage report. \nUsage: $ python runner.py --testcov'

#### low level met aromatic algorithm options for ai, bi and batch jobs
MSG_CODE = 'Process a pdb code. \nUsage: $ python runner.py --code <1abc>'
MSG_CUTOFF = 'Set a Euclidean cutoff. \nDefault = 6.0 Angstroms. \nUsage: $ python runner.py --cutoff <float>'
MSG_ANGLE = 'Set Met-theta/Met-phi angle. \nDefault = 109.5 degrees. \nUsage: $ python runner.py --angle <float>'
MSG_MODEL = 'Set a lone pair interpolation model. \nDefault = cp. \nUsage: $ python runner.py --model <cp|rm>'
MSG_CHAIN = 'Choose a chain. \nDefault = A. \nUsage: $ python runner.py --chain <chain>'
MSG_VERTICES = 'Choose number of vertices for bridging interactions. \nDefault = 3. \nUsage: $ python runner.py --vertices <3|4|5...>'

#### mongodb batch job parameters
MSG_PORT = 'Set a MongoDB port.'
MSG_HOST = 'Set a MongoDB host.'
MSG_DB = 'Choose a MongoDB export database name.'
MSG_COL = 'Choose a MongoDB export collection name.'
