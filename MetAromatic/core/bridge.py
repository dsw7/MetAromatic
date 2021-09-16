from networkx import (
    Graph,
    connected_components
)
from .helpers.consts import EXIT_FAILURE
from .pair import MetAromatic


class GetBridgingInteractions:

    def __init__(self, cutoff_distance: float, cutoff_angle: float, chain: str, model: str) -> None:
        self.arguments = {
            'cutoff_distance': cutoff_distance,
            'cutoff_angle': cutoff_angle,
            'chain': chain,
            'model': model
        }

        self.results = None
        self.vertices = None
        self.code = None
        self.joined_pairs = set()
        self.bridges = None

    def run_met_aromatic(self) -> bool:
        self.results = MetAromatic(
            **self.arguments
        ).get_met_aromatic_interactions(self.code)

        if self.results['exit_code'] == EXIT_FAILURE:
            return False

        return True

    def get_joined_pairs(self) -> bool:
        for result in self.results['results']:
            pair = (
                '{}{}'.format(result['aromatic_residue'], result['aromatic_position']),
                'MET{}'.format(result['methionine_position'])
            )
            self.joined_pairs.add(pair)

    def compute_connected_components(self) -> bool:
        graph = Graph()
        graph.add_edges_from(self.joined_pairs)
        self.bridges = list(connected_components(graph))

        if not self.bridges:
            return False
        return True

    def get_bridges(self) -> bool:

        self.results['results'] = []

        for bridge in self.bridges:
            if len(bridge) == self.vertices:
                self.results['results'].append(bridge)

        # Note that inverse bridges (MET-ARO-MET) not removed!

        if not self.results['results']:
            return False

        return True

    def get_bridging_interactions(self, code: str, vertices: int) -> dict:
        self.code = code
        self.vertices = vertices

        if not self.run_met_aromatic():
            return self.results

        self.get_joined_pairs()

        if not self.compute_connected_components():
            return self.results

        if not self.get_bridges():
            return self.results

        return self.results
