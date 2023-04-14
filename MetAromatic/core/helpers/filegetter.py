import gzip
from typing import Optional
from urllib.request import urlretrieve, urlcleanup
from urllib.error import URLError
from os import remove
from pathlib import Path
from tempfile import gettempdir


# XXX put this in a context

class PDBFileGetter:

    tmpdir = gettempdir()

    def __init__(self, code: str) -> None:
        self.code = code.lower()
        ent_gz = 'pdb{}.ent.gz'.format(self.code)

        self.ftp_url = 'ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{}/{}'.format(self.code[1:3], ent_gz)

        self.res_tar = Path(self.tmpdir) / ent_gz
        self.res_untar = self.res_tar.with_suffix('')

    def fetch_entry_from_pdb(self) -> Optional[Path]:

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
        remove(self.res_untar)
