# Written by David Weber
# dsw7@sfu.ca

"""
In this short namespace I house a function attempts to find EC classifier from
an .ent PDB file
"""

# ------------------------------------------------------------------------------

from re import search

def get_EC_classifier(filepath):
    """
    A short function for fetching EC classifier
        Parameters   -> path to PDB .ent file
        Returns      -> EC classifier, str type else None if EC classifier DNE
    """
    with open(filepath, 'r') as f:
        data = f.readlines()
        
    data = [line for line in data if search('COMPND', line) != None]
    data = [line for line in data if search('EC: ', line) != None]
    if data == []:
        return None
    else:
        data = data[0].split()
        return data[data.index('EC:') + 1].strip(';')