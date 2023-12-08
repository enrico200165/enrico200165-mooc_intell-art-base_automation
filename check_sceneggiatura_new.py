import sys
import os
import regex as re
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


def elabora_spreadsheet_fnames(file_spreadsheet, source_dir, col_dest_fname):

    if not os.path.isfile(file_spreadsheet):
        log.error(f"non trovato spreadsheet {file_spreadsheet}")
        exit(1)
        

    titolo_corso, valori = uxls.leggi_valori_da_sheet(file_spreadsheet, mdefs.SYMBOL, 
        mdefs.COLONNA_DA_LEGGER, mdefs.NR_RIGA_INIZIO_DATI)

    total_video_time_sec = 0; files_trovati = 0; source_dest_l = []; missing_files_l = []

    durate_video_lezioni = []
    nr_lezione = 0 
    nr_lezione_prec = -1

    for index, row in valori.iterrows():
        # for i in range(row.size): print(row.iloc[index], end= ", ")

        if row[0] is not None and type(row[0]) == str and len(str(row[0])) > 0:
            nr_lezione = int(row[0])
        if nr_lezione > nr_lezione_prec:
            durate_video_lezioni.append([0,[]])
            nr_lezione_prec = nr_lezione


        fname_no_ext = row[col_dest_fname]
        if pd.isnull(fname_no_ext):  # Verifica se il valore non è vuoto
           continue

        tipo = row[mdefs.NR_COL_TIPO_FILE]
        if not tipo in mdefs.FILES_ATTESI_L or pd.isnull(tipo):
            print(f"'{tipo}' tipo file inatteso, ignoro {fname_no_ext}")
            continue

        source_fname = fname_no_ext
        if len(source_fname.split(".")) < 2:
            print("# file senza estensione, la aggiungo: {source_fname}")
            source_fname = source_fname+"."+mdefs.EXTS[tipo]
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

        if source_fname.endswith(".pdf"):
            numero_pagine = numero_pagine_pdf(file_da_copiare)
            # print(f"Il file '{fname_no_ext}' è un PDF con {numero_pagine} pagine.")
        elif source_fname.endswith((".mp4", ".avi", ".mov")):
            minuti = durata_video_min_sec(file_da_copiare)
            total_video_time_sec += minuti
            durate_video_lezioni[-1][0] += minuti # totale lezione
            durate_video_lezioni[-1][1].append((source_fname, minuti))
            # print(f"Il file '{fname_no_ext}' è un video con durata {durata} secondi.")

            # print(f"Il file '{fname_no_ext}' è un video con durata min:secs {min}:{secs} ")

        components = fname_no_ext.split(mdefs.SEP_FNAME)
        # for c in components: print(c, end = ", ")

        lezione_long =components[1]
        lezione = lezione_long.split("-")[0]
        parte_long   = components[2]
        parte = parte_long.split("-")[0]
        # print(f"{lezione_long} , {lezione}")
        # print(f"{parte_long} , {parte}")
        fname_short = titolo_corso+mdefs.SEP_FNAME+lezione+mdefs.SEP_FNAME+parte+"."+mdefs.EXTS[tipo]
        # print(f"\n\n{source_fname}\n{fname_short}")
        source_dest_l.append( [source_fname, fname_short] )

    for lez, durata in enumerate(durate_video_lezioni):
        print(f"lez {lez} durate {durata[0]}")

    return source_dest_l, missing_files_l, total_video_time_sec, files_trovati, durate_video_lezioni


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
            dest = os.path.join(mdefs.DLV_DIR,d)
            if copia_files:
                print(f"copy {s} -> {d}")
                print(f"\nCOPIO\n{source} -> \n{dest}")
                # ul.copia_file(source, dest)
            else:
                # print(f"\nNON copy\n{source} -> \n{dest}")
                pass

    total_time_str = str(datetime.timedelta(seconds=total_video_time_sec))
    print(f"tempo totale dei video: {total_time_str}")
    print(f"{file_spreadsheet} spreadsheet")


def controlla_presenza_files(file_spreadsheet, col_fname, source_dir):

    nr_file_trovati = nr_file_non_trovati = 0

    if not os.path.isdir(source_dir):
        print(f"non trovata dire {source_dir}")
        exit(1)

    files_estranei_in_dir = set(os.listdir(source_dir))

    if not os.path.isfile(file_spreadsheet):
        print(f"non trovato spreadsheet {file_spreadsheet}")
        exit(1)

    print(f"analizzo {file_spreadsheet}")    

    _ , valori = uxls.leggi_valori_da_sheet(file_spreadsheet, mdefs.SYMBOL, 
        mdefs.COLONNA_DA_LEGGER, mdefs.NR_RIGA_INIZIO_DATI)

    for index, row in valori.iterrows():
        # for i in range(row.size): print(row.iloc[index], end= ", ")

        if row[0] is None or len(str(row[0])) <= 0:
            continue

        if row[0] is not None and type(row[0]) == str and len(str(row[0])) > 0:
            lezione = int(row[0])

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

        if tipo.lower() == "video":
            titolo = titolo_from_file(fname)
            video_pathname = os.path.join(mdefs.OUT_DIR, fname)
            zip_filename = os.path.join(mdefs.OUT_DIR, fname.replace(".mp4", ".h5p"))
            h5.zip_directory(mdefs.OUT_DIR, titolo, pathname, zip_filename)

        if fname in files_estranei_in_dir:
            files_estranei_in_dir.remove(fname)

    return nr_file_trovati, nr_file_non_trovati, files_estranei_in_dir


def main():

    try:
        if True:
            trovati, non_trovati, estranei = controlla_presenza_files(mdefs.SCENEGGIATURA,
                mdefs.NR_COL_FNAME, mdefs.DLV_DIR)
            if trovati is not None and non_trovati is not None:
                print(f"trovati: {trovati} non trovati: {non_trovati}")
                print("files estranei:")
            if estranei is not None:
                for f in estranei:
                    print(f"estraneo: {f}")
                

        if True:
            source_dest_l, missing_files_l, total_video_time_sec, trovati, durate = \
                elabora_spreadsheet_fnames(mdefs.SCENEGGIATURA, mdefs.DLV_DIR, mdefs.NR_COL_FNAME)
            print(f"total video time: {total_video_time_sec}")
        
        if durate is not None:
            for i, lezione in enumerate(durate):
                print("-"*50+f"lez:{i:0>2}: durata {round(lezione[0],2)}")
                lista_video = lezione[1]
                for video, durata in lista_video:
                    if durata > 10:
                        print(f"ECCESSIVO: {round(durata,1):>5} {video[ 46:]}")        
                    else:
                        print(f"durate: {round(durata,1):>5} {video[ 46:]}")        

        if True:
            post_proc(False, mdefs.SCENEGGIATURA, mdefs.DLV_DIR, source_dest_l, missing_files_l, total_video_time_sec)
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
