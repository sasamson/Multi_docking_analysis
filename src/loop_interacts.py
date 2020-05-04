'''
Protein-Ligand interactions inventory
'''

import os
import pandas as pd
import numpy as np
import glob
import modules.custom_excepts as err
import modules.basic_functions as fun

CSVDIR = "CSV_results"

HYDROP = ['', 'RESNR', 'RESTYPE', 'RESCHAIN', 'RESNR_LIG', 'RESTYPE_LIG', 'RESCHAIN_LIG', 'DIST', 'LIGCARBONIDX', 'PROTCARBONIDX', 'LIGCOO', 'PROTCOO', '']
HBONDS = ['', 'RESNR', 'RESTYPE', 'RESCHAIN', 'RESNR_LIG', 'RESTYPE_LIG', 'RESCHAIN_LIG', 'SIDECHAIN', 'DIST_H-A', 'DIST_D-A', 'DON_ANGLE', 'PROTISDON', 'DONORIDX', 'DONORTYPE', 'ACCEPTORIDX', 'ACCEPTORTYPE', 'LIGCOO', 'PROTCOO', '']
SALTBG = ['', 'RESNR', 'RESTYPE', 'RESCHAIN', 'RESNR_LIG', 'RESTYPE_LIG', 'RESCHAIN_LIG', 'DIST', 'PROTISPOS', 'LIG_GROUP', 'LIG_IDX_LIST', 'LIGCOO', 'PROTCOO', '']
PISTAC = ['', 'RESNR', 'RESTYPE', 'RESCHAIN', 'RESNR_LIG', 'RESTYPE_LIG', 'RESCHAIN_LIG', 'CENTDIST', 'ANGLE', 'OFFSET', 'TYPE', 'LIG_IDX_LIST', 'LIGCOO', 'PROTCOO', '']
PICATI = ['', 'RESNR', 'RESTYPE', 'RESCHAIN', 'RESNR_LIG', 'RESTYPE_LIG', 'RESCHAIN_LIG', 'DIST', 'OFFSET', 'PROTCHARGED', 'LIG_GROUP', 'LIG_IDX_LIST', 'LIGCOO', 'PROTCOO', '']
COLS = ["NUM", "ADT_RANK", "ADT_SUBRANK", "ADT_RUN", "RECEPTOR", "RESNR", "RESTYPE", "RESTYPE_LIG", "DIST", "DIST_H-A", "DIST_D-A", "CENTDIST", "INTERACTION", "TYPE", "LIG_GROUP", "LIGCOO", "PROTCOO"]


def read_report(reportfile, rec, rot):
    '''
    Parse PLIP report into a dataframe
    '''
    dt = pd.DataFrame(columns=COLS)
    interactype = None
    i = 0
    with open(reportfile, 'r') as f:
        for row in f:
            if row.startswith("**"):
                interactype = row.split("**")[1]
            if row[0] == "|" and "RESNR" not in row:
                row = "".join(row[:-1].split())
                elem = [a for a in row.split('|')]
                dt.loc[i] = np.nan
                ### Interactions ###
                if interactype == "Hydrophobic Interactions":
                    for x in HYDROP:
                        if x in COLS:
                            dt[x][i] = elem[HYDROP.index(x)]
                if interactype == "Hydrogen Bonds":
                    for x in HBONDS:
                        if x in COLS:
                            dt[x][i] = elem[HBONDS.index(x)]
                if interactype == "Salt Bridges":
                    for x in SALTBG:
                        if x in COLS:
                            dt[x][i] = elem[SALTBG.index(x)]
                if interactype == "pi-Stacking":
                    for x in PISTAC:
                        if x in COLS:
                            dt[x][i] = elem[PISTAC.index(x)]
                if interactype == "pi-Cation Interactions":
                    for x in PICATI:
                        if x in COLS:
                            dt[x][i] = elem[PICATI.index(x)]
                ### Loop variables columns ###
                dt["NUM"][i] = str(i+1)
                dt["RECEPTOR"][i] = rec
                dt["INTERACTION"][i] = "_".join(interactype.split())
                ### ADT ranking ###
                cplx = reportfile.split("/report.txt")[0].split("/")[-1]
                dt["ADT_RANK"][i] = cplx.split(rot)[1].split("-")[0]
                dt["ADT_SUBRANK"][i] = cplx.split("-")[1].split(".")[0]
                dt["ADT_RUN"][i] = cplx.split(".mod")[1]
                i += 1

    return(dt)


def interacts_nested_loop(inputs, rot, workdir):
    '''
    Class initialisation: one ligand ~ all proteins
    '''
    if os.path.isdir(workdir): 
        os.chdir(workdir)
        print(">>> PLIP reports parsing and Interactions inventory <<<")
    else:
        raise err.WrongPathError("working directory (PLIP tables parsing)", workdir)
    ### Outputs destination directory ###
    if os.path.isdir(CSVDIR):
        print("Directory exists: '{}'".format(CSVDIR))
    else:
        os.makedirs(CSVDIR)
        print("Directory created: '{}'".format(CSVDIR))

    receptors, ligands = fun.prep_loop(inputs)
    reports = {}
    for ldir in ligands.keys():
        for lig in ligands[ldir]:
            ### Ligand Interactions Dataframe ###
            key = lig + "_" + rot
            reports[key] = pd.DataFrame(columns=COLS)
            for rdir in receptors.keys():
                for rec in receptors[rdir]:
                    path = rdir + "/" + rec + "/" + ldir + "/" + lig + "_" + rot
                    cplxdir = glob.glob(path + "/plip_results/*")
                    if len(cplxdir) > 0:
                        print("> PLIP report parsing: '{}--{}'".format(lig, rec))
                        for cplx in cplxdir:
                            reportfile = cplx + "/report.txt"
                            new_dt = read_report(reportfile, rec, rot)
                            reports[key] = pd.concat([reports[key], new_dt])
                    else:
                        print("[WARNING] Missing PLIP files: '{}'".format(path + "/plip_results"))

    ### Write CSV outputs ###
    for key in reports.keys():
        outfile = CSVDIR + "/" + key + "_binding.csv"
        print(">>> Write CSV output for '{}' in '{}'.".format(key, outfile))
        reports[key].to_csv(outfile, sep=';', index=False, encoding='utf-8')