import gzip
from urllib.request import urlretrieve, urlcleanup
from urllib.error import URLError
from os import remove, path
from tempfile import gettempdir


class PDBFileGetter:
    def __init__(self, code):
        self.code = code.lower()
        tar = f'pdb{self.code}.ent.gz'
        self.url = f'ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{self.code[1:3]}/{tar}'
        self.res_tar = path.join(gettempdir(), tar)
        self.res_untar = self.res_tar.strip('.gz')

    def fetch_entry_from_pdb(self):
        try:
            urlcleanup()
            urlretrieve(self.url, self.res_tar)
        except URLError:
            return None

        with gzip.open(self.res_tar, 'rb') as gz:
            with open(self.res_untar, 'wb') as out:
                out.writelines(gz)

        remove(self.res_tar)
        return self.res_untar

    def remove_entry(self):
        retbool = True
        try:
            remove(self.res_untar)
        except FileNotFoundError:
            retbool = False
        return retbool
