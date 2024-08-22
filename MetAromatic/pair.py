from abc import ABC, abstractmethod
from gzip import open as gz_open
from itertools import groupby
from logging import getLogger
from operator import itemgetter
from os import path
from re import match
from tempfile import NamedTemporaryFile
from urllib.error import URLError
from urllib.request import urlretrieve, urlcleanup
from numpy import array, linalg
from .consts import TMPDIR
from .errors import SearchError
from .get_aromatic_midpoints import (
    get_phe_midpoints,
    get_trp_midpoints,
    get_tyr_midpoints,
)
from .lone_pair_interpolators import CrossProductMethod, RodriguesMethod
from .models import MetAromaticParams, FeatureSpace, LonePairs, Interactions
from .utils import get_angle_between_vecs, get_search_pattern


class MetAromaticBase(ABC):
    log = getLogger("met-aromatic")

    def __init__(self, params: MetAromaticParams) -> None:
        self.params = params
        self.f: FeatureSpace

    @abstractmethod
    def load_pdb_file(self, source: str) -> bool:
        pass

    def get_first_model(self) -> None:
        self.log.debug("Stripping feature space down to only first model")

        for line in self.f.raw_data:
            if "ENDMDL" in line:
                break

            self.f.first_model.append(line)

    def get_met_coordinates(self) -> None:
        self.log.debug("Isolating MET coordinates from feature space")

        pattern = get_search_pattern(res="met", chain=self.params.chain)

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_met.append(line.split()[:9])

        if len(self.f.coords_met) == 0:
            raise SearchError("No MET residues")

    def get_phe_coordinates(self) -> None:
        self.log.debug("Isolating PHE coordinates from feature space")
        pattern = get_search_pattern(res="phe", chain=self.params.chain)

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_phe.append(line.split()[:9])

    def get_tyr_coordinates(self) -> None:
        self.log.debug("Isolating TYR coordinates from feature space")
        pattern = get_search_pattern(res="tyr", chain=self.params.chain)

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_tyr.append(line.split()[:9])

    def get_trp_coordinates(self) -> None:
        self.log.debug("Isolating TRP coordinates from feature space")
        pattern = get_search_pattern(res="trp", chain=self.params.chain)

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_trp.append(line.split()[:9])

    def check_if_not_coordinates(self) -> bool:
        self.log.debug(
            "Ensuring that at least one aromatic residue exists in feature space"
        )

        if not any([self.f.coords_phe, self.f.coords_tyr, self.f.coords_trp]):
            self.log.error("No aromatic residues found for entry")
            self.f.status = "No PHE/TYR/TRP residues"
            self.f.OK = False
            return False

        return True

    def get_met_lone_pairs_cp(self) -> None:
        for position, groups in groupby(self.f.coords_met, lambda entry: entry[5]):
            ordered = sorted(list(groups), key=itemgetter(2))

            coords_ce = array(ordered[0][6:9]).astype(float)
            coords_cg = array(ordered[1][6:9]).astype(float)
            coords_sd = array(ordered[2][6:9]).astype(float)

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

            coords_ce = array(ordered[0][6:9]).astype(float)
            coords_cg = array(ordered[1][6:9]).astype(float)
            coords_sd = array(ordered[2][6:9]).astype(float)

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
        self.log.debug("Computing midpoints between PHE aromatic carbon atoms")
        self.f.midpoints_phe = get_phe_midpoints(self.f.coords_phe)

        self.log.debug("Computing midpoints between TYR aromatic carbon atoms")
        self.f.midpoints_tyr = get_tyr_midpoints(self.f.coords_tyr)

        self.log.debug("Computing midpoints between TRP aromatic carbon atoms")
        self.f.midpoints_trp = get_trp_midpoints(self.f.coords_trp)

    def apply_met_aromatic_criteria(self) -> None:
        self.log.debug(
            "Finding pairs meeting Met-aromatic algorithm criteria in feature space"
        )

        midpoints = self.f.midpoints_phe + self.f.midpoints_tyr + self.f.midpoints_trp

        for lone_pair in self.f.lone_pairs_met:
            for midpoint in midpoints:
                vector_v = midpoint[2] - lone_pair.coords_sd
                norm_vector_v = linalg.norm(vector_v)

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
                        # Variable norm_vector_v is of type numpy.float64
                        # and so round() returns a numpy.float64
                        # which causes mypy to complain. So cast norm_vector_v to float
                        norm=round(float(norm_vector_v), 3),
                    )
                )

        if len(self.f.interactions) == 0:
            self.log.info("Found no Met-aromatic interactions for entry")
            self.f.status = "No interactions"

    def get_met_aromatic_interactions(self, source: str) -> FeatureSpace:
        self.f = FeatureSpace()

        if not self.load_pdb_file(source=source):
            return self.f

        self.get_first_model()
        self.get_met_coordinates()

        self.get_phe_coordinates()
        self.get_tyr_coordinates()
        self.get_trp_coordinates()

        if not self.check_if_not_coordinates():
            return self.f

        self.log.debug(
            'Computing MET lone pair positions using "%s" model', self.params.model
        )
        if self.params.model == "cp":
            self.get_met_lone_pairs_cp()
        else:
            self.get_met_lone_pairs_rm()

        self.get_midpoints()
        self.apply_met_aromatic_criteria()

        return self.f


class MetAromatic(MetAromaticBase):
    def load_pdb_file(self, source: str) -> bool:
        self.log.debug('Fetching PDB file "%s"', source)

        code = source.lower()

        ent_gz = f"pdb{code}.ent.gz"
        ftp_url = f"ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{code[1:3]}/{ent_gz}"

        self.log.debug('Accessing URL: "%s"', ftp_url)

        with NamedTemporaryFile(dir=TMPDIR) as f:
            try:
                urlcleanup()
                urlretrieve(ftp_url, f.name)
            except URLError:
                self.log.error('Invalid PDB entry "%s"', code)

                self.f.status = "Invalid PDB entry"
                self.f.OK = False
                return False

            with gz_open(f.name, "rt") as gz:
                for line in gz:
                    self.f.raw_data.append(line)

        return True


class MetAromaticLocal(MetAromaticBase):
    def load_pdb_file(self, source: str) -> bool:
        self.log.debug('Reading local file "%s"', source)

        if not path.exists(source):
            errmsg = f'File "{source}" does not exist'
            self.log.error(errmsg)

            self.f.status = errmsg
            self.f.OK = False

            return False

        for line in open(source):
            self.f.raw_data.append(line)

        return True
