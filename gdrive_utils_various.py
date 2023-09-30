"""Check  https://developers.google.com/drive/api/v3/quickstart/python .

files in folders
https://stackoverflow.com/questions/41741520/how-do-i-search-sub-folders-and-sub-sub-folders-in-google-drive
You can use &fields=files(*) to get all of the file's fields.

--- important ---
https://developers.google.com/drive/api/v3/mime-types
"""

from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
from googleapiclient.http import MediaIoBaseDownload
import shutil

from pathlib import Path

from  logdef_local import log
#import ev2001_gdrive_utils.module_defs as md
# import ev2001_utils_tiny.main_test as lu_g
# import ev2001_utils_tiny.oper_sys as sou


FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
ALL_FILE_FIELDS = "*"

NON_DOWNLOADABLE_MIME_TYPES = [
    "application/vnd.google-apps.site",
    "vnd.google-apps.form",
]
MUST_EXPORT_MIME_TYPES = [
    "google-apps.spreadsheet", 
    "google-apps.document", 
    ]
# https://developers.google.com/drive/api/v3/ref-export-formats
EXPORT_FORMAT_FOR_D = {
    'application/vnd.google-apps.spreadsheet': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',"xlsx"],
    'application/vnd.google-apps.document'   : ['application/vnd.openxmlformats-officedocument.wordprocessingml.document','docx']
}


# If modifying these scopes, delete the file token.json.

def create_gdrive_service(scopes, token_file_path, credentials_file_path):
    """Create service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # if os.path.exists('token.json'):
    if os.path.exists(token_file_path):
        creds = Credentials.from_authorized_user_file(token_file_path, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file_path, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return None
    return service


def must_export(mime_type):
    """Say if export is necessary, because download not possibile."""
    for x in MUST_EXPORT_MIME_TYPES:
        if x in mime_type:
            return True
    return False


def get_file_from_id_name(file_id, file_name, gdrive_service):
    """Get file by name and id."""
    page_token = None
    while True:
        query = "name='{}'".format(file_name)
        response = gdrive_service.files().list(spaces='drive', q = query, 
            fields='nextPageToken, files({})'.format(ALL_FILE_FIELDS),
            pageToken=page_token).execute()

        for file in response.get('files', []):
            if file.get('id') == file_id:
                return file
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    log.warn("not found file for name = {} - id = {}".format(file_name, file_id))
    return None


def get_mime_type_from_id_name(file_id, file_name, gdrive_service):
    """."""
    file_d = get_file_from_id_name(file_id, file_name, gdrive_service)
    if file_d is None:
        log.error("file_d is None for file name: {} - id: {}".format(file_name, file_id))
        return None
    mime_type = file_d.get("mimeType")
    return mime_type


def download_file_low_level(file_id, file_name, file_link, dest_dir, mime_type, gdrive_service_initialized, 
    remove_if_present = False):
    """Manage the details of GDrive file download."""
    if mime_type is None:
        mime_type = get_mime_type_from_id_name(file_id, file_name, gdrive_service_initialized)
        if mime_type is None:
            log.warn("unable to download file\nname: {}\nid: {}\nlink: {}".format(file_name, file_id, file_link))
            return None

    for mt in NON_DOWNLOADABLE_MIME_TYPES:
        if mt in mime_type:
            log.warning("non downloadable mime type, ignoring: {}".format(mime_type))
            return None
    try:
        extension = ""
        if must_export(mime_type):
            if mime_type in EXPORT_FORMAT_FOR_D.keys():
                export_mime_type = EXPORT_FORMAT_FOR_D[mime_type][0]
                extension =    "."+EXPORT_FORMAT_FOR_D[mime_type][1]
            request = gdrive_service_initialized.files().export_media(fileId=file_id, mimeType=export_mime_type)
        else:
            request = gdrive_service_initialized.files().get_media(fileId=file_id)


        dest_fpath = os.path.join(dest_dir, sou.adjust_4_file_name(file_name) + extension)
        if not os.path.isdir(dest_dir):
            dest_dir = lu_g.create_dir(dest_dir)

        if remove_if_present and os.path.exists(dest_fpath) and Path(dest_fpath).is_file():
            os.remove(dest_fpath)
            log.info("removed {}".format(file_name))

        # This is where it downloads the file
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            log.debug("Download %d%%." % int(status.progress() * 100))
        fh.seek(0)
        with open(dest_fpath, 'wb') as f:
            shutil.copyfileobj(fh, f)
            return dest_fpath

    except Exception as e:
        log.warning("file download failed\nname: {}\nmime-type: {}\nid: {}".format(file_name, mime_type, file_id) +"\n"+str(e)+"\n")
        return None


def download_file_grdv_entry(gdrv_entry, dest_dir, gdrive_service_initialized, remove_if_present):
    """Download an attachment file of a submission."""
    ret = download_file_low_level(file_id = gdrv_entry['id'], file_name = gdrv_entry['name'], 
        mime_type = gdrv_entry['mimeType'], dest_dir = dest_dir, 
        gdrive_service_initialized=gdrive_service_initialized, 
        remove_if_present = remove_if_present)
    return ret


def download_file_submission_entry(subm_file_entry, dest_dir, gdrive_service_initialized, remove_if_present):
    """Download an attachment of a submisssion."""
    info = subm_file_entry['driveFile']

    ret = download_file_low_level(file_id = info['id'], file_name = info['title'], 
        file_link = info['alternateLink'], mime_type = None, dest_dir = dest_dir, 
        gdrive_service_initialized=gdrive_service_initialized, remove_if_present = remove_if_present)
    
    return ret


dest_dir = os.path.join("f:/","temp_cancella")

def test_gdrive(gdrive_scopes, gdrive_oauth_token_filepath, gdrive_credentials_filepath):
    """Test. quick&dirty try, check https://developers.google.com/drive/api/v3/search-files#python ."""
    gdrive_service = create_gdrive_service(gdrive_scopes, gdrive_oauth_token_filepath, gdrive_credentials_filepath)

    nr_examined = 0
    continua = True
    page_token = None
    scaricati = 0
    while continua:
        # response = gdrive_service.files().list(q="mimeType='image/jpeg'",
        response = gdrive_service.files().list(spaces='drive',
                                            fields='nextPageToken, files({})'.format(ALL_FILE_FIELDS),
                                            pageToken=page_token).execute()
        for item in response.get('files', []):
            nr_examined = nr_examined+1
            if nr_examined > 50:
                continua = False
                break
            # Process change
            mime_type = item['mimeType']
            owner0 = item['owners'][0]
            log.info(u"file: '{}' - owner[0]: '{}' - mimetype: '{}'".format(item['name'], owner0['emailAddress'], item['mimeType']))
            # log.info(u'{4} <{0}> {2} mio {3} <{1}>'.format(item['name'], item['id'], owner0['emailAddress'], 
            # owner0['me'], item['kind']))
            if mime_type == FOLDER_MIME_TYPE:
                log.info("folder")
            else:
                download_file_low_level(file_id = item['id'], file_name = item['name'], mime_type = item['mimeType'],
                dest_dir = dest_dir, gdrive_service_initialized=gdrive_service, remove_if_present = True)

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
        if not continua:
            break

if __name__ == '__main__':
    import inspect, os.path
    cur_frame = inspect.currentframe()
    if cur_frame is not None: # useless, done just to learn
        filename = inspect.getframeinfo(cur_frame).filename
        path     = os.path.dirname(os.path.abspath(filename))
        print(f'running, as {__name__} the file {os.path.join(path,filename)}')