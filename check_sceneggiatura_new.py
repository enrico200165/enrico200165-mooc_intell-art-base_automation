import regex as re
import pandas as pd
import os
import time

import datetime
import shutil

from PyPDF2 import PdfFileReader
from moviepy.editor import VideoFileClip


# Impostazioni del programma
file_spreadsheet_pers = r"D:\00_data\gdrive\galilei-mirror\gare_progetti_etc\lavoro\meta-learning\Sceneggiatura_MOOC_IA_aspetti-pratici_step3.xlsx"
# file_spreadsheet_dlv = r"D:\data_ENRICO\MOOC_video_master\delivery\out_Intelligenza artificiale base\02_Sceneggiatura_MOOC_enrico-viali.xlsx"

# foglio = "Int. Art - Base_Enrico-Viali"
foglio = "Int. artific. aspetti pratici"


# "Nome File ([nomeCorso]_lez[NumLezione]_parte[NumParte])"
colonna_da_leggere = 3
NR_RIGA_INIZIO_DATI = 6
DIRECTORY_SOURCE_EV  = r"D:\MOOC_Intell-Art ASP. Pratici\delivery_prev"
#DIRECTORY_SOURCE_DLV = r"D:\data_ENRICO\MOOC_master\delivery\out_Intelligenza artificiale base"

DIRECTORY_DEST = r"D:\MOOC_Intell-Art ASP. Pratici\delivery_new"
DIRECTORY_DEST = r"D:\MOOC_Intell-Art ASP. Pratici\delivery_LONG-LESSONS"


NR_COL_FNAME = 5 # dovrebbe essere normale
NR_COL_FNAME = 7 # mio spreadsheet modificato
NR_COL_TIPO_FILE = NR_COL_FNAME+1

SEP_FNAME = "_"

NOME_CORSO = "Itelligenza Artificiale Base"

SLIDES = "Slides pdf"
QUIZ = "Quiz"
VIDEO = "Video"
DOCX = "docx"
XML = "xml"

FILES_ATTESI_L = [SLIDES, VIDEO, QUIZ, DOCX, XML, "mbz", "xlsx" , "pdf" ]


# per appendere estensione giusta
EXTS = {SLIDES: "pdf", VIDEO: "mp4", QUIZ: "xlsx"}

FNAME1_COL = 4


def leggi_valori(nome_file, nome_foglio,  colonna, riga_iniziale):
    # legge i valori di tutte le colonne piene
    # ritorna ( titolo del corso , i valori dell compresi nella matrice dello spreadshee )

    if not os.path.isfile(nome_file):
        print(f"non trovato file: {nome_file}")
        return None, None

    # Leggi il file spreadsheet utilizzando pandas
    df = pd.read_excel(nome_file, sheet_name=nome_foglio)

    # Seleziona i valori della colonna specificata
    valori_colonna = df.iloc[riga_iniziale:, :]
    titolo = df.iloc[2][1]

    return titolo, valori_colonna



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


def numero_pagine_pdf(file_pdf):
    # Funzione per ottenere il numero di pagine di un file PDF
    with open(file_pdf, "rb") as f:
        pdf = PdfFileReader(f, strict=False)
        numero_pagine = pdf.getNumPages()

    return numero_pagine


def durata_video(file_video):
    # Funzione per ottenere la durata di un file video
    clip = VideoFileClip(file_video)
    durata = clip.duration

    return durata


