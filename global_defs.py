"""Definitions global to the project.

Should 
- not contain code unless trivial and strictly necessary for definitions
- not depend on other file
Eventual files of personal trivial tiny util functions should be in their own
file or module independent from this (and any other file)
"""

import os
from os.path import join

# hack to use modules locally copied within the workspace because they might be 
# extended/improved when beomg used by this
# import sys
# if "." not in sys.path:
#     sys.path.insert(0, ".")

from logdef_local import log
 

def get_env_var(varname, exit_if_undefined = True, exit_if_not_dir = False):
    
    if not varname in os.environ.keys():
        msg = "environment variable '{}' not found".format(varname)
        if exit_if_undefined:
            log.error(msg+" EXITING")
            exit(1)
        else:
            log.warning(msg + " setting it to empty string")
            val = ""
    else:
        val = os.environ[varname]

    if exit_if_not_dir and not os.path.isdir(val):
        log.error("environment variable %s value %s  is not a directory. EXITING" %(varname, val))
        sys.exit(1)

    return val



#####################################################################
#                           DIRECTORIES
#####################################################################
# --- root directories ----
GDRIVE_ENRICO200165_ROOT =  get_env_var('GDRIVE_ENRICO200165_HOME',exit_if_not_dir=True)
GDRIVE_GALILEI_ROOT =  os.path.join(get_env_var('GDRIVE_GALILEI_HOME',exit_if_not_dir=True), 
    'H:/My Drive/enrico_galilei_classi')

USERPROFILE_DIR = get_env_var('USERPROFILE',exit_if_not_dir=True)

# DIR_DOWNLOADS = join(USERPROFILE_DIR, "gclass_loc_download")
DIR_DOWNLOADS = get_env_var('TEMP',exit_if_not_dir=True)


# --- credentials and token paths ---
config_file_path = join(GDRIVE_ENRICO200165_ROOT, "08_dev_gdrive", "configs", "google_classroom","education.ini")
if not os.path.isfile(config_file_path):
    log.error(f"Not found config file path: {config_file_path}")
    exit(1)

oauth_token_filedir = join(GDRIVE_ENRICO200165_ROOT, "08_dev_gdrive", "configs", "google_classroom")
if not os.path.isdir(oauth_token_filedir):
    log.error(f"Not found tokens directory: {oauth_token_filedir}")
    exit(1)
glcassroom_oauth_token_filepath = join(oauth_token_filedir, "token_gclassroom.json")
GDRIVE_TOKEN_FILE_PATHNAME     = join(oauth_token_filedir, "token_gdrive.json")
gmail_oauth_token_filepath      = join(oauth_token_filedir, "token_gmail.json")
gcalendar_oauth_token_filepath  = join(oauth_token_filedir, "token_gcalendar.json")


credentials_file_dir = oauth_token_filedir
if not os.path.isdir(credentials_file_dir):
    log.error(f"Not found credentials directory: {credentials_file_dir}")
    exit(1)

#enrico200165_credentials   = "client_secret_235502692513-dcc97c4geg6kea8umr8au52eqlqgn6cu.apps.googleusercontent.com.json"

# https://console.developers.google.com/apis/credentials?hl=it&orgonly=true&project=classroom-00&supportedpurview=organizationId
enrico_galilei_credentials = "client_secret_762622398402-3je8ufvkg8hcruniearrnp14nffbk2fm.apps.googleusercontent.com.json"

CREDENTIALS_FILE_PATHNAME = os.path.join(credentials_file_dir, enrico_galilei_credentials)



