from gzip import open as gz_open
from pathlib import Path
from tempfile import NamedTemporaryFile, gettempdir
from urllib.error import URLError
from urllib.request import urlretrieve, urlcleanup
from .aliases import RawData
from .errors import SearchError

TMPDIR = Path(gettempdir())


def _is_valid_pdb_file(file_content: list[str]) -> bool:
    tags = {
        "HEADER": False,
        "TITLE": False,
        "REMARK": False,
        "ATOM": False,
        "HETATM": False,
        "END": False,
    }

    for line in file_content:
        tag = line[:6].strip()

        if tag in tags:
            tags[tag] = True

        if all(tags.values()):
            return True

    return False


def load_local_pdb_file(pdb_file: Path) -> RawData:
    contents = pdb_file.read_text().splitlines()

    if not _is_valid_pdb_file(contents):
        raise SearchError("Not a valid PDB file")

    return contents


def _get_ftp_url(pdb_code: str) -> str:
    ent_gz = f"pdb{pdb_code}.ent.gz"

    return f"ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{pdb_code[1:3]}/{ent_gz}"


def load_pdb_file_from_rscb(pdb_code: str) -> RawData:
    ftp_url = _get_ftp_url(pdb_code.lower())

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
