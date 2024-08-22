from logging import getLogger
from networkx import Graph, connected_components
from .errors import SearchError
from .models import MetAromaticParams, FeatureSpace, BridgeSpace
from .pair import MetAromatic

LOGGER = getLogger("met-aromatic")


def get_bridges(params: MetAromaticParams, code: str, vertices: int) -> BridgeSpace:
    LOGGER.info('Locating bridging interactions for entry "%s"', code)

    fs: FeatureSpace = MetAromatic(params).get_met_aromatic_interactions(code)
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

    num_bridges = len(bs.bridges)

    if num_bridges == 0:
        raise SearchError("Found no bridges")

    if num_bridges == 1:
        LOGGER.info("Found 1 bridge")
    else:
        LOGGER.info("Found %i bridges", num_bridges)

    return bs
