import sys
from os import EX_OK
from typing import Dict, Union
from networkx import Graph, connected_components
from click import echo
from core.helpers.consts import T
from .pair import MetAromatic

MINIMUM_VERTICES = 3


class GetBridgingInteractions:

    def __init__(self: T, cli_opts: Dict[str, Union[str, float]]) -> T:

        self.cli_opts = cli_opts
        self.interactions = set()
        self.bridges = []

    def get_interacting_pairs(self: T, code: str) -> bool:

        results = MetAromatic(**self.cli_opts).get_met_aromatic_interactions(code)

        if results['exit_code'] != EX_OK:
            return False

        for interaction in results['results']:
            pair = (
                f"{interaction['aromatic_residue']}{interaction['aromatic_position']}",
                f"MET{interaction['methionine_position']}"
            )
            self.interactions.add(pair)

        return True

    def isolate_connected_components(self: T, vertices: int) -> None:

        graph = Graph()
        graph.add_edges_from(self.interactions)

        for bridge in connected_components(graph):
            if len(bridge) == vertices:
                self.bridges.append(bridge)

        # Note that inverse bridges (MET-ARO-MET) not removed!

    def get_bridging_interactions(self: T, code: str, vertices: int) -> bool:

        if vertices < MINIMUM_VERTICES:
            #sys.exit(f'Vertices must be >= {MINIMUM_VERTICES}')
            return False

        if not self.get_interacting_pairs(code):
            return False

        self.isolate_connected_components(vertices=vertices)

        return True

    def display_results(self: T) -> None:

        if len(self.bridges) == 0:
            sys.exit('No bridges found')

        echo(self.bridges)
