"""Create service for both gspread (service account) and normal Google API."""

from __future__ import print_function

import os.path

import gspread

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from logdef_local import log

import global_defs as gd




# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]



CONFIGS_HOME = os.path.join(gd.GDRIVE_ENRICO200165_ROOT,"08_dev_gdrive","configs")
GSHEETS_CREDENTIALS =    os.path.join(CONFIGS_HOME,"google_classroom","client_secret_762622398402-3je8ufvkg8hcruniearrnp14nffbk2fm.apps.googleusercontent.com.json")
GSHEETS_TOKEN =          os.path.join(CONFIGS_HOME,"google_classroom","token.json")
GSHEETS_SRVACC_GSHEETS = os.path.join(CONFIGS_HOME,"google_classroom","service_account.json")



def get_gsheets_service(token_pathname: str = GSHEETS_TOKEN,
 credentials_pathname: str = GSHEETS_CREDENTIALS,
 scopes: list[str] = SCOPES):
    """."""
    creds = None
    # The token file  stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_pathname):
        creds = Credentials.from_authorized_user_file(token_pathname, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_pathname, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_pathname, 'w', encoding="utf-8") as token:
            token.write(creds.to_json())
    try:
        service = build('sheets', 'v4', credentials=creds)
    except HttpError as err:
        log.error(err)
        exit(1)

    return service


def gs_srvacc_srvc(creds_pathnname, token_pathname):
    """Service for service account.

    must have shared sheet with the email OF THE SERVICE ACCOUNT
    """
    gc = gspread.service_account(creds_pathnname)

    return gc


if __name__ == '__main__':
    pass
