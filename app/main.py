# for envvars
import os
import os.path

import logging
logging.basicConfig(level=logging.INFO)

# for Google Drive authentication
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


from apiclient.http import MediaFileUpload

# to compress files
import tarfile
import datetime

from utils import *


def set_envvars():
    """
    Asserts that all required env vars are present and raises error if not
    Sets config from envvars if all present
    """
    try:
        if not "FILE_PATH" in os.environ:
            logging.error("Please set a FILE_PATH env var")
            raise FileNotFoundError
        if not "GDRIVE_FOLDER" in os.environ:
            logging.error("Please set a GDRIVE_FOLDER env var")
            raise FileNotFoundError
        if not "BACKUPS_TO_KEEP" in os.environ:
            logging.error("Please set a BACKUPS_TO_KEEP env var")
            raise FileNotFoundError
        file_path = os.environ['FILE_PATH']
        gdrive_folder = os.environ['GDRIVE_FOLDER']
        backups_to_keep = int(os.environ['BACKUPS_TO_KEEP'])
        logging.info("All env vars found")
        return file_path, gdrive_folder, backups_to_keep
    except:
        raise


def connect_gdrive(method):
    """
    Connects to Google Drive API, either via a token or service account. 
    Adapted from https://google-auth.readthedocs.io/en/latest/user-guide.html

    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    if method == "token":
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials_token.json', SCOPES)
                creds = flow.run_console()
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    elif method == "service_account":
        credentials = service_account.Credentials.from_service_account_file(
            'credentials_service_account.json')
        creds = credentials.with_scopes(SCOPES)

    service = build('drive', 'v3', credentials=creds)
    return service






def make_tarfile(output_filename, source_dir):
    """
    Takes a directory and puts it in a tar package.
    Source: https://stackoverflow.com/a/17081026
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def file_package(file_path):
    """
    Packages up the file or throws an error
    """
    try:
        if not os.path.isdir(file_path): # if the provided dir isn't a dir, abort
            raise FileNotFoundError
        today = datetime.datetime.today() # formats the backup filename
        file_name = "Home Assistant {0}.tar.gz".format(today.strftime("%d-%m-%Y %H %M"))
        make_tarfile(file_name, file_path)
        return file_name
    except FileNotFoundError:
        logging.error("Your FILE_PATH variable is incorrect. Is {0} definitely a directory?".format(file_path))
        raise


def google_drive_folder(service, gdrive_folder):
    """
    Creates or retrieves the specified Google Drive folder
    """
    # Checks to see if the folder already exists by searching
    query_string = "mimeType='application/vnd.google-apps.folder' and name = '{0}'".format(gdrive_folder)
    response = service.files().list(
        q=query_string,
        spaces='drive',
        fields='files(id, name)').execute()
    
    num_of_folders = len(response.get('files')) # checks how many folders are returned
    if num_of_folders > 1: # multiple folders of the same name, so abort and tell user to delete
        # raises exception to delete one
        logging.error("You have multiple folders in Google Drive called '{0}'. Please delete one and empty it from the Trash".format(gdrive_folder))
        raise Exception

    if num_of_folders == 0: # doesn't exist, so create
        # creates a folder
        file_metadata = {
            'name': gdrive_folder,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = service.files().create(body=file_metadata,
                                            fields='id').execute()
        return file.get('id')

    if num_of_folders == 1: # already exists, so use it
        file = response.get('files')
        return file[0].get('id')


def google_drive_file_age(file):
    """
    Takes a file from GDrive and appends how old it is in days
    """
    created_on = datetime.datetime.strptime(file['createdTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
    now = datetime.datetime.today()
    delta = now - created_on
    file['file_age_days'] = delta.days
    return file['file_age_days']



def google_drive_folder_children(service, folder_id):
    """
    Gets all files in a folder.
    Adapted from https://developers.google.com/drive/api/v2/reference/children/list
    """

    page_token = None
    query_string = "parents in '{0}'".format(folder_id)
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            children = service.files().list(
                q=query_string,
                spaces='drive',
                fields='files(id, name, createdTime)').execute()
            page_token = children.get('nextPageToken')
            if not page_token:
                break
        except Exception as E:
            logging.error('An error occurred: %s' % E)
            break

    return children.get('files') # returns just the JSON


def append_file_age(files):
    """
    Appends the file age to a JSON of GDrive files and sorts them
    """
    files.sort(key = lambda json: json['createdTime'], reverse=False) # sorts so that oldest are first
    for child in files:
        google_drive_file_age(child) # appends age in days
    return files


def google_drive_delete(service, files, backups_to_keep):
    """
    Determines whether or not a file should be deleted according to config
    and returns a boolean
    """
    number_of_files = len(files)
    # print("number of files to start = {0}".format(number_of_files))
    if number_of_files <= backups_to_keep: # not enough files yet, so exit
        return 0
    else:
        index = 0
        while number_of_files > backups_to_keep:
            file_id = files[index]['id'] # gets the file to be deleted
            service.files().delete(fileId=file_id).execute() # deletes the file
            logging.info("Deleted file {0}".format(file_id))
            number_of_files -= 1 # decrements the count
            index += 1
            # print("number of files = {0}, number deleted = {1}".format(number_of_files, index))
        return index



def upload(service, file_name, folder_id):
    """
    Uploads a packaged file to the specificed GDrive folder, returns the file_id
    """
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
        }
    media = MediaFileUpload(file_name, mimetype='application/x-tar')
    file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    logging.info("Successfully created file {0}".format(file.get('id')))

    return file.get('id')


def run(file_path, gdrive_folder, backups_to_keep):
    logging.info(
        "Running backup from '{0}' on the local machine to '{1}' in Google Drive, keeping the most recent {2} backups.".format(
            file_path, gdrive_folder, backups_to_keep))
    service = connect_gdrive("token") # connect to Google
    folder_id = google_drive_folder(service, gdrive_folder) # gets the folder
    file_name = file_package(file_path) # zips the file
    upload(service, file_name, folder_id) # uploads the file
    files = google_drive_folder_children(service, folder_id) # gets the files
    files = append_file_age(files) # adds the file age
    files_deleted = google_drive_delete(service, files, backups_to_keep) # deletes the files
    os.remove(file_name)
    logging.info("Backup successful. {0} files deleted.".format(files_deleted))
    return files_deleted


if __name__ == '__main__':
    file_path, gdrive_folder, backups_to_keep = set_envvars()
    run(file_path, gdrive_folder, backups_to_keep)