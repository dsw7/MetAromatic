from logging import getLogger
from networkx import Graph, connected_components
from MetAromatic.pair import MetAromatic
from MetAromatic.complex_types import TYPE_BRIDGE_SPACE
from .models import MetAromaticParams, FeatureSpace


class GetBridgingInteractions:
    log = getLogger("met-aromatic")

    def __init__(self, params: MetAromaticParams) -> None:
        self.params = params
        self.f: TYPE_BRIDGE_SPACE

    def get_interacting_pairs(self, code: str) -> bool:
        fs: FeatureSpace = MetAromatic(self.params).get_met_aromatic_interactions(code)

        if not fs.OK:
            self.log.error(
                "Cannot get bridging interactions as Met-aromatic algorithm failed"
            )

            self.f["OK"] = False
            self.f["status"] = fs.status
            return False

        if len(fs.interactions) < 1:
            self.log.info(
                "No Met-aromatic interactions were found therefore cannot find bridges"
            )

            self.f["status"] = "No Met-aromatic interactions were found"
            return False

        for interaction in fs.interactions:
            pair = (
                f"{interaction.aromatic_residue}{interaction.aromatic_position}",
                f"MET{interaction.methionine_position}",
            )
            self.f["interactions"].add(pair)

        return True

    def isolate_connected_components(self, vertices: int) -> None:
        graph: Graph = Graph()
        graph.add_edges_from(self.f["interactions"])

        for bridge in connected_components(graph):
            if len(bridge) == vertices:
                self.f["bridges"].append(bridge)

        # Note that inverse bridges (MET-ARO-MET) not removed!

        num_bridges = len(self.f["bridges"])

        if num_bridges > 0:
            if num_bridges == 1:
                self.log.info("Found 1 bridge")
            else:
                self.log.info("Found %i bridges", num_bridges)

            return

        self.log.info("Found no bridges")
        self.f["status"] = "No bridges"

    def get_bridging_interactions(self, code: str, vertices: int) -> TYPE_BRIDGE_SPACE:
        self.log.info('Locating bridging interactions for entry "%s"', code)

        self.f = {"interactions": set(), "bridges": [], "OK": True, "status": "Success"}

        if not self.get_interacting_pairs(code):
            return self.f

        self.isolate_connected_components(vertices=vertices)

        return self.f
