
import os
import shutil
import regex as re
import pandas as pd


import module_defs as mdefs
import utils_excel as uxls


def chiave_file(fname):
    result = re.search(r"lez([\d]+)", fname)
    if result is None:
        print(f"WARNING: ignoro {fname}")
        return None
    nr_lez = int(result.groups(1)[0])
    result = re.search(r"parte([\d]+)", fname)
    if result is None:
        print(f"WARNING: ignoro {fname}")
        return None
    nr_parte = int(result.groups(1)[0])
    # print(f"lez: {nr_lez} parte: {nr_parte} fname: {fname}")
    #nr_parte_lez = nr_lez+nr_parte
    _ , file_extension = os.path.splitext(fname)

    return nr_lez, nr_parte, file_extension



def copia_file(file_origine, directory_destinazione, simula = True):
    # Funzione per copiare un file da una directory all'altra

    ok = True

    if not os.path.isfile(file_origine):
        print(f"file da copiare {file_origine} non esiste")
        ok = False
    if not os.path.isdir(directory_destinazione):
        print(f"directory destinazione {directory_destinazione} non esiste")
        ok = False
    if not ok:
        return False

    if simula:
        print(f"simulo copia file: {file_origine} in directory: {directory_destinazione}")
        return True
    try:
        shutil.copy(file_origine, directory_destinazione)
        return True
    except Exception as exc:
        print(exc)


def copia_vecchio_fname_nuovo(file_spreadsheet, source_dir, dest_dir, col_old_fname):

    _ , valori = uxls.leggi_valori_da_sheet(file_spreadsheet, mdefs.SYMBOL, 
        mdefs.COLONNA_DA_LEGGER, mdefs.NR_RIGA_INIZIO_DATI)

    if not os.path.isdir(source_dir):
        print(f"non trovata dir {source_dir}")
        return
    old_files_dict = {}
    for disk_fname in os.listdir(source_dir):
        key = chiave_file(disk_fname)
        if key is None:
            continue
        old_files_dict[key] = disk_fname


    for index, row in valori.iterrows():
        # for i in range(row.size): print(row.iloc[index], end= ", ")

        fname_new = row[col_old_fname]
        if pd.isnull(fname_new):  # Verifica se il valore non è vuoto
           continue
        tipo = row[mdefs.NR_COL_TIPO_FILE]
        if not tipo in mdefs.FILES_ATTESI_L or pd.isnull(tipo):
            print(f"'{tipo}' tipo file inatteso, ignoro")
            continue
        dest_fname = fname_new
        if len(dest_fname.split(".")) < 2:
            print("# file senza estensione, la aggiungo: {}")
            dest_fname = dest_fname+"."+mdefs.EXTS[tipo]
            print("#"*5, f"file senza estensione, la aggiungo: {dest_fname}")
        # print(f"file DEST trovato nello spreadsheet: {dest_fname}")
        dest_fname = os.path.join(dest_dir, dest_fname)

        fname_old = row[col_old_fname+11]
        if pd.isnull(fname_old):  # Verifica se il valore non è vuoto
           continue
        chiave_file_old = chiave_file(fname_old)
        # print(f"file Source trovato nello spreadsheet: {dest_fname}")
        source_fname = os.path.join(source_dir,old_files_dict[chiave_file_old])
        if not os.path.isfile(source_fname):
            print(f"non trovato sorgente: {source_fname}")
        # print(f"source: {source_fname}\ndestin: {dest_fname}\n")

        # copia = f'copy "{source_fname}" "{dest_fname}"'
        shutil.copy(source_fname, dest_fname)        

#    return source_dest_l, missing_files_l, total_video_time_sec, files_trovati
