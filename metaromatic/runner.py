"""
dsw7@sfu.ca
The "main" script that accepts PDB code input from user.
"""


import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from tqdm import tqdm
from pymongo import MongoClient
from runner_helpers import print_version, colorize_error, mapper, pandas_print, HelpMessages
from ma3 import MetAromatic
from versionhandler import VersionHandler


COLUMNS = ["ARO", "ARO POS", "MET", "MET POS", "NORM", "MET-THETA", "MET-PHI"]
DEFAULT_PORT = 27017
DEFAULT_HOST = "localhost"
DB = "foo"
COL = "bar"


class Runner:
    def __init__(self):
        parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
        parser.add_argument('-c', '--code', help=HelpMessages.MSG_CODE, default='0', type=str)
        parser.add_argument('-b', '--batch', help=HelpMessages.MSG_BATCH, default='0', type=str)
        parser.add_argument('-n', '--cutoff', help=HelpMessages.MSG_CUTOFF, default=6.0, type=float)
        parser.add_argument('-a', '--angle', help=HelpMessages.MSG_ANGLE, default=109.5, type=float)
        parser.add_argument('-m', '--model', help=HelpMessages.MSG_MODEL, default='cp')
        parser.add_argument('-v', '--verbose', help=HelpMessages.MSG_VERBOSITY, action='store_true')
        parser.add_argument('--export-mongo', help=HelpMessages.MSG_EXPORT_MONGO, action='store_true')
        parser.add_argument('--mongoport', help=HelpMessages.MSG_PORT, default=DEFAULT_PORT, type=int)
        parser.add_argument('--mongohost', help=HelpMessages.MSG_HOST, default=DEFAULT_HOST, type=str)
        parser.add_argument('--database', help=HelpMessages.MSG_DB, default=DB, type=str)
        parser.add_argument('--collection', help=HelpMessages.MSG_COL, default=COL, type=str)

        self.__version__ = VersionHandler('..').get_version().get('__version__')
        self.code = parser.parse_args().code
        self.path = parser.parse_args().batch
        self.cutoff = parser.parse_args().cutoff
        self.angle = parser.parse_args().angle
        self.model = parser.parse_args().model
        self.verbose = parser.parse_args().verbose
        self.export_mongo = parser.parse_args().export_mongo
        self.mongoport = parser.parse_args().mongoport
        self.mongohost = parser.parse_args().mongohost
        self.database = parser.parse_args().database
        self.collection = parser.parse_args().collection

        # print_version(self.__version__)

        self.parser = parser  # verify_user_input() makes a ref to parser object
        self.verify_user_input()
        self.print_args()

        # and set up MongoDB if need be
        # apparently not a good idea to close a MongoDB connection
        if self.export_mongo:
            self.client = MongoClient(self.mongohost, self.mongoport)

    def verify_user_input(self):
        if len(sys.argv) < 2:
            print(colorize_error('Warning: no options specified!\n'))
            self.parser.print_help()
            sys.exit()
        else:
            if (len(self.code) != 4) and (self.code != '0'):
                sys.exit('Invalid pdb code: {}'.format(self.code))
            elif (self.code != '0') and (self.path != '0'):
                sys.exit('Cannot choose between .txt file and pdb code.')
            elif self.model not in ('cp', 'rm'):
                sys.exit("Invalid model. Valid models are: cp (Cross Product) or rm (Rodrigues' method).")
            elif (self.angle < 0.0) or (self.angle > 360.00):
                sys.exit('Angle must be between 0 and 360 degrees.')
            elif self.cutoff < 0:
                sys.exit('Cutoff must be greater than or equal to 0.0 Angstroms.')
            else:
                pass

    def print_args(self):
        """ All user input printed to console for logging purposes """
        print("Cutoff: {}".format(self.cutoff))
        print("Angle: {}".format(self.angle))
        print("Model: {}".format(self.model))
        print("Mongo Port: {}".format(self.mongoport))
        print("Mongo Host: {}".format(self.mongohost))
        print("Database Name: {}".format(self.database))
        print("Collection Name: {}".format(self.collection))
        print("Export to MongoDB: {}\n".format(self.export_mongo))

    def base(self, code):
        """ Base for handling Met-aromatic PDB code input source """
        try:
            ma = MetAromatic(code=code, cutoff=self.cutoff, angle=self.angle, model=self.model)
            results, EC = ma.met_aromatic(), ma.get_ec_classifier()
        except Exception as exception:
            tqdm.write('An exception has occurred for entry {}:\n{}'.format(code, exception))
        else:
            if results is None:
                tqdm.write('NoneType object was returned from MetAromatic algorithm.')
            elif not results:
                pass
            else:
                mapped = mapper(results, EC, code)
                if self.verbose:
                    pandas_print(mapped)
                if self.export_mongo:
                    self.client[self.database][self.collection].insert_many(mapped)

    def run_single(self):
        """ Query a single PDB entry """
        self.base(code=self.code)

    def run_batch(self):
        """ Query a batch of PDB entries """
        with open(self.path, 'r') as f:  #XXX: fails to handle missing .txt file
            codes = f.read().splitlines()

        if not codes:
            sys.exit('Empty .txt file.')
        else:
            for code in tqdm(codes, unit=' files', miniters=1):
                self.base(code=code)

    def run(self):
        """ Handle either batch or single PDB code request """
        if (self.code == '0') and (self.path == '0'):
            sys.exit('No PDB code or path to .txt given.')
        elif (self.code != '0') and (self.path == '0'):
            self.run_single()
        elif (self.code == '0') and (self.path != '0'):
            self.run_batch()
        else:
            sys.exit('Cannot run both batch job and single code.')


if __name__ == '__main__':
    Runner().run()
