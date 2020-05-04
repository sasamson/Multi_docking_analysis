'''
Run PLIP on every inputs
'''

import os
import glob
import modules.custom_excepts as err
import modules.basic_functions as fun

CPLXDIR = "complexes"
PLIPDIR = "plip_results"
plipcmd = "python2 /home/ssamson/pliptool/plip/plipcmd.py "
GA_RUN = 20 


def run_plip(paths):
    '''
    PLIP on (GA_run) x Cplx PDB files
    '''
    if not os.path.isdir(PLIPDIR):
        os.system("mkdir {}".format(PLIPDIR))
    else:
        os.system("rm -fr {}".format(PLIPDIR))
        os.system("mkdir {}".format(PLIPDIR))

    resdir = []
    i=0
    for cplxpath in paths:
        resdir.append(PLIPDIR + "/" + cplxpath.split("/")[1].split(".pdb")[0])
        print("> PLIP: '{}'".format(resdir[-1]))
        plip_command = plipcmd + "-f {} -xty -o {}".format(cplxpath, resdir[i])
        os.system(plip_command)
        i += 1

    return(resdir)


def parse_plip(paths):
    '''
    Parse plip results
    '''
    for path in paths:
        report = path + "/report.txt"


def plip_nested_loop(inputs, rot, workdir):
    '''
    Nested loop - Run PLIP
    '''
    if os.path.isdir(workdir):
        os.chdir(workdir)
    else:
        raise err.WrongPathError("working directory (PLIP)", workdir)

    receptors, ligands = fun.prep_loop(inputs)
    warnings = 0
    for rdir in receptors.keys():
        for rec in receptors[rdir]:
            for ldir in ligands.keys():
                for lig in ligands[ldir]:
                    print(">>> Interactions between protein '{}' and ligand '{}_{}' profiling.".format(rec, lig, rot))
                    path = rdir + "/" + rec + "/" + ldir + "/" + lig + "_" + rot + "/"
                    os.chdir(path)
                    #--- Complexe files directory ---#
                    if not os.path.isdir(CPLXDIR):
                        print("[WARNING] Complexes directory is missing: '{}'".format(path + CPLXDIR))
                        warnings += 1
                        continue
                    
                    path_cplx = glob.glob(CPLXDIR + "/*.pdb")
                    if len(path_cplx) != GA_RUN:
                        print("[WARNING] Complex files are missing, {} file.s found: '{}'".format(len(path_cplx), path + CPLXDIR))
                        warnings +=1
                        continue

                    #--- PLIP ---#
                    results = run_plip(path_cplx)
                    parse_plip(results)
                    os.chdir("../../../../")
                    print()

    print("WARNINGS = {}\n...".format(warnings))
    