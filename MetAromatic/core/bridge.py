from dataclasses import dataclass, field
from logging import getLogger
from typing import Optional, Set, Tuple
from typing import Dict, Union, List
from networkx import Graph, connected_components
from core.helpers.consts import T
from core.pair import MetAromatic

MINIMUM_VERTICES = 3


@dataclass
class BridgeSpace:

    INTERACTIONS: Optional[Set[Tuple[str]]] = field(default_factory=set)
    BRIDGES: Optional[List[Set[str]]] = field(default_factory=list)

    OK: bool = True
    STATUS: str = 'Success'


class GetBridgingInteractions:

    log = getLogger('met-aromatic')

    def __init__(self: T, cli_opts: Dict[str, Union[str, float]]) -> T:

        self.cli_opts = cli_opts
        self.f = None

    def get_interacting_pairs(self: T, code: str) -> bool:

        results = MetAromatic(**self.cli_opts).get_met_aromatic_interactions(code)

        if not results.OK:
            self.log.error('Cannot get bridging interactions as Met-aromatic algorithm failed')

            self.f.OK = False
            self.f.STATUS = results.STATUS
            return False

        for interaction in results.INTERACTIONS:
            pair = (
                f"{interaction['aromatic_residue']}{interaction['aromatic_position']}",
                f"MET{interaction['methionine_position']}"
            )
            self.f.INTERACTIONS.add(pair)

        return True

    def isolate_connected_components(self: T, vertices: int) -> None:

        self.log.info('Locating bridging interactions')

        graph = Graph()
        graph.add_edges_from(self.f.INTERACTIONS)

        for bridge in connected_components(graph):
            if len(bridge) == vertices:
                self.f.BRIDGES.append(bridge)

        # Note that inverse bridges (MET-ARO-MET) not removed!

        self.log.info('Found %i bridges', len(self.f.BRIDGES))

    def get_bridging_interactions(self: T, code: str, vertices: int) -> BridgeSpace:

        self.f = BridgeSpace()

        if vertices < MINIMUM_VERTICES:
            self.log.error('Vertices must be >= %i', MINIMUM_VERTICES)

            self.f.OK = False
            self.f.STATUS = f'Vertices must be >= {MINIMUM_VERTICES}'
            return self.f

        if not self.get_interacting_pairs(code):
            return self.f

        self.isolate_connected_components(vertices=vertices)

        return self.f
