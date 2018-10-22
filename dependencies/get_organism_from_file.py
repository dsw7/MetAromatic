# Written by David Weber
# dsw7@sfu.ca

"""
In this short namespace I house a function that attempts to find source
organism from a PDB .ent file
"""

# ------------------------------------------------------------------------------

def get_organism(filename):
    """ get organism from PDB file
    
    Parameters
    ----------
    filename : name of PDB .ent file in pwd
    
    Returns
    -------
    organism : a list of str type binomial nomenclature names for organisms
    """
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    linesA = [line.split() for line in lines]
    linesB = [line for line in linesA if 'SOURCE' in line]
    linesC = [line for line in linesB if 'ORGANISM_SCIENTIFIC:' in line]
    
    organism = []
    for item in linesC:
        idx = item.index('ORGANISM_SCIENTIFIC:')
        out_str = '{} ' * len(item[idx + 1:])
        organism.append(out_str.format(*item[idx + 1:]))
        
    return organism
        
