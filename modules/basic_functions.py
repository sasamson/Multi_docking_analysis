"""
Basic functions
"""

import os
import modules.custom_excepts as err

RECs = ["1-Refs", "2-ESKAPE", "3-BACER"]
LIGs = ["1-Basics", "2-NewMeds", "3-Aveugles", "4-Analogs"]

def check_path(path):
    """
    Check if path exists and if path is a file or directory
    """
    if os.path.isdir(path):
        if not path.endswith('/'):
            path = path + '/'
            return("directory")
    elif os.path.isfile(path):
        return("file")
    else:
        raise err.PathNotFoundError(path)


def prep_loop(inputs):
    """
    Sort parsed inputs before program loop
    """
    receptors = {}
    ligands = {}

    for key, value in inputs.items():
        if key in RECs:
            receptors[key] = value
        elif key in LIGs:
            ligands[key] = value
        
    return(receptors, ligands)

'''
def check_pdbfile(PDBfile):
    """
    Checking of the PDB file format / Search for ATOM or HETATM coordinates
    """
    with open(PDBfile, 'r') as fpdb:
        for row in fpdb:
            if row[0:4] == 'ATOM' or row[0:6] == 'HETATM':
                return(PDBfile)

    print("[WARNING] Given file in the wrong format, no 'ATOM' or 'HETATM' found: '{}' ".format(PDBfile))
'''  
