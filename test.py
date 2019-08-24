# delete this eventually
# test that old data matches new data
# time

from sys                    import path as PATH; PATH.append('./utils')  # built in
from time                   import time                                  # built in
from ma_lowlevel            import met_aromatic                          # local
from PDB_filegetter         import PDBFile                               # local
from ma                     import MetAromatic 

CODE = '1rcy'
CHAIN = "A"
CUTOFF = 4.9
ANGLE = 109.5

t_start = time()
file_PDB = PDBFile(CODE)
path_to_file = file_PDB.fetch_from_PDB()
data_old = met_aromatic(filepath=path_to_file, CHAIN=CHAIN, CUTOFF=CUTOFF, ANGLE=ANGLE, MODEL="cp")
file_PDB.clear()
t_end = time()
print('Old: ', t_end - t_start)

t_start = time()
data_new = MetAromatic(CODE, CHAIN, CUTOFF, ANGLE).met_aromatic()
t_end = time()
print('New: ', t_end - t_start)

assert data_new == data_old
