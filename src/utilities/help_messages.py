#### top level mutually exclusive options
MSG_AI = 'Run a single Met-aromatic calculation on a PDB structure. \nUsage: $ python runner.py --ai'
MSG_BI = 'Run a single bridging interaction query on a PDB structure. \nUsage: $ python runner.py --bi'
MSG_BATCH = 'Run a batch job. \nUsage: $ python runner.py --batch'
MSG_TEST = 'Run pytest over this project. \nUsage: $ python runner.py --test'
MSG_TEST_COV = 'Run pytest over this project with a coverage report. \nUsage: $ python runner.py --testcov'

#### low level met aromatic algorithm options for ai, bi and batch jobs
MSG_CODE = 'Process a pdb code. \nUsage: --code <1abc>'
MSG_CUTOFF = 'Set a Euclidean cutoff. \nUsage: --cutoff <float>'
MSG_ANGLE = 'Set Met-theta/Met-phi angle. \nUsage: --angle <float>'
MSG_MODEL = 'Set a lone pair interpolation model. \nUsage: --model <cp|rm>'
MSG_CHAIN = 'Choose a chain. \nUsage: --chain <chain>'
MSG_VERTICES = 'Choose number of vertices for bridging interactions. \nUsage: --vertices <3|4|5...>'

#### mongodb batch job parameters
MSG_PORT = 'Set a MongoDB port. \nUsage: --mongoport <port>'
MSG_HOST = 'Set a MongoDB host. \nUsage: --mongohost <host>'
MSG_DB = 'Choose a MongoDB export database name. \nUsage: --database <name>'
MSG_COL = 'Choose a MongoDB export collection name. \nUsage: --collection <name>'
MSG_THREADS = 'Choose number of threads to use for batch job. \nUsage: --threads <num_threads>'
MSG_BATCH_FILE = 'Choose a batch file containing PDB codes of interest. \nUsage: --batch_file </path/to/file>'
