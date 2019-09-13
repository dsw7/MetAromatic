# Written by David Weber
# dsw7@sfu.ca

"""
A low level implementation of the Met-Aromatic algorithm. I wrote this mainly
as an alternative to the more high level Pandas/BioPython implementation
of the algorithm. Here I mostly use built in libraries. The main function is
a bit long, which is an antipattern in a sense, however the script works very
well. This script would be well suited for use in large mining jobs as the
main function can be imported into a separate workspace.
"""

# ------------------------------------------------------------------------------

import methods                                      # local in sys.path
from re             import search                   # built in 
from itertools      import groupby                  # built in 
from operator       import itemgetter               # built in 
from numpy          import array                    # external
from numpy.linalg   import norm                     # external

ATOMS_MET = r'CE|SD|CG' 
ATOMS_TYR = r'CD1|CE1|CZ|CG|CD2|CE2'   
ATOMS_TRP = r'CD2|CE3|CZ2|CH2|CZ3|CE2'  
ATOMS_PHE = r'CD1|CE1|CZ|CG|CD2|CE2'
IDX_ATOM = 0
IDX_CHAIN = 4
IDX_AA = 3
IDX_ATM_LABEL = 2

DICT_ATOMS_PHE = {
                 'CG':'A', 'CD2':'B', 'CE2':'C', 
                 'CZ':'D', 'CE1':'E', 'CD1':'F'
                 }

DICT_ATOMS_TYR = {
                 'CG':'A', 'CD2':'B', 'CE2':'C', 
                 'CZ':'D', 'CE1':'E', 'CD1':'F'
                 }

DICT_ATOMS_TRP = {
                 'CD2':'A', 'CE3':'B', 'CZ3':'C', 
                 'CH2':'D', 'CZ2':'E', 'CE2':'F'
                 }

# ------------------------------------------------------------------------------

def met_aromatic(filepath, CHAIN, CUTOFF=6.0, ANGLE=109.5, MODEL='cp'):
    """
    Function runs the Met-Aromatic algorithm on a PDB structure
        Params:
            CHAIN      -> 'A', 'B', 'C', etc, str
            CUTOFF     -> cutoff distance ||v||, float
            ANGLE      -> cutoff angle, float
            MODEL      -> 'cp' or 'rm' for Cross Product or Rodrigues Method, str
            filepath   -> path to pdb .ent file
        Returns:
            A nested list of met-aromatic algorithm data
    """
    
    # open file if file successfully retrieved
    with open(filepath, 'r') as f:
        data_incoming = f.readlines()
     
    # chunk lines 
    data = [line.split() for line in data_incoming]
    
    # stop at end of first model - fix for bug in v1.3
    model_first = []
    for line in data:
        if line[IDX_ATOM] != 'ENDMDL':
            model_first.append(line)
        else:
            break
        
    # get only ATOM records
    model_first = [line for line in model_first if line[IDX_ATOM] == 'ATOM']
    
    # get only specific chains
    model_first = [line for line in model_first if line[IDX_CHAIN] == CHAIN]
    
    # strip down to specific residues
    DATA_MET = [line for line in model_first if line[IDX_AA] == 'MET']
    DATA_PHE = [line for line in model_first if line[IDX_AA] == 'PHE']
    DATA_TYR = [line for line in model_first if line[IDX_AA] == 'TYR']
    DATA_TRP = [line for line in model_first if line[IDX_AA] == 'TRP']
    
    # strip down to specific atoms using regex
    DATA_MET = [line for line in DATA_MET if search(ATOMS_MET, line[IDX_ATM_LABEL]) != None]
    DATA_PHE = [line for line in DATA_PHE if search(ATOMS_PHE, line[IDX_ATM_LABEL]) != None]
    DATA_TYR = [line for line in DATA_TYR if search(ATOMS_TYR, line[IDX_ATM_LABEL]) != None]
    DATA_TRP = [line for line in DATA_TRP if search(ATOMS_TRP, line[IDX_ATM_LABEL]) != None]
    
    # sort data prior to applying groupby operations
    DATA_ARO = DATA_PHE + DATA_TYR + DATA_TRP
    DATA_ARO = sorted(DATA_ARO, key=itemgetter(5))  # note lexicographic ordering
    
    # apply groupby operator
    DATA_ARO = [list(group) for _, group in groupby(DATA_ARO, lambda x: x[5])]                
    
    # get midpoints
    MIDPOINTS = []
    for grouped in DATA_ARO:
        # map unique values to atomic label keys
        for row in grouped:
            if row[3] == 'PHE':
                row[2] = DICT_ATOMS_PHE.get(row[2])
            elif row[3] == 'TYR':
                row[2] = DICT_ATOMS_TYR.get(row[2])
            else:
                row[2] = DICT_ATOMS_TRP.get(row[2])
        
        # then sort based on these values which are just A, B, C, D, E, F
        ordered = sorted(grouped, key=itemgetter(2))
        
        # isolate x, y, z
        x = [float(i[6]) for i in ordered]
        y = [float(i[7]) for i in ordered]
        z = [float(i[8]) for i in ordered]
        
        # get hexagon midpoints
        x_mid, y_mid, z_mid = methods.get_hexagon_midpoints(x, y, z)
        
        for a, b, c in zip(x_mid, y_mid, z_mid):
            MIDPOINTS.append([ordered[0][5], ordered[0][3], array([a, b, c])])
            
    RESULT = []
    
    # apply distance and angular conditions 
    for key, grouped_met in groupby(DATA_MET, lambda x: x[5]):
        # guarantees the order of methionine data
        ord_met = sorted(list(grouped_met), key=itemgetter(2))
        
        CE = array(ord_met[0][6:9]).astype(float)
        CG = array(ord_met[1][6:9]).astype(float)
        SD = array(ord_met[2][6:9]).astype(float)
        
        if MODEL == 'cp':
            object_lonepairs = methods.LonePairs(CG, SD, CE)
        elif MODEL == 'rm':
            object_lonepairs = methods.RodriguesMethod(CG, SD, CE)
        else:
            raise ValueError('Valid models are: cp, rm')    
        
        VEC_A = object_lonepairs.vector_a()
        VEC_G = object_lonepairs.vector_g()  
        
        for row in MIDPOINTS:
            VEC_V = row[2] - SD  # mapping to origin of SD
            NORM = norm(VEC_V)
            if NORM <= CUTOFF:  # distance condition     
                MET_THETA = methods.vector_angle(VEC_V, VEC_A)
                MET_PHI = methods.vector_angle(VEC_V, VEC_G)
                if MET_THETA <= ANGLE or MET_PHI <= ANGLE:  # angular condition
                    RESULT.append([row[1], row[0], ord_met[0][3], ord_met[0][5],
                                   NORM, MET_THETA, MET_PHI])
                else:
                    continue
            else:
                continue
            
    return RESULT          
                
                
