from dataclasses import dataclass, field
from logging import getLogger
from typing import Optional, Set, Tuple
from typing import Dict, Union, List
from networkx import Graph, connected_components
from MetAromatic.pair import MetAromatic


@dataclass
class BridgeSpace:

    interactions: Optional[Set[Tuple[str]]] = field(default_factory=set)
    bridges: Optional[List[Set[str]]] = field(default_factory=list)

    OK: bool = True
    status: str = 'Success'


class GetBridgingInteractions:

    log = getLogger('met-aromatic')

    def __init__(self, cli_opts: Dict[str, Union[str, float]]) -> None:

        self.cli_opts = cli_opts
        self.f = None

    def get_interacting_pairs(self, code: str) -> bool:

        ma_results = MetAromatic(**self.cli_opts).get_met_aromatic_interactions(code)

        if not ma_results.OK:
            self.log.error('Cannot get bridging interactions as Met-aromatic algorithm failed')

            self.f.OK = False
            self.f.status = ma_results.status
            return False

        if len(ma_results.interactions) < 1:
            self.log.info('No Met-aromatic interactions were found therefore cannot find bridges')

            self.f.status = 'No Met-aromatic interactions were found'
            return False

        for interaction in ma_results.interactions:
            pair = (
                f"{interaction['aromatic_residue']}{interaction['aromatic_position']}",
                f"MET{interaction['methionine_position']}"
            )
            self.f.interactions.add(pair)

        return True

    def isolate_connected_components(self, vertices: int) -> None:

        graph = Graph()
        graph.add_edges_from(self.f.interactions)

        for bridge in connected_components(graph):
            if len(bridge) == vertices:
                self.f.bridges.append(bridge)

        # Note that inverse bridges (MET-ARO-MET) not removed!

        num_bridges = len(self.f.bridges)

        if num_bridges > 0:

            if num_bridges == 1:
                self.log.info('Found 1 bridge')
            else:
                self.log.info('Found %i bridges', num_bridges)

            return

        self.log.info('Found no bridges')
        self.f.status = 'No bridges'

    def get_bridging_interactions(self, code: str, vertices: int) -> BridgeSpace:

        self.log.info('Locating bridging interactions for entry "%s"', code)

        self.f = BridgeSpace()

        if not self.get_interacting_pairs(code):
            return self.f

        self.isolate_connected_components(vertices=vertices)
        return self.f
