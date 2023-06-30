import pandas as pd
import os

import datetime
import shutil

from PyPDF2 import PdfFileReader
from moviepy.editor import VideoFileClip


# Impostazioni del programma
file_spreadsheet_pers = r"D:\data_ENRICO\GDRIVE\galilei_mirror\gare_progetti_etc\lavoro\AI-MOOC-base\contenuti\02_Sceneggiatura_MOOC_enrico-viali.xlsx"
file_spreadsheet_dlv = r"D:\data_ENRICO\MOOC_video_master\delivery\out_Intelligenza artificiale base\02_Sceneggiatura_MOOC_enrico-viali.xlsx"

foglio = "Int. Art - Base_Enrico-Viali"
# "Nome File ([nomeCorso]_lez[NumLezione]_parte[NumParte])"
colonna_da_leggere = 4
riga_iniziale = 5
DIRECTORY_SOURCE_EV  = r"D:\data_ENRICO\MOOC_video_master\delivery\delivery_ev"
DIRECTORY_SOURCE_DLV = r"D:\data_ENRICO\MOOC_video_master\delivery\out_Intelligenza artificiale base"
DIRECTORY_DEST = r"D:\temp"

SEP_FNAME = "_"

NOME_CORSO = "Itelligenza Artificiale Base"

SLIDES = "Slides pdf"
QUIZ = "Quiz"
VIDEO = "Video"

# per appendere estensione giusta
EXTS = {SLIDES: "pdf", VIDEO: "mp4", QUIZ: "xlsx"}

FNAME1_COL = 4


# Funzione per leggere i valori dalla colonna N, a partire dalla riga M
def leggi_valori(nome_file, nome_foglio,  colonna, riga_iniziale):
    # Leggi il file spreadsheet utilizzando pandas
    df = pd.read_excel(nome_file, sheet_name=nome_foglio)

    # Seleziona i valori della colonna specificata
    valori_colonna = df.iloc[riga_iniziale:, :]
    titolo = df.iloc[2][1]
    return titolo, valori_colonna

# Funzione per copiare un file da una directory all'altra


def copia_file(file_origine, directory_destinazione):
    try:
        shutil.copy(file_origine, directory_destinazione)
    except Exception as e:
        print(e)

# Funzione per ottenere il numero di pagine di un file PDF


def numero_pagine_pdf(file_pdf):
    with open(file_pdf, "rb") as f:
        pdf = PdfFileReader(f, strict=False)
        numero_pagine = pdf.getNumPages()

    return numero_pagine

# Funzione per ottenere la durata di un file video


def durata_video(file_video):
    clip = VideoFileClip(file_video)
    durata = clip.duration

    return durata


def durata_video_min_sec(file_video):
    durata = durata_video(file_video)

    return int(durata//60), int(durata % 60)


# Leggi i valori dalla colonna specificata


def elabora_spreadsheet_fnames(file_spreadsheet, source_dir):

    titolo_corso, valori = leggi_valori(file_spreadsheet, foglio, colonna_da_leggere, riga_iniziale)

    total_video_time_sec = 0

    source_dest_l = []
    missing_files_l = []

    for index, row in valori.iterrows():
        # for i in range(row.size): print(row.iloc[index], end= ", ")

        fname_no_ext = row[4]
        if pd.isnull(fname_no_ext):  # Verifica se il valore non è vuoto
           continue

        tipo = row[5]
        if not tipo in [SLIDES, VIDEO, QUIZ] or pd.isnull(tipo):
            print(f"'{tipo}' tipo file inatteso, ignoro")
            continue

        source_fname = fname_no_ext+"."+EXTS[tipo]

        file_da_copiare = os.path.join(source_dir, source_fname)
        if not os.path.isfile(file_da_copiare):
            # print(f"index {index} - {file_da_copiare} non è un file")
            missing_files_l.append(source_fname)
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

    return source_dest_l, missing_files_l, total_video_time_sec


def post_proc(copia_files, file_spreadsheet, source_dir, source_dest_l, missing_files_l, total_video_time_sec):
    
    print("-"*20, "missing files", "-"*20)
    
    if (len(missing_files_l)) > 0:
        print(f"{len(missing_files_l)} missing files in dir: {source_dir}")
        for e in missing_files_l:
            print(f"{e} not found")

    if (len(missing_files_l)) <= 0:
        for s,d in source_dest_l:
            source = os.path.join(source_dir,s)
            print(f"copy {s} -> {d}")
            dest = os.path.join(DIRECTORY_DEST,d)
            if copia_files:
                copia_file(source, dest)
                print(f"\nCOPIO\n{source} -> \n{dest}")
            else:
                print(f"\nNON copy\n{source} -> \n{dest}")

    total_time_str = str(datetime.timedelta(seconds=total_video_time_sec))
    print(f"tempo totale dei video: {total_time_str}")
    print(f"{file_spreadsheet} spreadsheet")


# mia directory personale
# source_dest_l, missing_files_l, total_video_time_sec = elabora_spreadsheet_fnames(file_spreadsheet_pers, DIRECTORY_SOURCE_EV)
# post_proc(False, file_spreadsheet_pers, DIRECTORY_SOURCE_EV, source_dest_l, missing_files_l, total_video_time_sec)

# copia da deliverare
source_dest_l, missing_files_l, total_video_time_sec = elabora_spreadsheet_fnames(file_spreadsheet_pers, DIRECTORY_SOURCE_DLV)
post_proc(False, file_spreadsheet_dlv, DIRECTORY_SOURCE_DLV, source_dest_l, missing_files_l, total_video_time_sec)
