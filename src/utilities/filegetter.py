import gzip
from urllib.request import urlretrieve, urlcleanup
from urllib.error import URLError
from os import remove, getcwd, path


class PDBFileGetter:
    def __init__(self, code):
        self.code = code.lower()

    def fetch_entry_from_pdb(self):
        subdir = self.code[1:3]
        infile = f'pdb{self.code}.ent.gz'
        decompressed = infile.strip('.gz')
        fullpath = f'ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{subdir}/{infile}'

        try:
            urlcleanup()
            urlretrieve(fullpath, infile)
        except URLError:
            pass
        else:
            with gzip.open(infile, 'rb') as gz:
                with open(decompressed, 'wb') as out:
                    out.writelines(gz)
            remove(infile)
            return path.join(getcwd(), decompressed)

    def remove_entry(self):
        filename = f'pdb{self.code}.ent'
        try:
            remove(path.join(getcwd(), filename))
        except FileNotFoundError:
            return False
        else:
            return True
