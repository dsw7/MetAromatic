from gzip import open as gz_open
from logging import getLogger
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.error import URLError
from urllib.request import urlretrieve, urlcleanup
from .aliases import RawData
from .consts import TMPDIR
from .errors import SearchError

LOGGER = getLogger("met-aromatic")


def load_local_pdb_file(pdb_file: Path) -> RawData:
    LOGGER.debug('Reading local file "%s"', pdb_file)

    if not pdb_file.exists():
        raise SearchError(f'File "{pdb_file}" does not exist')

    return pdb_file.read_text().splitlines()


def _get_ftp_url(pdb_code: str) -> str:
    ent_gz = f"pdb{pdb_code}.ent.gz"

    return f"ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{pdb_code[1:3]}/{ent_gz}"


def load_pdb_file_from_rscb(pdb_code: str) -> RawData:
    LOGGER.debug('Fetching PDB file "%s"', pdb_code)

    ftp_url = _get_ftp_url(pdb_code.lower())
    LOGGER.debug('Accessing URL: "%s"', ftp_url)

    raw_data: RawData = []
    with NamedTemporaryFile(dir=TMPDIR) as f:
        try:
            urlcleanup()
            urlretrieve(ftp_url, f.name)
        except URLError as error:
            raise SearchError(f"Invalid PDB entry '{pdb_code}'") from error

        with gz_open(f.name, "rt") as gz:
            for line in gz:
                raw_data.append(line)

    return raw_data
