from logging import getLogger
from networkx import Graph, connected_components
from .errors import SearchError
from .models import MetAromaticParams, FeatureSpace, BridgeSpace
from .pair import MetAromatic


class GetBridgingInteractions:
    log = getLogger("met-aromatic")

    def __init__(self, params: MetAromaticParams) -> None:
        self.params = params
        self.bs: BridgeSpace

    def get_interacting_pairs(self, code: str) -> None:
        fs: FeatureSpace = MetAromatic(self.params).get_met_aromatic_interactions(code)

        for interaction in fs.interactions:
            pair = (
                f"{interaction.aromatic_residue}{interaction.aromatic_position}",
                f"MET{interaction.methionine_position}",
            )
            self.bs.interactions.add(pair)

    def isolate_connected_components(self, vertices: int) -> None:
        graph: Graph = Graph()
        graph.add_edges_from(self.bs.interactions)

        for bridge in connected_components(graph):
            if len(bridge) == vertices:
                self.bs.bridges.append(bridge)

        # Note that inverse bridges (MET-ARO-MET) not removed!

        num_bridges = len(self.bs.bridges)

        if num_bridges == 0:
            raise SearchError("Found no bridges")

        if num_bridges == 1:
            self.log.info("Found 1 bridge")
        else:
            self.log.info("Found %i bridges", num_bridges)

    def get_bridging_interactions(self, code: str, vertices: int) -> BridgeSpace:
        self.log.info('Locating bridging interactions for entry "%s"', code)

        self.bs = BridgeSpace()
        self.get_interacting_pairs(code)
        self.isolate_connected_components(vertices=vertices)

        return self.bs
