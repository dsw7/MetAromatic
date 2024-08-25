from logging import getLogger
from networkx import Graph, connected_components
from .algorithm import MetAromatic
from .aliases import RawData
from .load_resources import load_pdb_file_from_rscb
from .models import MetAromaticParams, FeatureSpace, BridgeSpace

LOGGER = getLogger("met-aromatic")


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

    match len(bs.bridges):
        case 0:
            LOGGER.info("Found 0 bridges")
        case 1:
            LOGGER.info("Found 1 bridge")
        case _:
            LOGGER.info("Found %i bridges", len(bs.bridges))

    return bs


def get_bridges(params: MetAromaticParams, code: str, vertices: int) -> None:
    LOGGER.info('Locating bridging interactions for entry "%s"', code)

    raw_data: RawData = load_pdb_file_from_rscb(code)

    fs: FeatureSpace = MetAromatic(params=params, raw_data=raw_data).get_interactions()
    bs: BridgeSpace = _isolate_bridges(fs, vertices)

    bs.print_bridges()
