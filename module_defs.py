"""."""

import os

DIRECTORY = r"D:\MOOC_Intell-Art ASP. Pratici\delivery"

# Impostazioni del programma
SCENEGGIATURA = os.path.join(DIRECTORY,"00_Sceneggiatura_MOOC_IA_aspetti-pratici.xlsx")
SYMBOL = "Int. artific. aspetti pratici"

# "Nome File ([nomeCorso]_lez[NumLezione]_parte[NumParte])"
COLONNA_DA_LEGGER = 3
NR_RIGA_INIZIO_DATI = 8


NR_COL_FNAME = 5 # dovrebbe essere normale
NR_COL_FNAME = 7 # mio spreadsheet modificato
NR_COL_TIPO_FILE = NR_COL_FNAME+1
NR_COL_FNAME1 = 4

SEP_FNAME = "_"

NOME_CORSO = "Intelligenza Artificiale Base"

SLIDES = "Slides pdf"
QUIZ = "Quiz"
VIDEO = "Video"
DOCX = "docx"
XML = "xml"
MBZ = "mbz"

FILES_ATTESI_L = [SLIDES, VIDEO, QUIZ, DOCX, XML, "mbz", "xlsx" , "pdf" ]

# per appendere estensione giusta
EXTS = {SLIDES: "pdf", VIDEO: "mp4", QUIZ: "xlsx", DOCX: "docx", MBZ: MBZ, 
        "pdf": "pdf", "xml": "xml"}

