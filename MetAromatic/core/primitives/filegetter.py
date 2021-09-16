import gzip
from urllib.request import urlretrieve, urlcleanup
from urllib.error import URLError
from os import remove, path
from tempfile import gettempdir


class PDBFileGetter:

    def __init__(self, code: str) -> None:
        self.code = code.lower()
        ent_gz = 'pdb{}.ent.gz'.format(self.code)

        self.ftp_url = 'ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{}/{}'.format(self.code[1:3], ent_gz)
        self.res_tar = path.join(gettempdir(), ent_gz)
        self.res_untar = self.res_tar.strip('.gz')

    def fetch_entry_from_pdb(self) -> str:
        try:
            urlcleanup()
            urlretrieve(self.ftp_url, self.res_tar)
        except URLError:
            return None

        with gzip.open(self.res_tar, 'rb') as gz:
            with open(self.res_untar, 'wb') as out:
                out.writelines(gz)

        remove(self.res_tar)
        return self.res_untar

    def remove_entry(self) -> bool:
        try:
            remove(self.res_untar)
        except FileNotFoundError:
            return False

        return True
