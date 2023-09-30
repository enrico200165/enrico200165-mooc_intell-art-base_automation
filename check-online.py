

import os

import googleapiclient
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import pandas as pd

from logdef_local import log

import global_defs as gdfs

# ------------------------------------------------------------------------------------

GDRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive',
    #'https://www.googleapis.com/auth/drive.metadata',
    ]
# Create a token.json file to store the OAuth 2.0 credentials (or use an existing one)
GSHEETS_SCOPES = [ 'https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES_ALL = GDRIVE_SCOPES+GSHEETS_SCOPES

TOKEN_JSON_PATH = gdfs.GDRIVE_TOKEN_FILE_PATHNAME

SPREADSHEET_ID = '1jY-QLTytaH3w3ruIjTVW6O_ZjeKrwDo_' # excel deve essere scaricato, API non funziona
FOLDER_ID = '1xTG6zdigZEHXBlqtDTbq6p35JE_Rv8oL'



def scarica_file(service_gdrive, file_id):

    # creds_gdrive = flow_sheets.run_local_server(port=0)

    try:
        # Get the file metadata
        file_metadata = service_gdrive.files().get(fileId=file_id,
                                                supportsAllDrives=True,).execute()

        # Get the file's name
        file_name = file_metadata['name']

        # Download the file
        request = service_drive.files().get_media(fileId=file_id)
        file_path = os.path.join(file_name)

        with open(file_path, 'wb') as file:
            downloader = googleapiclient.http.MediaIoBaseDownload(file, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%")

        print(f"Downloaded '{file_name}' to '{file_path}'.")
        return file_name

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

    return False



def files_in_gdrive_folder(service, folder_id):
# List files in the specified folder
    files_in_folder = []

    folder_query = f"'{folder_id}' in parents"
    folder_files = service.files().list(q=folder_query, supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    folder_file_names = [file['name'] for file in folder_files.get('files', [])]

    for file_name in folder_file_names:
        # print(f"'{file_name}' is present in the folder.")
        files_in_folder.append(file_name)

    return files_in_folder


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



def files_in_sceneggiatura(service_drive, spreadsheet_id):

    fname = scarica_file(service_drive, spreadsheet_id)


    titolo, valori_colonna = leggi_valori("./"+fname,
                                        "Int. artific. aspetti pratici",  
                                        colonna = 7, riga_iniziale = 6)

    files_in_sceneggiatura = valori_colonna.iloc[:, 7].values.tolist()
    files_in_sceneggiatura = [x for x in files_in_sceneggiatura if str(x) != 'nan']

    return files_in_sceneggiatura




flow_common = InstalledAppFlow.from_client_secrets_file(
    gdfs.CREDENTIALS_FILE_PATHNAME, SCOPES_ALL)
creds_common = flow_common.run_local_server(port=0)
service_drive = build('drive', 'v3', credentials=creds_common)


files_in_sceneggiatura = files_in_sceneggiatura(service_drive, SPREADSHEET_ID)
files_in_folder = files_in_gdrive_folder(service_drive, FOLDER_ID)

set_in_sceneggiatura = set(files_in_sceneggiatura)
set_in_folder = set(files_in_folder)

mancanti = list(set_in_sceneggiatura.difference(set_in_folder))
print("-"*10+f"files non trovati {len(mancanti)}")
for mancante in mancanti:
    print(f"manca: {mancante}")

eccessi = list(set_in_folder.difference(set_in_sceneggiatura))
print("\n"*2)
print("-"*10+f"files non in eccesso {len(eccessi)}")
for eccesso in eccessi:
    print(f"eccesso: {eccesso}")

print("")

#for i, fname in enumerate(in_folder):
#     print(f"'{i:>3}: {fname}' is present in the folder.")



