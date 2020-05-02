'''
Run AutoDoTools4 on every inputs
'''

import os
import modules.custom_excepts as err
import modules.basic_functions as fun

LOGDIR = "/home/ssamson/1.work_MFD/Docking3/LOG/"
GPFDIR = "/home/ssamson/1.work_MFD/Docking3/GPF_ref/"
prepare_gpf4 = "/home/ssamson/0.scripts/ReposGit/Multi_docking_analysis/autodocktools/prepare_gpf4.py"
prepare_dpf4 = "/home/ssamson/0.scripts/ReposGit/Multi_docking_analysis/autodocktools/prepare_dpf4.py"
GA_RUN = 20


def check_dockpath(rec, rdir, lig, ldir, rot):
    '''
    Check docking outputs directories
    ''' 
    #--- Directory creation ---#
    path = rdir + "/" + rec + "/" + ldir + "/" + lig + "_" + rot
    if os.path.isdir(path):
        print("Directory exists: '{}'".format(path))
    else:
        os.makedirs(path)
        print("Directory created: '{}'".format(path))

    return(path)


def make_docking_dir(path, rec, rdir, rec_srcdir, lig, ldir, lig_srcdir, rot):
    '''
    Docking directories preparation and ADT4 inputs copy
    ''' 
    cpt = 0
    print(">>> PDBQT files destination directory: '{}'".format(path))
    #--- PDBQT inputs copy ---#
    recpath = rec_srcdir + rdir + "/" + rec + "/" + rec + "_apoH.pdbqt"
    ligpath = lig_srcdir + ldir + "/" + lig + "/" + lig + "_" + rot + ".pdbqt"
    if not os.path.isfile(recpath):
        print("[WARNING] Receptor file not found: '{}'".format(recpath))
        cpt += 1
    else:
        os.system("cp {} {}".format(recpath, path))
        print("> Receptor file copied: '{}'".format(recpath))
    if not os.path.isfile(ligpath):
        print("[WARNING] Ligand file not found: '{}'".format(ligpath))
        cpt += 1
    else:
        os.system("cp {} {}".format(ligpath, path))
        print("> Ligand file copied: '{}'".format(ligpath))

    return(cpt)


def run_docking(rec, rdir, lig, ldir, rot, gpf):
    '''
    Run autogrid on inputs
    '''
    cpt = 0
    recfile = rec + "_apoH.pdbqt"
    ligfile = lig + "_" + rot + ".pdbqt"
    if not os.path.isfile(recfile):
        print("[WARNING] Protein PDBQT file is missing: '{}'".format(recfile))
        cpt += 1
    if not os.path.isfile(ligfile):
        print("[WARNING] Ligand PDBQT file is missing: '{}'".format(ligfile))
        cpt += 1
    if cpt != 0:
        return(cpt)
    else:
        print("> Protein '{}' and ligand '{}_{}' PDBQT files found.".format(rec, lig, rot))
        radical = rec + "_" + lig + "_" + rot
        print("> Run Docking: '{}'".format(radical))
        print()

    #--- Autogrid ---#
    print("> AutoGrid - GPF reference file found: '{}'".format(gpf))
    autogrid_prep = "pythonsh {} -l {} -r {} -i {} -o grid_{}.gpf".format(prepare_gpf4, ligfile, recfile, gpf, radical)
    os.system(autogrid_prep)
    autogrid_run = "autogrid4 -p grid_{}.gpf -l grid_{}.glg".format(radical, radical)
    os.system(autogrid_run)
    print("> fin AutoGrid.")
    print()
    #----------------#
    if not os.path.isfile("grid_{}.glg".format(radical)):
        print("[WARNING] AutoGrid (.glg) failed for protein '{}' and ligand '{}_{}'.".format(rec, lig, rot))
        return(cpt+1)
    #--- Autodock ---#
    print("> AutoDock - GLG file found: 'grid_{}.glg'".format(radical))
    autodock_prep = "pythonsh {} -l {} -r {} -p ga_run={} -o dock_{}.dpf".format(prepare_dpf4, ligfile, recfile, GA_RUN, radical)
    os.system(autodock_prep)
    autodock_run = "autodock4 -p dock_{}.dpf -l dock_{}.dlg".format(radical, radical)
    os.system(autodock_run)
    print("> fin AutoDock.")
    #----------------#
    if not os.path.isfile("dock_{}.dlg".format(radical)):
        print("[WARNING] AutoDock (.dlg) failed for protein '{}' and ligand '{}_{}'.".format(rec, lig, rot))
        return(cpt+1)

    return(0)


def adt_nested_loops(inputs, rot, workdir):
    '''
    Nested loops - Run ADT4
    '''
    if os.path.isdir(workdir): 
        os.chdir(workdir)
    else:
        raise err.WrongPathError("working directory (Docking)", workdir)

    receptors, ligands = fun.prep_loop(inputs)
    for key, value in inputs.items():
        if key == "PROTDIR" and fun.check_path(value[0]) == "directory":
            rec_srcdir = value[0] + "/"
        elif key == "LIGDIR" and fun.check_path(value[0]) == "directory":
            lig_srcdir = value[0]  + "/"

    warnings = 0
    for rdir in receptors.keys():
        for rec in receptors[rdir]:
            #--- Check GPF reference file ---#
            gpf = GPFDIR + "grid_" + rec + "_ref.gpf"
            if not os.path.isfile(gpf):
                print("[WARNING] Grid box reference file not found: '{}'".format(gpf))
                warnings += 1
            else:
                #os.system("cp {} {}".format(gpf, rdir + "/" + rec + "/"))
                print("> GPF reference file copied: '{}'".format(gpf))
                for ldir in ligands.keys():
                    for lig in ligands[ldir]:
                        path = check_dockpath(rec, rdir, lig, ldir, rot)
                        warnings += make_docking_dir(path, rec, rdir, rec_srcdir, lig, ldir, lig_srcdir, rot)
                        print("----------------------------------------")
                        os.chdir(path)
                        print(">>> Docking in '{}'.".format(path))
                        warnings += run_docking(rec, rdir, lig, ldir, rot, gpf)
                        os.chdir("../../../../")
                        print("----------------------------------------")

    print("WARNINGS = {}\n...".format(warnings))


### Remplacer les cpt des warnings par une liste de str.
### write liste dans log file.