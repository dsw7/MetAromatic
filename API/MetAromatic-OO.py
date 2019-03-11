"""
dsw7@sfu.ca

Here I narrow down the MetAromatic code into one file (for ease of use)
in addition to setting up a regression testing framework (for use
with nosetests).
"""



# dependencies
# ==============================================================================
import gzip                                         # built in
from urllib.request import urlretrieve, urlcleanup  # built in
from os             import remove, getcwd, path     # built in
from re             import search                   # built in 
from itertools      import groupby, chain           # built in 
from operator       import itemgetter               # built in 
from numpy          import array                    # external
from numpy          import sin, cos, pi             # external
from numpy          import degrees                  # external
from numpy          import linalg                   # external
from numpy          import cross                    # external
from numpy          import matmul                   # external
from numpy          import matrix                   # external
from numpy          import arccos                   # external
from numpy          import eye                      # external
from numpy          import dot                      # external
from numpy          import float64                  # external




# constants
# ==============================================================================
ROOT           = 'ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{}/{}'
ATOMS_MET      = r'CE|SD|CG' 
ATOMS_TYR      = r'CD1|CE1|CZ|CG|CD2|CE2'   
ATOMS_TRP      = r'CD2|CE3|CZ2|CH2|CZ3|CE2'  
ATOMS_PHE      = r'CD1|CE1|CZ|CG|CD2|CE2'
IDX_ATOM       = 0
IDX_CHAIN      = 4
IDX_AA         = 3
IDX_ATM_LABEL  = 2
DICT_ATOMS_PHE = {'CG':'A', 'CD2':'B', 'CE2':'C', 'CZ':'D', 'CE1':'E', 'CD1':'F'}
DICT_ATOMS_TYR = {'CG':'A', 'CD2':'B', 'CE2':'C', 'CZ':'D', 'CE1':'E', 'CD1':'F'}
DICT_ATOMS_TRP = {'CD2':'A', 'CE3':'B', 'CZ3':'C', 'CH2':'D', 'CZ2':'E', 'CE2':'F'}
SCAL1          = sin(pi / 2)
SCAL2          = 1 - cos(pi / 2)




# some universal helper functions (put into utility class?)
# ==============================================================================
def _vector_angle(u, v):
    # a routine for computing angle between two vectors
    num = dot(u, v)
    den = linalg.norm(v) * linalg.norm(u)
    return degrees(arccos(num / den))
    
def _get_hexagon_midpoints(x, y, z):
    """
    Function for computing midpoints between vertices in a hexagon
    Parameters:
        x, y, z -> list objects of x, y, and z hexagon coordinates
    Returns:
        x_mid, y_mid, z_mid -> a list of x, y, and z hexagon midpoint coordinates
    """
    
    # offset each list by 1
    x_f = x[1:] + [x[0]]
    y_f = y[1:] + [y[0]]
    z_f = z[1:] + [z[0]]

    # compute means between original and offset lists
    x_mid = [0.5 * (a + b) for a, b in zip(x, x_f)]
    y_mid = [0.5 * (a + b) for a, b in zip(y, y_f)]
    z_mid = [0.5 * (a + b) for a, b in zip(z, z_f)]
    
    return x_mid, y_mid, z_mid




# lone pair interpolation helper classes
# ==============================================================================
class RodriguesMethod:
    """
    Here I use Rodrigues' rotation formula for completing the vertices
    of a regular tetrahedron. To start, we know two vertices of a tetrahedron,
    A and B, in addition to knowing the origin O. So we map A and B to the
    origin of the frame in which the tetrahedron resides by computing
    u = A - O and v = B - O. The directions of u, v are then flipped by scaling
    u, v by -1. We then take -u, -v and rotate the vectors by 90 degrees about
    k, where k is the line of intersection between the two orthogonal planes
    of the tetrahedron. These rotated vectors now describe the position of the
    remaining coordinates C, D. We have our tetrahedron with vertices A, B,
    C, D and the origin O.
    """
    def __init__(self, vertex_a, origin, vertex_b):
        # map to origin
        vec_u = vertex_a - origin
        vec_v = vertex_b - origin
        
        # flip direction
        self.vec_u = -1 * vec_u
        self.vec_v = -1 * vec_v
        
        # we then find the vector about which we rotate
        r = 0.5 * (self.vec_u + self.vec_v)
        
        # then find unit vector of r
        r_hat = r / linalg.norm(r)
        
        # get components of the unit vector r
        r_hat_x = r_hat[0]
        r_hat_y = r_hat[1]
        r_hat_z = r_hat[2]
        
        # get the W matrix
        W = matrix([[0, -r_hat_z, r_hat_y],
                    [r_hat_z, 0, -r_hat_x],
                    [-r_hat_y, r_hat_x, 0]])
                       
        # then construct Rodrigues rotation matrix
        self.R = matrix(eye(3)) + (SCAL1 * W) + (SCAL2 * matmul(W, W))
    
    # note that I flipped these methods to match previous algorithm
    def vector_g(self):
        # get vector g - first vertex
        return matmul(self.R, self.vec_u).tolist()[0]

    def vector_a(self):
        # get vector v - second vertex
        return matmul(self.R, self.vec_v).tolist()[0]


