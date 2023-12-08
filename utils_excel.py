
import os
import pandas as pd
import module_defs as mdefs


def leggi_valori_da_sheet(nome_file, nome_foglio, colonna, riga_iniziale):
    # legge i valori di tutte le colonne piene
    # ritorna ( titolo del corso , i valori dell compresi nella matrice dello spreadshee )

    if not os.path.isfile(nome_file):
        print(f"non trovato file: {nome_file}")
        return None, None

    # Leggi il file spreadsheet utilizzando pandas
    df = pd.read_excel(nome_file, sheet_name=nome_foglio)

    # Seleziona i valori della colonna specificata
    valori_colonna = df.iloc[riga_iniziale:, :]
    titolo = df.iloc[2][mdefs.NR_COL_OFFSET+1]

    return titolo, valori_colonna
