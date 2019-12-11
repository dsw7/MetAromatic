from hashlib import md5
from pandas import DataFrame
from colorama import Fore, Style

def mapper(result, ec, pdbcode):
    """ A helper for adapting Met-aromatic results to MongoDB """
    outgoing = []
    for item in result:
        doc = {
            "code": pdbcode,
            "aro": item[0],
            "arores": item[1],
            "met": item[3],
            "norm": item[4],
            "met-theta": item[5],
            "met-phi": item[6],
            "ec": ec
        }

        # overwrite MongoDB _id with custom _id to prevent writing duplicate data into database
        _id = ''.join([str(i) for i in doc.values()])
        doc['_id'] = md5(_id.encode()).hexdigest()
        outgoing.append(doc)
    return outgoing


def pandas_print(data):
    """
    I print a pandas dataframe of the data to prompt if verbose set to true
    Not super efficient but very readable
    """
    df = DataFrame(data)
    df = df.sort_values(by='norm')
    df = df.reset_index(drop=True)
    df = df.reindex(sorted(df.columns), axis=1)
    print(df)


def colorize_error(msg):
    """ Colorize stderr """
    return Fore.RED + msg + Style.RESET_ALL


def print_version(version):
    """ Colorize version """
    msg = "MetAromaticEngine Version: v.{}".format(version)
    print(Fore.LIGHTMAGENTA_EX + '-' * 50 + Style.RESET_ALL)
    print(Fore.LIGHTMAGENTA_EX + msg + Style.RESET_ALL)
    print(Fore.LIGHTMAGENTA_EX + '-' * 50 + Style.RESET_ALL)

    
class HelpMessages:
    MSG_CODE = 'Process a pdb code. \nUsage: $ python runner.py --code <1abc>'
    MSG_BATCH = 'Process a batch of pdb codes. \nUsage: $ python runner.py --batch /path/to/foo.txt'
    MSG_CUTOFF = 'Set a Euclidean cutoff. \nDefault = 6.0 Angstroms. \nUsage: $ python runner.py --cutoff <float>'
    MSG_ANGLE = 'Set Met-theta/Met-phi angle. \nDefault = 109.5 degrees. \nUsage: $ python runner.py --angle <float>'
    MSG_MODEL = 'Set a lone pair interpolation model. \nDefault = cp. \nUsage: $ python runner.py --model <cp|rm>'
    MSG_VERBOSITY = 'Set output verbosity. \nUsage: $ python runner.py --verbose'
    MSG_EXPORT_MONGO = 'Export results to MongoDB. \nUsage: $ python runner.py --export-mongo'
    MSG_PORT = 'Set a MongoDB port. \nDefault = 27017. \nUsage: $ python runner.py --mongoport <port>'
    MSG_HOST = 'Set a MongoDB host. \nDefault = localhost. \nUsage: $ python runner.py --mongohost <host>'
    MSG_DB = 'Choose a MongoDB export database name. \nDefault = ma. \nUsage: $ python runner.py --database <name>'
    MSG_COL = 'Choose a MongoDB export collection name. \nDefault = ma. \nUsage: $ python runner.py --collection <name>'