class LonePairs:
    # a class for computing the vectors parallel to MET SD lone pairs
    # methods associated with the class complete the vertices of a tetrahedron
    # made this one in my undergrad
    
    @staticmethod  # put in static method to shorten downstream method code
    def _unit_vec(v):
        return v / linalg.norm(v)
    
    def __init__(self, terminal_a, midpoint, terminal_b):
        self.terminal_a = terminal_a
        self.midpoint = midpoint
        self.terminal_b = terminal_b
        self.u = self.terminal_a - self.midpoint  # mapping to origin
        self.v = self.terminal_b - self.midpoint  # mapping to origin
        self.NOT_vec =self. _unit_vec(-0.5 * (self._unit_vec(self.v) + self._unit_vec(self.u)))
        
    def vector_a(self):
        cross_vec = cross(self.u, self.v)
        return self.NOT_vec + 2**0.5 * self._unit_vec(cross_vec)
        
    def vector_g(self):
        cross_vec = cross(self.v, self.u)
        return self.NOT_vec + 2**0.5 * self._unit_vec(cross_vec)




# file I/O handling                                                          
# ==============================================================================
class PDBFileHandler:
    def __init__(self, code):
        """Initialize a PDBFile object with a pdb file of interest

        Parameters
        ----------
        code : the pdb code if interest
            Any valid PDB code can be passed into PDBFile.

        Examples
        --------
        >>> pdb_file = PDBFile('1rcy')  
        
        """
        self.code = code.lower()
                                                                

    def fetch_from_PDB(self):
        """
        Connects to PDB FTP server, downloads a .gz file of interest,
        decompresses the .gz file into .ent and then dumps a copy of
        the pdb{code}.ent file into cwd.

        Parameters
        ----------
        None

        Examples
        --------
        
        >>> inst = PDBFile('1rcy')
        >>> path_to_file = inst.fetch_from_PDB()
        >>> print(path_to_file)
        
        """        
            
        subdir = self.code[1:3]
        infile = 'pdb{}.ent.gz'.format(self.code)
        decompressed = infile.strip('.gz')
        fullpath = ROOT.format(subdir, infile)
        
        try:
            urlcleanup()
            urlretrieve(fullpath, infile)
        except Exception:
            return 'URLError'
        else:
            with gzip.open(infile, 'rb') as gz:
                with open(decompressed, 'wb') as out:
                    out.writelines(gz)
            remove(infile)
            return path.join(getcwd(), decompressed)
        
    def clear(self):
        """
        Deletes file from current working directory after the file has
        been processed by some algorithm.

        Parameters
        ----------
        None

        Examples
        --------
        >>> inst = PDBFile('1rcy')
        >>> path_to_file = inst.fetch_from_PDB()
        >>> print(path_to_file)  # process the file using some algorithm
        >>> inst.clear()
        
        """        
        filename = 'pdb{}.ent'.format(self.code)
        try:
            remove(path.join(getcwd(), filename))
        except FileNotFoundError:
            print('Cannot delete file. Does not exist.')
    



