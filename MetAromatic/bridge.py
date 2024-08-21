from logging import getLogger
from networkx import Graph, connected_components
from .models import MetAromaticParams, FeatureSpace, BridgeSpace
from .pair import MetAromatic


class GetBridgingInteractions:
    log = getLogger("met-aromatic")

    def __init__(self, params: MetAromaticParams) -> None:
        self.params = params
        self.bs: BridgeSpace

    def get_interacting_pairs(self, code: str) -> bool:
        fs: FeatureSpace = MetAromatic(self.params).get_met_aromatic_interactions(code)

        if not fs.OK:
            self.log.error(
                "Cannot get bridging interactions as Met-aromatic algorithm failed"
            )

            self.bs.OK = False
            self.bs.status = fs.status
            return False

        if len(fs.interactions) < 1:
            self.log.info(
                "No Met-aromatic interactions were found therefore cannot find bridges"
            )

            self.bs.status = "No Met-aromatic interactions were found"
            return False

        for interaction in fs.interactions:
            pair = (
                f"{interaction.aromatic_residue}{interaction.aromatic_position}",
                f"MET{interaction.methionine_position}",
            )
            self.bs.interactions.add(pair)

        return True

    def isolate_connected_components(self, vertices: int) -> None:
        graph: Graph = Graph()
        graph.add_edges_from(self.bs.interactions)

        for bridge in connected_components(graph):
            if len(bridge) == vertices:
                self.bs.bridges.append(bridge)

        # Note that inverse bridges (MET-ARO-MET) not removed!

        num_bridges = len(self.bs.bridges)

        if num_bridges > 0:
            if num_bridges == 1:
                self.log.info("Found 1 bridge")
            else:
                self.log.info("Found %i bridges", num_bridges)

            return

        self.log.info("Found no bridges")
        self.bs.status = "No bridges"

    def get_bridging_interactions(self, code: str, vertices: int) -> BridgeSpace:
        self.log.info('Locating bridging interactions for entry "%s"', code)

        self.bs = BridgeSpace()

        if not self.get_interacting_pairs(code):
            return self.bs

        self.isolate_connected_components(vertices=vertices)

        return self.bs
