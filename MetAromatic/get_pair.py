from pathlib import Path
from .algorithm import MetAromatic
from .aliases import RawData
from .load_resources import load_local_pdb_file, load_pdb_file_from_rscb
from .models import MetAromaticParams, FeatureSpace
from .utils import print_separator


def get_pairs_from_file(params: MetAromaticParams, filepath: Path) -> FeatureSpace:
    raw_data: RawData = load_local_pdb_file(filepath)
    return MetAromatic(params=params, raw_data=raw_data).get_interactions()


def get_pairs_from_pdb(params: MetAromaticParams, pdb_code: str) -> FeatureSpace:
    raw_data: RawData = load_pdb_file_from_rscb(pdb_code)
    return MetAromatic(params=params, raw_data=raw_data).get_interactions()


def print_interactions(fs: FeatureSpace) -> None:
    print_separator()

    print("ARO        POS        MET POS    NORM       MET-THETA  MET-PHI")
    print_separator()

    for i in fs.interactions:
        print(
            f"{i.aromatic_residue:<10} "
            f"{i.aromatic_position:<10} "
            f"{i.methionine_position:<10} "
            f"{i.norm:<10} "
            f"{i.met_theta_angle:<10} "
            f"{i.met_phi_angle:<10}"
        )

    print_separator()