# ==============================================================================  
# TODO: consider refactoring this!
def met_aromatic_lowlevel(filepath, chain, cutoff=6.0, angle=109.5, model='cp'):
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
    model_first = [line for line in model_first if line[IDX_CHAIN] == chain]
    
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
        x_mid, y_mid, z_mid = _get_hexagon_midpoints(x, y, z)
        
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
        
        if model == 'cp':
            object_lonepairs = LonePairs(CG, SD, CE)
        elif model == 'rm':
            object_lonepairs = RodriguesMethod(CG, SD, CE)
        else:
            raise ValueError('Valid models are: cp, rm')    
        
        VEC_A = object_lonepairs.vector_a()
        VEC_G = object_lonepairs.vector_g()  
        
        for row in MIDPOINTS:
            VEC_V = row[2] - SD  # mapping to origin of SD
            NORM = linalg.norm(VEC_V)
            if NORM <= cutoff:  # distance condition     
                MET_THETA = _vector_angle(VEC_V, VEC_A)
                MET_PHI = _vector_angle(VEC_V, VEC_G)
                if MET_THETA <= angle or MET_PHI <= angle:  # angular condition
                    RESULT.append([row[1], row[0], ord_met[0][3], ord_met[0][5],
                                   NORM, MET_THETA, MET_PHI])
                else:
                    continue
            else:
                continue
            
    return RESULT          
    



# the main class to be called by end user
# ==============================================================================    
class MetAromatic:
    """
    Wrapper class over the MetAromatic process.
    Basic usage:
        
    >>> data = MetAromatic().met_aromatic()
    To get data using defaults (useful for testing).
        
    >>> data = MetAromatic(model='rm', cutoff=6.0).met_aromatic()
    To get data using some custom parameters.
    """
    
    # defaults for nosetests
    _CODE   = '1rcy'
    _CHAIN  = 'A'
    _CUTOFF = 4.9
    _ANGLE  = 109.5
    _MODEL  = 'cp'
    
    def __init__(self, code=_CODE, chain=_CHAIN, cutoff=_CUTOFF, angle=_ANGLE, model=_MODEL):      
        self.code   = code
        self.chain  = chain
        self.cutoff = cutoff
        self.angle  = angle
        self.model  = model
    
    def met_aromatic(self):
        pdbfile  = PDBFileHandler(self.code)                           
        filepath = pdbfile.fetch_from_PDB()
        data = met_aromatic_lowlevel(filepath,
                                     self.chain,
                                     self.cutoff,
                                     self.angle,
                                     self.model)
        pdbfile.clear()
        return data
        
    
# tests
# ==============================================================================   

_CP_DATA_FROM_APP = """
TYR 122 MET 18 4.211 75.766 64.317 
TYR 122 MET 18 3.954 60.145 68.352 
TYR 122 MET 18 4.051 47.198 85.151 
TYR 122 MET 18 4.39 53.4 95.487 
TYR 122 MET 18 4.62 68.452 90.771 
TYR 122 MET 18 4.537 78.568 76.406 
PHE 54 MET 148 4.777 105.947 143.022 
PHE 54 MET 148 4.61 93.382 156.922 
PHE 54 MET 148 4.756 93.287 154.63 
""".split()

_RM_DATA_FROM_APP = """
TYR 122 MET 18 4.211 73.168 61.503 
TYR 122 MET 18 3.954 57.237 64.226 
TYR 122 MET 18 4.051 45.097 80.768 
TYR 122 MET 18 4.39 52.505 91.841 
TYR 122 MET 18 4.62 67.558 88.251 
TYR 122 MET 18 4.537 76.865 74.377 
PHE 54 MET 148 4.61 97.467 161.871 
PHE 54 MET 148 4.756 97.225 158.761 
PHE 54 MET 148 5.052 108.845 145.122 
""".split()

def test_cp_model_defaults():
    data = MetAromatic(model='cp').met_aromatic()
    data = list(chain(*data))  
    
    # truncate in place
    for i in range(0, len(data)):
        if type(data[i]) == float64:
            data[i] = round(data[i], 3)
    
    # convert ewerything to str dtype to match _CP_* and _RM_* above
    data = [str(i) for i in data]
   
    assert set(data) == set(_CP_DATA_FROM_APP)
  
    
def test_rm_model_defaults():
    data = MetAromatic(model='rm', cutoff=6.0).met_aromatic()
    data = list(chain(*data))  
    
    # truncate in place
    for i in range(0, len(data)):
        if type(data[i]) == float64:
            data[i] = round(data[i], 3)
    
    # convert ewerything to str dtype to match _CP_* and _RM_* above
    data = [str(i) for i in data]
   
    assert set(data) == set(_RM_DATA_FROM_APP)
    
    
