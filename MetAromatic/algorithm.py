from itertools import groupby
from operator import itemgetter
from re import match
from numpy import array, linalg
from .errors import SearchError
from .get_aromatic_midpoints import (
    get_phe_midpoints,
    get_trp_midpoints,
    get_tyr_midpoints,
)
from .lone_pair_interpolators import CrossProductMethod, RodriguesMethod
from .models import MetAromaticParams, FeatureSpace, LonePairs, Interactions
from .utils import get_angle_between_vecs, get_search_pattern
from .aliases import RawData, FloatArray


class MetAromatic:

    def __init__(self, params: MetAromaticParams, raw_data: RawData) -> None:
        self.params = params
        self.raw_data = raw_data
        self.f: FeatureSpace

    def get_first_model(self) -> None:
        for line in self.raw_data:
            if "ENDMDL" in line:
                break

            self.f.first_model.append(line)

    def get_met_coordinates(self) -> None:
        pattern = get_search_pattern(res="met", chain=self.params.chain)

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_met.append(line.split()[:9])

        if len(self.f.coords_met) == 0:
            raise SearchError("No MET residues")

    def get_phe_coordinates(self) -> None:
        pattern = get_search_pattern(res="phe", chain=self.params.chain)

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_phe.append(line.split()[:9])

    def get_tyr_coordinates(self) -> None:
        pattern = get_search_pattern(res="tyr", chain=self.params.chain)

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_tyr.append(line.split()[:9])

    def get_trp_coordinates(self) -> None:
        pattern = get_search_pattern(res="trp", chain=self.params.chain)

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_trp.append(line.split()[:9])

    def get_met_lone_pairs_cp(self) -> None:
        for position, groups in groupby(self.f.coords_met, lambda entry: entry[5]):
            ordered = sorted(list(groups), key=itemgetter(2))

            coords_ce: FloatArray = array(ordered[0][6:9]).astype(float)
            coords_cg: FloatArray = array(ordered[1][6:9]).astype(float)
            coords_sd: FloatArray = array(ordered[2][6:9]).astype(float)

            lp = CrossProductMethod(coords_cg, coords_sd, coords_ce)

            self.f.lone_pairs_met.append(
                LonePairs(
                    coords_sd=coords_sd,
                    position=position,
                    vector_a=lp.get_vector_a(),
                    vector_g=lp.get_vector_g(),
                )
            )

    def get_met_lone_pairs_rm(self) -> None:
        for position, groups in groupby(self.f.coords_met, lambda entry: entry[5]):
            ordered = sorted(list(groups), key=itemgetter(2))

            coords_ce: FloatArray = array(ordered[0][6:9]).astype(float)
            coords_cg: FloatArray = array(ordered[1][6:9]).astype(float)
            coords_sd: FloatArray = array(ordered[2][6:9]).astype(float)

            lp = RodriguesMethod(coords_cg, coords_sd, coords_ce)

            self.f.lone_pairs_met.append(
                LonePairs(
                    coords_sd=coords_sd,
                    position=position,
                    vector_a=lp.get_vector_a(),
                    vector_g=lp.get_vector_g(),
                )
            )

    def get_midpoints(self) -> None:
        self.f.midpoints_phe = get_phe_midpoints(self.f.coords_phe)
        self.f.midpoints_tyr = get_tyr_midpoints(self.f.coords_tyr)
        self.f.midpoints_trp = get_trp_midpoints(self.f.coords_trp)

    def apply_met_aromatic_criteria(self) -> None:
        midpoints = self.f.midpoints_phe + self.f.midpoints_tyr + self.f.midpoints_trp

        for lone_pair in self.f.lone_pairs_met:
            for midpoint in midpoints:
                vector_v: FloatArray = midpoint[2] - lone_pair.coords_sd
                norm_vector_v: float = linalg.norm(vector_v).item()

                if norm_vector_v > self.params.cutoff_distance:
                    continue

                met_theta_angle = get_angle_between_vecs(vector_v, lone_pair.vector_a)
                met_phi_angle = get_angle_between_vecs(vector_v, lone_pair.vector_g)

                if (met_theta_angle > self.params.cutoff_angle) and (
                    met_phi_angle > self.params.cutoff_angle
                ):
                    continue

                self.f.interactions.append(
                    Interactions(
                        aromatic_position=int(midpoint[0]),
                        aromatic_residue=midpoint[1],
                        met_phi_angle=round(met_phi_angle, 3),
                        met_theta_angle=round(met_theta_angle, 3),
                        methionine_position=int(lone_pair.position),
                        norm=round(norm_vector_v, 3),
                    )
                )

    def get_interactions(self) -> FeatureSpace:
        self.f = FeatureSpace()

        self.get_first_model()
        self.get_met_coordinates()
        self.get_phe_coordinates()
        self.get_tyr_coordinates()
        self.get_trp_coordinates()

        if len(self.f.coords_phe + self.f.coords_tyr + self.f.coords_trp) == 0:
            raise SearchError("No PHE/TYR/TRP residues")

        if self.params.model == "cp":
            self.get_met_lone_pairs_cp()
        else:
            self.get_met_lone_pairs_rm()

        self.get_midpoints()
        self.apply_met_aromatic_criteria()

        if len(self.f.interactions) == 0:
            raise SearchError("No Met-aromatic interactions")

        return self.f
