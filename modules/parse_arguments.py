ARGS = """
#----------------------------------------------------------------#
#       Program: Automation of multi-docking and analysis.       #
#----------------------------------------------------------------#

Usage:
  multi-docking.py -h | --help | --version
  multi-docking.py -D FILEPATH BONDS_TYPE [-o OUTDIR/]
  multi-docking.py -C FILEPATH BONDS_TYPE [-o OUTDIR/]
  multi-docking.py -P FILEPATH BONDS_TYPE [-o OUTDIR/]
  multi-docking.py -I FILEPATH BONDS_TYPE [-o OUTDIR/]

Options:
  -h, --help      Show usage.
      --version   Show programme version.
  -D, --docking   Run AutoDockTools.
  -C, --complex   Parse dlg files into PLIP inputs.
  -P, --plip      Run Protein-Ligand Interaction Profiler (PLIP).
  -I, --interact  PLIP outputs parsing and interactions inventory.
(Optional)
  -o, --outdir OUTDIR/  User defined outputs directory,
                        current directory by default.

Arguments:
  FILEPATH    Parameters file path (.txt).
  BONDS_TYPE  Ligands bonds type: "free" or "fix".
  OUTDIR/     Working directory path.

#----------------------------------------------------------------#
"""

import os
import re
from docopt import docopt
import modules.custom_excepts as err
import modules.basic_functions as fun

VERSION = "Multi-Docking with ADT4-PLIP 1.0"


class InputArguments(object):
    """
    Parse user arguments
    """
    def __init__(self):
        self.option = None
        self.bonds = None
        self.parsed_input = {}
        self.path_input = ""
        self.path_output = "./"

    def init_inpaths(self, infile):
        """
        Parse input file
        """
        cpt = 0
        with open(infile, 'r') as inf:
            for row in inf:
                cpt += 1
                row = row[:-1]
                lrow = row.split()
                if row.startswith("#") or len(lrow) <= 1:
                    continue
                if lrow[1] != "=":
                    raise err.InFileSyntaxError(infile, cpt, row)

                tmp = re.split(r'"*"', row.split('=')[1])
                tmp = [i for i in tmp if ' ' not in i and i!='']
                if len(tmp) == 0 or tmp[0] == row.split('=')[1]:
                    raise err.InFileSyntaxError(infile, cpt, row)

                self.parsed_input[lrow[0]] = tmp

    def init_arg(self):
        """
        Class initialisation - Arguments parsing and checking
        """
        arguments = docopt(ARGS, version=VERSION)

        if arguments['--help']:
            print(ARGS)
            return(0)
    
        if arguments['--version']:
            print(VERSION)
            return(0)

        if arguments['--docking']:
            self.option = "docking"
        elif arguments['--complex']:
            self.option = "complex"
        elif arguments['--plip']:
            self.option = "plip"
        elif arguments['--interact']:
            self.option = "interact"

        infile = arguments['FILEPATH']
        if fun.check_path(infile) == "file" and infile.endswith(".txt"):
            self.path_input = infile
            self.init_inpaths(infile)
        else:
            raise err.WrongPathError("parameters file", infile)

        if arguments['BONDS_TYPE'] == "free" or arguments['BONDS_TYPE'] == "fix":
            self.bonds = arguments['BONDS_TYPE']
        else:
            raise err.WrongBondError(bonds)

        outdir = arguments['--outdir']
        if outdir is not None:
            if fun.check_path(outdir) == "directory":
                self.path_output = outdir
            else:
                raise err.WrongPathError("working directory", outdir)