'''
Complex PDB files creation
'''

import os
import modules.custom_excepts as err
import modules.basic_functions as fun

write_all_complexes = "/home/ssamson/0.scripts/ReposGit/Multi_docking_analysis/autodocktools/write_all_complexes.py"
pdbqt_to_pdb = "/home/ssamson/0.scripts/ReposGit/Multi_docking_analysis/autodocktools/pdbqt_to_pdb.py"
CPLXDIR = "complexes"
POSEDIR = "poses"
GA_RUN = 20


def parse_DLG_ranks(dlgfile, warnings):
    '''
    Parsing of "RMSD TABLE" in a DLG file
    '''
    with open (dlgfile, 'r') as f :
        ranks = []
        subranks = []
        runs = []
        for line in f :
            cpt = 0
            if cpt <= GA_RUN and line.find("RANKING") != -1 :
                row = [i for i in line[:line.find("RANKING")].split(' ') if i]
                ranks.append(row[0])
                subranks.append(row[1])
                runs.append(row[2])
                cpt+=1

    if(len(ranks) != GA_RUN or len(subranks) != GA_RUN or len(runs) != GA_RUN):
        print("[WARNING] Wrong format of RMSD TABLE: '{}'".format(dlgfile))
        warnings += 1
        return([], [], [])

    return(ranks, subranks, runs)


def write_cplxes(radical, rec, dlgfile, ranks, subranks, runs):
    '''
    Write PDB files of protein and ligand complexes
    '''
    os.system("pythonsh {} -f {}_apoH.pdbqt -o {}_apoH.pdb".format(pdbqt_to_pdb, rec, rec))
    os.system("pythonsh {} -d {} -r {}_apoH.pdb -o {}/cplx".format(write_all_complexes, dlgfile, rec, CPLXDIR))
    for i in range(1, GA_RUN+1):
        for j in range(GA_RUN):
            if(i == int(runs[j])):
                output = "cplx_" + radical + ranks[j] + "-" + subranks[j] + ".mod" + runs[j]
                os.system("pythonsh {} -f {}/cplx_{}.pdbqt -o {}/{}.pdb".format(pdbqt_to_pdb, CPLXDIR, i-1, CPLXDIR, output))


def write_poses(lig, rot, dlgfile, ranks, subranks, runs):
    '''
    Write PDB files of ligand docked position
    '''
    radical = lig + "_" + rot
    os.system("grep '^DOCKED' {} | cut -c9- > {}/docked_{}.pdbqt".format(dlgfile, POSEDIR, radical))
    os.system("cut -c-66 {}/docked_{}.pdbqt > {}/docked_{}.pdb".format(POSEDIR, radical, POSEDIR, radical))
    os.system("""awk '/MODEL/{{i++}}{{print > "{}/pose_"i".pdb"}}' {}/docked_{}.pdb""".format(POSEDIR, POSEDIR, radical))
    for i in range(1, GA_RUN+1):
        for j in range(GA_RUN):
            if(i == int(runs[j])):
                output = radical + "_" + ranks[j] + "-" + subranks[j] + ".mod" + runs[j]
                os.system("mv {}/pose_{}.pdb {}/{}.pdb".format(POSEDIR, i, POSEDIR, output))


def dlg_nested_loop(inputs, rot, workdir):
    '''
    Nested loops - DLG file parsing 
    '''
    if os.path.isdir(workdir): 
        os.chdir(workdir)
        print("cd {}".format(workdir))
    else:
        raise err.WrongPathError("working directory (DLG parsing)", workdir)

    receptors, ligands = fun.prep_loop(inputs)
    warnings = 0
    for rdir in receptors.keys():
        for rec in receptors[rdir]:
            for ldir in ligands.keys():
                for lig in ligands[ldir]:
                    print(">>> DLG parsing for protein '{}' and ligand '{}_{}'.".format(rec, lig, rot))
                    path = rdir + "/" + rec + "/" + ldir + "/" + lig + "_" + rot + "/"
                    radical = rec + "_" + lig + "_" + rot
                    dlgfile = "dock_{}.dlg".format(radical)
                    if not os.path.isfile(path + dlgfile):
                        print("[WARNING] DLG file is missing: '{}'".format(path + dlgfile))
                        warnings += 1
                        continue

                    os.chdir(path)
                    #--- Complexe files directory ---#
                    if not os.path.isdir(CPLXDIR):
                        os.system("mkdir {}".format(CPLXDIR))
                    else:
                        os.system("rm -f {}/*".format(CPLXDIR))
                    #--- Docked pose files directory ---#
                    if not os.path.isdir(POSEDIR):
                        os.system("mkdir {}".format(POSEDIR))
                    else:
                        os.system("rm -f {}/*".format(POSEDIR))
                    #--- DLG file parsing ---#
                    print("> DLG Parsing - DLG file found: '{}'".format(path + dlgfile))
                    ranks, subranks, runs = parse_DLG_ranks(dlgfile, warnings)
                    if not ranks or not subranks or not runs:
                        print("[WARNING] DLG file parsing failed: '{}'".format(path + dlgfile))
                        warnings += 1
                        continue

                    write_cplxes(radical, rec, dlgfile, ranks, subranks, runs)
                    write_poses(lig, rot, dlgfile, ranks, subranks, runs)
                    os.chdir("../../../../")

    print("WARNINGS = {}\n...".format(warnings))