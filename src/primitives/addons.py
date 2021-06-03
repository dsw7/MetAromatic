from re import search


def get_ec_classifier(first_model):
    """ COMPND   5 EC: 6.1.1.13; -> 6.1.1.13 """
    for line in first_model:
        if search(r'COMPND.*EC:', line):
            return search(r'(?<=: )(.*)(?=;)', line).group(0)

def get_protein_identity(first_model):
    """ COMPND   2 MOLECULE: D-ALANINE; -> D-ALANINE """
    for line in first_model:
        if search(r'COMPND.*MOLECULE:', line):
            return search('(?<=: ).*?(?=;|\n)', line).group(0)

def get_organism(first_model):
    """ SOURCE   2 ORGANISM_SCIENTIFIC: B. SUBTILIS; -> B. SUBTILIS """
    for line in first_model:
        if search(r'SOURCE.*ORGANISM_SCIENTIFIC:', line):
            return search('(?<=: ).*?(?=;|\n)', line).group(0)
