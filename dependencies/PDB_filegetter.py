# Written by David Weber
# dsw7@sfu.ca

"""
In this short namespace I house a class that connects to PDB and downloads
file over PDB file transfer protocol.
"""

# ------------------------------------------------------------------------------

import gzip
from urllib.request import urlretrieve, urlcleanup  # built in
from os             import remove, getcwd, path     # built in

ROOT = 'ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{}/{}'

class PDBFile:
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
    
    