def tests_cp_2eph(test_entry='2eph'):
    # fetch and process data from MetAromatic application
    # ---------------------------------------------------
    with open(r'regression_data\{}_cp.txt'.format(test_entry)) as f:
        data = f.readlines()
    
    data = [line.split() for line in data if 'RESULT' in line and 'MET' in line]
    data = [line[1:] for line in data]
    data = set(list(chain(*data)))
    
    # fetch and process data from MetAromatic class
    # ---------------------------------------------------
    data2 = MetAromatic(code=test_entry, model='cp', cutoff=5.5).met_aromatic()
    data2 = list(chain(*data2))  
    
    # truncate in place
    for i in range(0, len(data2)):
        if type(data2[i]) == float64:
            data2[i] = round(data2[i], 3)
    
    data2 = set([str(i) for i in data2]) 
    
    # compare
    assert data == data2


def tests_cp_2rcy(test_entry='2rcy'):
    # fetch and process data from MetAromatic application
    # ---------------------------------------------------
    with open(r'regression_data\{}_cp.txt'.format(test_entry)) as f:
        data = f.readlines()
    
    data = [line.split() for line in data if 'RESULT' in line and 'MET' in line]
    data = [line[1:] for line in data]
    data = set(list(chain(*data)))
    
    # fetch and process data from MetAromatic class
    # ---------------------------------------------------
    data2 = MetAromatic(code=test_entry, model='cp', cutoff=5.5).met_aromatic()
    data2 = list(chain(*data2))  
    
    # truncate in place
    for i in range(0, len(data2)):
        if type(data2[i]) == float64:
            data2[i] = round(data2[i], 3)
    
    data2 = set([str(i) for i in data2]) 
    
    # compare
    assert data == data2


def tests_cp_3uiy(test_entry='3uiy'):
    # fetch and process data from MetAromatic application
    # ---------------------------------------------------
    with open(r'regression_data\{}_cp.txt'.format(test_entry)) as f:
        data = f.readlines()
    
    data = [line.split() for line in data if 'RESULT' in line and 'MET' in line]
    data = [line[1:] for line in data]
    data = set(list(chain(*data)))
    
    # fetch and process data from MetAromatic class
    # ---------------------------------------------------
    data2 = MetAromatic(code=test_entry, model='cp', cutoff=5.5).met_aromatic()
    data2 = list(chain(*data2))  
    
    # truncate in place
    for i in range(0, len(data2)):
        if type(data2[i]) == float64:
            data2[i] = round(data2[i], 3)
    
    data2 = set([str(i) for i in data2]) 
    
    # compare
    assert data == data2


def tests_cp_4bpj(test_entry='4bpj'):
    # fetch and process data from MetAromatic application
    # ---------------------------------------------------
    with open(r'regression_data\{}_cp.txt'.format(test_entry)) as f:
        data = f.readlines()
    
    data = [line.split() for line in data if 'RESULT' in line and 'MET' in line]
    data = [line[1:] for line in data]
    data = set(list(chain(*data)))
    
    # fetch and process data from MetAromatic class
    # ---------------------------------------------------
    data2 = MetAromatic(code=test_entry, model='cp', cutoff=5.5).met_aromatic()
    data2 = list(chain(*data2))  
    
    # truncate in place
    for i in range(0, len(data2)):
        if type(data2[i]) == float64:
            data2[i] = round(data2[i], 3)
    
    data2 = set([str(i) for i in data2]) 
    
    # compare
    assert data == data2
    

def tests_cp_4orh(test_entry='4orh'):
    # fetch and process data from MetAromatic application
    # ---------------------------------------------------
    with open(r'regression_data\{}_cp.txt'.format(test_entry)) as f:
        data = f.readlines()
    
    data = [line.split() for line in data if 'RESULT' in line and 'MET' in line]
    data = [line[1:] for line in data]
    data = set(list(chain(*data)))
    
    # fetch and process data from MetAromatic class
    # ---------------------------------------------------
    data2 = MetAromatic(code=test_entry, model='cp', cutoff=5.5).met_aromatic()
    data2 = list(chain(*data2))  
    
    # truncate in place
    for i in range(0, len(data2)):
        if type(data2[i]) == float64:
            data2[i] = round(data2[i], 3)
    
    data2 = set([str(i) for i in data2]) 
    
    # compare
    assert data == data2
    

