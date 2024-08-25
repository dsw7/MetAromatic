from pathlib import Path
from .algorithm import MetAromatic
from .aliases import RawData
from .load_resources import load_local_pdb_file, load_pdb_file_from_rscb
from .models import MetAromaticParams, FeatureSpace


def get_pairs_from_file(params: MetAromaticParams, filepath: Path) -> None:
    raw_data: RawData = load_local_pdb_file(filepath)

    fs: FeatureSpace = MetAromatic(params=params, raw_data=raw_data).get_interactions()
    fs.print_interactions()


def get_pairs_from_pdb(params: MetAromaticParams, pdb_code: str) -> None:
    raw_data: RawData = load_pdb_file_from_rscb(pdb_code)

    fs: FeatureSpace = MetAromatic(params=params, raw_data=raw_data).get_interactions()
    fs.print_interactions()