def durata_video_min_sec(file_video):
    durata = durata_video(file_video)

    return int(durata//60), int(durata % 60)


# Leggi i valori dalla colonna specificata


def elabora_spreadsheet_fnames(file_spreadsheet, source_dir, col_dest_fname):

    titolo_corso, valori = leggi_valori(file_spreadsheet, foglio, colonna_da_leggere, NR_RIGA_INIZIO_DATI)

    total_video_time_sec = 0; files_trovati = 0; source_dest_l = []; missing_files_l = []


    for index, row in valori.iterrows():
        # for i in range(row.size): print(row.iloc[index], end= ", ")

        fname_no_ext = row[col_dest_fname]
        if pd.isnull(fname_no_ext):  # Verifica se il valore non è vuoto
           continue

        tipo = row[NR_COL_TIPO_FILE]
        if not tipo in FILES_ATTESI_L or pd.isnull(tipo):
            print(f"'{tipo}' tipo file inatteso, ignoro")
            continue

        source_fname = fname_no_ext
        if len(source_fname.split(".")) < 2:
            print("# file senza estensione, la aggiungo: {}")
            source_fname = source_fname+"."+EXTS[tipo]
            print("#"*5, f"file senza estensione, la aggiungo: {source_fname}")


        file_da_copiare = os.path.join(source_dir, source_fname)
        if not os.path.isfile(file_da_copiare):
            # print(f"index {index} - {file_da_copiare} non è un file")
            missing_files_l.append(source_fname)
            continue

        files_trovati +=1

        # includi = int(row[9])
        includi = True
        if includi == 0:
            print(f"escluso {source_fname}")
            continue

        if file_da_copiare.endswith(".pdf"):
            numero_pagine = numero_pagine_pdf(file_da_copiare)
            # print(f"Il file '{fname_no_ext}' è un PDF con {numero_pagine} pagine.")
        elif file_da_copiare.endswith((".mp4", ".avi", ".mov")):
            durata_sec = durata_video(file_da_copiare)
            total_video_time_sec += durata_sec
            # print(f"Il file '{fname_no_ext}' è un video con durata {durata} secondi.")

            min, secs = durata_video_min_sec(file_da_copiare)
            # print(f"Il file '{fname_no_ext}' è un video con durata min:secs {min}:{secs} ")

        components = fname_no_ext.split(SEP_FNAME)
        # for c in components: print(c, end = ", ")

        lezione_long =components[1]
        lezione = lezione_long.split("-")[0]
        parte_long   = components[2]
        parte = parte_long.split("-")[0]
        # print(f"{lezione_long} , {lezione}")
        # print(f"{parte_long} , {parte}")
        fname_short = titolo_corso+SEP_FNAME+lezione+SEP_FNAME+parte+"."+EXTS[tipo]
        # print(f"\n\n{source_fname}\n{fname_short}")
        source_dest_l.append( [source_fname, fname_short] )

    return source_dest_l, missing_files_l, total_video_time_sec, files_trovati


def post_proc(copia_files, file_spreadsheet, source_dir, source_dest_l, missing_files_l, total_video_time_sec):
    
    print("-"*20, "missing files", "-"*20)
    
    if (len(missing_files_l)) > 0:
        print(f"{len(missing_files_l)} missing files in dir: {source_dir}")
        for e in missing_files_l:
            print(f"{e} not found in {source_dir}")
    else:
        print("OK, trovati tutti i files")
        for s,d in source_dest_l:
            source = os.path.join(source_dir,s)
            dest = os.path.join(DIRECTORY_DEST,d)
            if copia_files:
                print(f"copy {s} -> {d}")
                print(f"\nCOPIO\n{source} -> \n{dest}")
                # copia_file(source, dest)
            else:
                # print(f"\nNON copy\n{source} -> \n{dest}")
                pass

    total_time_str = str(datetime.timedelta(seconds=total_video_time_sec))
    print(f"tempo totale dei video: {total_time_str}")
    print(f"{file_spreadsheet} spreadsheet")



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



def copia_vecchio_fname_nuovo(file_spreadsheet, source_dir, dest_dir, col_old_fname):

    _ , valori = leggi_valori(file_spreadsheet, foglio, colonna_da_leggere, NR_RIGA_INIZIO_DATI)



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
        tipo = row[NR_COL_TIPO_FILE]
        if not tipo in FILES_ATTESI_L or pd.isnull(tipo):
            print(f"'{tipo}' tipo file inatteso, ignoro")
            continue
        dest_fname = fname_new
        if len(dest_fname.split(".")) < 2:
            print("# file senza estensione, la aggiungo: {}")
            dest_fname = dest_fname+"."+EXTS[tipo]
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



def controlla_presenza_files(file_spreadsheet, col_fname, source_dir):

    nr_file_trovati = nr_file_non_trovati = 0

    if not os.path.isdir(source_dir):
        print(f"non trovata dir {source_dir}")
        return

    _ , valori = leggi_valori(file_spreadsheet, foglio, colonna_da_leggere, NR_RIGA_INIZIO_DATI)

    for index, row in valori.iterrows():
        # for i in range(row.size): print(row.iloc[index], end= ", ")

        dest_fname = row[col_fname]
        if pd.isnull(dest_fname):  # Verifica se il valore non è vuoto
           continue
        tipo = row[NR_COL_TIPO_FILE]
        if not tipo in FILES_ATTESI_L or pd.isnull(tipo):
            print(f"'{tipo}' tipo file inatteso, ignoro")
            continue

        if len(dest_fname.split(".")) < 2:
            print("# file senza estensione, la aggiungo: {}")
            dest_fname = dest_fname+"."+EXTS[tipo]
            print("#"*5, f"file senza estensione, la aggiungo: {dest_fname}")
        # print(f"file DEST trovato nello spreadsheet: {dest_fname}")
        dest_fname = os.path.join(source_dir, dest_fname)

        if not os.path.isfile(dest_fname):
            print("\n\n"+"#"*10+f"ERRORE non trovato: \n{os.path.basename(dest_fname)}"+"\n\n")
            nr_file_non_trovati += 1
        else:
            # print(f"ok trovato: {dest_fname}")
            nr_file_trovati += 1

    return nr_file_trovati, nr_file_non_trovati



#file_spreadsheet_pers = r"D:\MOOC_Intell-Art ASP. Pratici\delivery_new\00_Sceneggiatura_MOOC_IA_aspetti-pratici.xlsx"

file_spreadsheet_pers = r"D:\MOOC_Intell-Art ASP. Pratici\delivery_LONG-LESSONS\00_Sceneggiatura_MOOC_IA_aspetti-pratici.xlsx"


# copia_vecchio_fname_nuovo(file_spreadsheet_pers, DIRECTORY_SOURCE_EV, DIRECTORY_DEST, NR_COL_FNAME)

if True:
    trovati, non_trovati = controlla_presenza_files(file_spreadsheet_pers,NR_COL_FNAME, DIRECTORY_DEST)
    print(f"trovati: {trovati} non trovati: {non_trovati}")

if False:
    source_dest_l, missing_files_l, total_video_time_sec, trovati = elabora_spreadsheet_fnames(file_spreadsheet_pers, DIRECTORY_DEST, NR_COL_FNAME)
    post_proc(False, file_spreadsheet_pers, DIRECTORY_SOURCE_EV, source_dest_l, missing_files_l, total_video_time_sec)
# copia da deliverare
# source_dest_l, missing_files_l, total_video_time_sec = elabora_spreadsheet_fnames(file_spreadsheet_pers, DIRECTORY_SOURCE_DLV, 4)
# post_proc(False, file_spreadsheet_dlv, DIRECTORY_SOURCE_DLV, source_dest_l, missing_files_l, total_video_time_sec)

# print(f"files trovati: {trovati}")