ATOMS_MET = r'CE|SD|CG'
ATOMS_TYR = r'CD1|CE1|CZ|CG|CD2|CE2'
ATOMS_TRP = r'CD2|CE3|CZ2|CH2|CZ3|CE2'
ATOMS_PHE = r'CD1|CE1|CZ|CG|CD2|CE2'

def pattern_regex_met(chain):
    return fr'(ATOM.*({ATOMS_MET})\s+MET\s+{chain}\s)'

def pattern_regex_phe(chain):
    return fr'(ATOM.*({ATOMS_PHE})\s+PHE\s+{chain}\s)'

def pattern_regex_tyr(chain):
    return fr'(ATOM.*({ATOMS_TYR})\s+TYR\s+{chain}\s)'

def pattern_regex_trp(chain):
    return fr'(ATOM.*({ATOMS_TRP})\s+TRP\s+{chain}\s)'
