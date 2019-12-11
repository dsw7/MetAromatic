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
from sys            import path; path.append('..')
from utils          import get_hexagon_midpoints, vector_angle, LonePairs, RodriguesMethod
from filegetter     import PDBFile           
from re             import search                   
from itertools      import groupby                  
from operator       import itemgetter               
from numpy          import array                   
from numpy.linalg   import norm                    

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
def met_aromatic(filepath, chain='A', cutoff=6.0, angle=109.5, model='cp'):
    """
    Function runs the Met-Aromatic algorithm on a PDB structure
        Params:
            chain      -> 'A', 'B', 'C', etc, str
            cutoff     -> cutoff distance ||v||, float
            angle      -> cutoff angle, float
            model      -> 'cp' or 'rm' for Cross Product or Rodrigues Method, str
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
    model_first = [line for line in model_first if line[IDX_CHAIN] == chain]
    
    # strip down to specific residues
    data_met = [line for line in model_first if line[IDX_AA] == 'MET']
    data_phe = [line for line in model_first if line[IDX_AA] == 'PHE']
    data_tyr = [line for line in model_first if line[IDX_AA] == 'TYR']
    data_trp = [line for line in model_first if line[IDX_AA] == 'TRP']
    
    # strip down to specific atoms using regex
    data_met = [line for line in data_met if search(ATOMS_MET, line[IDX_ATM_LABEL]) != None]
    data_phe = [line for line in data_phe if search(ATOMS_PHE, line[IDX_ATM_LABEL]) != None]
    data_tyr = [line for line in data_tyr if search(ATOMS_TYR, line[IDX_ATM_LABEL]) != None]
    data_trp = [line for line in data_trp if search(ATOMS_TRP, line[IDX_ATM_LABEL]) != None]
    
    # sort data prior to applying groupby operations
    data_aro = data_phe + data_tyr + data_trp
    data_aro = sorted(data_aro, key=itemgetter(5))  # note lexicographic ordering
    
    # apply groupby operator
    data_aro = [list(group) for _, group in groupby(data_aro, lambda x: x[5])]                
    
    # get midpoints
    midpoints = []
    for grouped in data_aro:
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
        x_mid, y_mid, z_mid = get_hexagon_midpoints(x, y, z)
        
        for a, b, c in zip(x_mid, y_mid, z_mid):
            midpoints.append([ordered[0][5], ordered[0][3], array([a, b, c])])
            
    result = []
    
    # apply distance and angular conditions 
    for key, grouped_met in groupby(data_met, lambda x: x[5]):
        # guarantees the order of methionine data
        ord_met = sorted(list(grouped_met), key=itemgetter(2))
        
        CE = array(ord_met[0][6:9]).astype(float)
        CG = array(ord_met[1][6:9]).astype(float)
        SD = array(ord_met[2][6:9]).astype(float)
        
        if model == 'cp':
            object_lonepairs = LonePairs(CG, SD, CE)
        elif model == 'rm':
            object_lonepairs = RodriguesMethod(CG, SD, CE)
        else:
            raise ValueError('Valid models are: cp, rm')    
        
        vec_a = object_lonepairs.vector_a()
        vec_g = object_lonepairs.vector_g()      
        
        for row in midpoints:
            vec_v = row[2] - SD  # mapping to origin of SD
            norm_vec_v = norm(vec_v)
            if norm_vec_v <= cutoff:  # distance condition           
                met_theta = vector_angle(vec_v, vec_a)
                met_phi = vector_angle(vec_v, vec_g)
                if met_theta <= angle or met_phi <= angle:  # angular condition
                    result.append([row[1], row[0], ord_met[0][3], ord_met[0][5],
                                   norm_vec_v, met_theta, met_phi])
                else:
                    continue
            else:
                continue
            
    return result


def run_met_aromatic(code, chain='A', cutoff=6.0, angle=109.5, model='cp'):
    object_pdb_file = PDBFile(code)
    filepath = object_pdb_file.fetch_from_pdb()
    results = met_aromatic(filepath, chain=chain, cutoff=cutoff, angle=angle, model=model)
    object_pdb_file.clear()
    return results

                
