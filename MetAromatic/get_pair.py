from pathlib import Path
from .algorithm import MetAromatic
from .aliases import RawData, Models
from .load_resources import load_local_pdb_file, load_pdb_file_from_rscb
from .models import FeatureSpace, get_params
from .utils import print_separator


def get_pairs_from_file(
    filepath: Path,
    chain: str,
    cutoff_angle: float,
    cutoff_distance: float,
    model: Models,
) -> FeatureSpace:
    params = get_params(
        chain=chain,
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        model=model,
    )

    raw_data: RawData = load_local_pdb_file(filepath)
    return MetAromatic(params=params, raw_data=raw_data).get_interactions()


def get_pairs_from_pdb(
    pdb_code: str,
    chain: str,
    cutoff_angle: float,
    cutoff_distance: float,
    model: Models,
) -> FeatureSpace:
    params = get_params(
        chain=chain,
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        model=model,
    )

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
