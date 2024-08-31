from networkx import Graph, connected_components
from .algorithm import MetAromatic
from .aliases import RawData, Models
from .load_resources import load_pdb_file_from_rscb
from .models import FeatureSpace, BridgeSpace, get_params
from .utils import print_separator


def _isolate_bridges(fs: FeatureSpace, vertices: int) -> BridgeSpace:
    bs = BridgeSpace()

    for interaction in fs.interactions:
        pair = (
            f"{interaction.aromatic_residue}{interaction.aromatic_position}",
            f"MET{interaction.methionine_position}",
        )
        bs.interactions.add(pair)

    graph: Graph = Graph()
    graph.add_edges_from(bs.interactions)

    for bridge in connected_components(graph):
        if len(bridge) == vertices:
            bs.bridges.append(bridge)

    # Note that inverse bridges (MET-ARO-MET) not removed!

    return bs


def get_bridges(
    chain: str,
    code: str,
    cutoff_angle: float,
    cutoff_distance: float,
    model: Models,
    vertices: int,
) -> BridgeSpace:
    params = get_params(
        chain=chain,
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        model=model,
    )
    raw_data: RawData = load_pdb_file_from_rscb(code)

    fs: FeatureSpace = MetAromatic(params=params, raw_data=raw_data).get_interactions()
    return _isolate_bridges(fs, vertices)


def print_bridges(bs: BridgeSpace) -> None:
    print_separator()

    if len(bs.bridges) > 0:
        for bridge in bs.bridges:
            print("{" + "}-{".join(bridge) + "}")
    else:
        print("Found 0 bridges")

    print_separator()
