import sys
import os
from numpy import isnan
import regex as re
import numpy as np
import pandas as pd

import datetime

import utils_little as ul
import utils_excel as uxls

from PyPDF2 import PdfReader
from moviepy.editor import VideoFileClip


from logdef_local import log
import module_defs as mdefs
import h5p_video as h5


def titolo_from_file(fname):
    ret = fname.split(sep = "_")
    ret = ret[3]+" - "+ret[4]
    return ret


def numero_pagine_pdf(file_pdf):
    # Funzione per ottenere il numero di pagine di un file PDF
    with open(file_pdf, "rb") as f:
        pdf_reader = PdfReader(f, strict=False)
        numero_pagine = len(pdf_reader.pages)

    return numero_pagine


def durata_video(file_video):
    # Funzione per ottenere la durata di un file video
    clip = VideoFileClip(file_video)
    durata = clip.duration

    return durata


def durata_video_min_sec(file_video):
    durata = durata_video(file_video)

    minuti = int(durata//60)
    secondi = (durata % 60)/60

    return minuti+secondi


# Leggi i valori dalla colonna specificata



def empty_cell_value(val):
    return val is None or np.isnan(val) or len(val) <= 0

def controlla_scenografia(file_spreadsheet, col_fname, source_dir):

    nr_file_trovati = nr_file_non_trovati = 0
    source_dest_l = []; missing_files_l = []

    if not os.path.isdir(source_dir):
        print(f"non trovata dire {source_dir}")
        exit(1)
    if not os.path.isfile(file_spreadsheet):
        print(f"non trovato spreadsheet {file_spreadsheet}")
        exit(1)

    # assumiamo siano tutti estranei, rimuoviamo non estranei
    files_estranei_l = set(os.listdir(source_dir))
    print(f"analizzo {file_spreadsheet}")    

    titolo_corso , valori = uxls.leggi_valori_da_sheet(file_spreadsheet, mdefs.SYMBOL, 
        mdefs.COLONNA_DA_LEGGER, mdefs.NR_RIGA_INIZIO_DATI)
    durate_video_lezioni = []; total_video_time_sec = 0
    nr_lezione = 0; nr_lezione_prec = -1
    # for index, row in valori.iterrows():
    for index in range(len(valori)):
        
        row = valori.iloc[index]

        nr_lez_raw = row[mdefs.NR_COL_NR_LEZ]
        ttl_lez_raw = row[mdefs.NR_COL_TTL_LEZ]
        try:
            nr_lezione = int(row[mdefs.NR_COL_NR_LEZ])
        except Exception as exc_obj:
            if ttl_lez_raw is None or np.isnan(ttl_lez_raw) or len(ttl_lez_raw) <= 0:
                continue # ok riga vuota
            print(f"{nr_lez_raw} caused exception {exc_obj}")
            for i in range(row.size):
                print(row.iloc[index], end= ", ")
            exit(1)

        if nr_lezione > nr_lezione_prec:
            print(f"nr lezione {nr_lezione}")
            print("")
            durate_video_lezioni.append([0,[]]) # crea antry per lezione, durata lez a 0
            nr_lezione_prec = nr_lezione

        fname = row[col_fname]
        if pd.isnull(fname):  # Verifica se il valore non è vuoto
           continue

        tipo = row[mdefs.NR_COL_TIPO_FILE]
        if not tipo in mdefs.FILES_ATTESI_L or pd.isnull(tipo):
            print(f"'{tipo}' tipo file inatteso, ignoro")
            continue

        if len(fname.split(".")) < 2:
            print("# file senza estensione, la aggiungo: {}")
            fname = fname+"."+mdefs.EXTS[tipo]
            print("#"*5, f"file senza estensione, la aggiungo: {fname}")
        # print(f"file DEST trovato nello spreadsheet: {dest_fname}")
        pathname = os.path.join(source_dir, fname)

        if not os.path.isfile(pathname):
            print("\n"+"#"*10+f" {index}-esimo ERRORE non trovato: \n{os.path.basename(pathname)}"+"\n")
            nr_file_non_trovati += 1
            continue

        # print(f"{index}- ok trovato: {dest_fname}")
        nr_file_trovati += 1

        # lista coppie (fname sorgente/originario , fname pulito/destinazione)
        fname_no_ext = os.path.splitext(fname)[0]
        components = fname_no_ext.split(mdefs.SEP_FNAME)
        # for c in components: print(c, end = ", ")
        lezione_long =components[1]
        lezione = lezione_long.split("-")[0]
        parte_long   = components[2]
        parte = parte_long.split("-")[0]
        # print(f"{lezione_long} , {lezione} {parte_long} , {parte}")
        # fname_short = titolo_corso+mdefs.SEP_FNAME+lezione+mdefs.SEP_FNAME+parte+"."+mdefs.EXTS[tipo]
        # print(f"\n\n{source_fname}\n{fname_short}")
        source_dest_l.append( [fname, fname] )

        if fname.endswith(".pdf"):
            numero_pagine = numero_pagine_pdf(pathname)
            # print(f"Il file '{fname_no_ext}' è un PDF con {numero_pagine} pagine.")
        elif fname.endswith((".mp4", ".avi", ".mov")):
            assert(tipo.lower() == "video")
            minuti = durata_video_min_sec(pathname)
            total_video_time_sec += minuti
            durate_video_lezioni[-1][0] += minuti # totale lezione
            durate_video_lezioni[-1][1].append((fname, minuti)) # durata video

        # non è estraneo
        if fname in files_estranei_l:
            files_estranei_l.remove(fname)

    # return nr_file_trovati, nr_file_non_trovati, files_estranei_in_dir
    return source_dest_l, missing_files_l, files_estranei_l, total_video_time_sec,\
        nr_file_trovati, durate_video_lezioni


def post_proc(copia_files, file_spreadsheet, 
              source_dir, dest_dir, 
              source_dest_l, missing_files_l, files_estranei_l,
              total_video_time_sec, durate_video_lezioni_l):
    """
    durate_video_lezioni_l[ secondi-totali, [ [] ]]
    """
    
    
    if (len(missing_files_l)) > 0:
        print("-"*20, "missing files", "-"*20)
        print(f"{len(missing_files_l)} missing files in dir: {source_dir}")
        for e in missing_files_l:
            print(f"{e} not found in {source_dir}")
        return
    print(f"OK, trovati tutti i files, {len(source_dest_l)}")
    
    if files_estranei_l is not None:
        print("troati files estranei (innocui):")
        for f in files_estranei_l:
            print(f"estraneo: {f}")


    for source_fname, dest_fname in source_dest_l:
        source_pathname = os.path.join(source_dir, source_fname)
        dest_pathname = os.path.join(dest_dir, dest_fname)
        if copia_files:
            if source_fname.endswith((".mp4", ".avi", ".mov")):
                titolo = titolo_from_file(source_fname)
                zip_filename = os.path.join(dest_dir, source_fname.replace(".mp4", ".h5p"))
                if not os.path.isfile(zip_filename):
                    h5.zip_directory(dest_dir, titolo, source_pathname, zip_filename)
            else:
                print(f"copy {source_fname} -> {dest_fname}")
                print(f"\nCOPIO\n{source_pathname} -> \n{dest_pathname}")
                ul.copia_file(source_pathname, dest_dir, simula= False)
        else:
            # print(f"\nNON copy\n{source} -> \n{dest}")
            pass

        if source_fname.endswith(".pdf"):
            numero_pagine = numero_pagine_pdf(source_pathname)
            # print(f"Il file '{fname_no_ext}' è un PDF con {numero_pagine} pagine.")


    for lez, durata in enumerate(durate_video_lezioni_l):
        print(f"lez {lez} durate {durata[0]}")

    for i, lezione in enumerate(durate_video_lezioni_l):
        print("-"*8+f" lez:{i:0>2}: durata {round(lezione[0],2)} "+"-"*28)
        lista_video = lezione[1]
        for video, durata in lista_video:
            if durata > 10:
                print(f"ECCESS: {round(durata,1):>5} {video[ 46:]}")        
            else:
                print(f"durate: {round(durata,1):>5} {video[ 46:]}")        

    total_time_str = str(datetime.timedelta(seconds=total_video_time_sec))
    print(f"tempo totale dei video: {total_time_str}")
    print(f"{file_spreadsheet} spreadsheet")


def main():

    try:
        if True:
            # trovati, non_trovati, estranei = controlla_scenografia(mdefs.SCENEGGIATURA,
            source_dest_l, missing_files_l, files_estranei_l, total_video_time_sec, trovati, durate = \
                controlla_scenografia(mdefs.SCENEGGIATURA,mdefs.NR_COL_FNAME, mdefs.DLV_DIR)        

        if True:
            out_dir = os.path.sep.join(mdefs.DLV_DIR.split(os.path.sep)[:-1]+["out"])
            post_proc(True, mdefs.SCENEGGIATURA, 
                      mdefs.DLV_DIR, out_dir, 
                      source_dest_l, missing_files_l,files_estranei_l, 
                      total_video_time_sec, durate)
            print(f"file_trovati {trovati} == da copiare {len(source_dest_l)}")
        # copia da deliverare
        # source_dest_l, missing_files_l, total_video_time_sec = elabora_spreadsheet_fnames(file_spreadsheet_pers, DIRECTORY_SOURCE_DLV, 4)
        # post_proc(False, file_spreadsheet_dlv, DIRECTORY_SOURCE_DLV, source_dest_l, missing_files_l, total_video_time_sec)

        # print(f"files trovati: {trovati}")
    except Exception as e:
        e_type, e_object, e_traceback = sys.exc_info()
        e_filename = os.path.split(e_traceback.tb_frame.f_code.co_filename)[1]
        e_message = str(e)
        e_line_number = e_traceback.tb_lineno
        print(f'exception type: {e_type}')
        print(f'exception filename: {e_filename}')
        print(f'exception line number: {e_line_number}')
        print(f'exception message: {e_message}')

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        e_type, e_object, e_traceback = sys.exc_info()
        e_filename = os.path.split(e_traceback.tb_frame.f_code.co_filename)[1]
        e_message = str(e)
        e_line_number = e_traceback.tb_lineno
        print(f'exception type: {e_type}')
        print(f'exception filename: {e_filename}')
        print(f'exception line number: {e_line_number}')
        print(f'exception message: {e_message}')
