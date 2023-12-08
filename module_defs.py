"""."""

import os

ROOT_DIR = r"D:\MOOC_Intell-Art-ASP-Pratici" 
DLV_DIR  = os.path.join(ROOT_DIR, "delivery")
OUT_DIR  = os.path.join(ROOT_DIR, "out")


# Impostazioni del programma
SCENEGGIATURA = os.path.join(DLV_DIR,"00_Sceneggiatura_MOOC_IA_aspetti-pratici.xlsx")
SYMBOL = "Int. artific. aspetti pratici"

NR_COL_OFFSET = 3

# "Nome File ([nomeCorso]_lez[NumLezione]_parte[NumParte])"
COLONNA_DA_LEGGER = 3
NR_RIGA_INIZIO_DATI = 8

NR_COL_FNAME = NR_COL_OFFSET+7 # dovrebbe essere normale
NR_COL_TIPO_FILE = NR_COL_FNAME+1

SEP_FNAME = "_"

NOME_CORSO = "Intelligenza Artificiale Base"

SLIDES = "Slides pdf"
QUIZ = "Quiz"
VIDEO = "Video"
DOCX = "docx"
XML = "xml"
MBZ = "mbz"

FILES_ATTESI_L = [SLIDES, VIDEO, QUIZ, DOCX, XML, "mbz", "xlsx" , "pdf", "docx -> pg moodle" ]

# per appendere estensione giusta
EXTS = {SLIDES: "pdf", VIDEO: "mp4", QUIZ: "xlsx", DOCX: "docx", MBZ: MBZ, 
        "pdf": "pdf", "xml": "xml"}

