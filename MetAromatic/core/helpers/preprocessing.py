from re import match

ATOMS_MET = r'CE|SD|CG'
ATOMS_TYR = r'CD1|CE1|CZ|CG|CD2|CE2'
ATOMS_TRP = r'CD2|CE3|CZ2|CH2|CZ3|CE2'
ATOMS_PHE = r'CD1|CE1|CZ|CG|CD2|CE2'

def pattern_regex_met(chain: str) -> str:
    return r'(ATOM.*({})\s+MET\s+{}\s)'.format(ATOMS_MET, chain)

def pattern_regex_phe(chain: str) -> str:
    return r'(ATOM.*({})\s+PHE\s+{}\s)'.format(ATOMS_PHE, chain)

def pattern_regex_tyr(chain: str) -> str:
    return r'(ATOM.*({})\s+TYR\s+{}\s)'.format(ATOMS_TYR, chain)

def pattern_regex_trp(chain: str) -> str:
    return r'(ATOM.*({})\s+TRP\s+{}\s)'.format(ATOMS_TRP, chain)

def get_relevant_met_coordinates(first_model: list, chain: str) -> list:
    return [line.split()[:9] for line in first_model if match(pattern_regex_met(chain), line)]

def get_relevant_phe_coordinates(first_model: list, chain: str) -> list:
    return [line.split()[:9] for line in first_model if match(pattern_regex_phe(chain), line)]

def get_relevant_tyr_coordinates(first_model: list, chain: str) -> list:
    return [line.split()[:9] for line in first_model if match(pattern_regex_tyr(chain), line)]

def get_relevant_trp_coordinates(first_model: list, chain: str) -> list:
    return [line.split()[:9] for line in first_model if match(pattern_regex_trp(chain), line)]