def tests_rm_2eph(test_entry='2eph'):
    # fetch and process data from MetAromatic application
    # ---------------------------------------------------
    with open(r'regression_data\{}_rm.txt'.format(test_entry)) as f:
        data = f.readlines()
    
    data = [line.split() for line in data if 'RESULT' in line and 'MET' in line]
    data = [line[1:] for line in data]
    data = set(list(chain(*data)))
    
    # fetch and process data from MetAromatic class
    # ---------------------------------------------------
    data2 = MetAromatic(code=test_entry, model='rm', cutoff=5.5).met_aromatic()
    data2 = list(chain(*data2))  
    
    # truncate in place
    for i in range(0, len(data2)):
        if type(data2[i]) == float64:
            data2[i] = round(data2[i], 3)
    
    data2 = set([str(i) for i in data2]) 
    
    # compare
    assert data == data2


def tests_rm_2rcy(test_entry='2rcy'):
    # fetch and process data from MetAromatic application
    # ---------------------------------------------------
    with open(r'regression_data\{}_rm.txt'.format(test_entry)) as f:
        data = f.readlines()
    
    data = [line.split() for line in data if 'RESULT' in line and 'MET' in line]
    data = [line[1:] for line in data]
    data = set(list(chain(*data)))
    
    # fetch and process data from MetAromatic class
    # ---------------------------------------------------
    data2 = MetAromatic(code=test_entry, model='rm', cutoff=5.5).met_aromatic()
    data2 = list(chain(*data2))  
    
    # truncate in place
    for i in range(0, len(data2)):
        if type(data2[i]) == float64:
            data2[i] = round(data2[i], 3)
    
    data2 = set([str(i) for i in data2]) 
    
    # compare
    assert data == data2


def tests_rm_3uiy(test_entry='3uiy'):
    # fetch and process data from MetAromatic application
    # ---------------------------------------------------
    with open(r'regression_data\{}_rm.txt'.format(test_entry)) as f:
        data = f.readlines()
    
    data = [line.split() for line in data if 'RESULT' in line and 'MET' in line]
    data = [line[1:] for line in data]
    data = set(list(chain(*data)))
    
    # fetch and process data from MetAromatic class
    # ---------------------------------------------------
    data2 = MetAromatic(code=test_entry, model='rm', cutoff=5.5).met_aromatic()
    data2 = list(chain(*data2))  
    
    # truncate in place
    for i in range(0, len(data2)):
        if type(data2[i]) == float64:
            data2[i] = round(data2[i], 3)
    
    data2 = set([str(i) for i in data2]) 
    
    # compare
    assert data == data2


def tests_rm_4bpj(test_entry='4bpj'):
    # fetch and process data from MetAromatic application
    # ---------------------------------------------------
    with open(r'regression_data\{}_rm.txt'.format(test_entry)) as f:
        data = f.readlines()
    
    data = [line.split() for line in data if 'RESULT' in line and 'MET' in line]
    data = [line[1:] for line in data]
    data = set(list(chain(*data)))
    
    # fetch and process data from MetAromatic class
    # ---------------------------------------------------
    data2 = MetAromatic(code=test_entry, model='rm', cutoff=5.5).met_aromatic()
    data2 = list(chain(*data2))  
    
    # truncate in place
    for i in range(0, len(data2)):
        if type(data2[i]) == float64:
            data2[i] = round(data2[i], 3)
    
    data2 = set([str(i) for i in data2]) 
    
    # compare
    assert data == data2
    

def tests_rm_4orh(test_entry='4orh'):
    # fetch and process data from MetAromatic application
    # ---------------------------------------------------
    with open(r'regression_data\{}_rm.txt'.format(test_entry)) as f:
        data = f.readlines()
    
    data = [line.split() for line in data if 'RESULT' in line and 'MET' in line]
    data = [line[1:] for line in data]
    data = set(list(chain(*data)))
    
    # fetch and process data from MetAromatic class
    # ---------------------------------------------------
    data2 = MetAromatic(code=test_entry, model='rm', cutoff=5.5).met_aromatic()
    data2 = list(chain(*data2))  
    
    # truncate in place
    for i in range(0, len(data2)):
        if type(data2[i]) == float64:
            data2[i] = round(data2[i], 3)
    
    data2 = set([str(i) for i in data2]) 
    
    # compare
    assert data == data2


    
    
# main
# ==============================================================================    
if __name__ == '__main__':
    test_cp_model_defaults()
    test_rm_model_defaults()
    tests_cp_2eph()
    tests_cp_2rcy()
    tests_cp_3uiy()
    tests_cp_4bpj()
    tests_cp_4orh()
    tests_rm_2eph()
    tests_rm_2rcy()
    tests_rm_3uiy()
    tests_rm_4bpj()
    tests_rm_4orh()
