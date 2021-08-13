# for envvars
import os
import os.path

# for Google Drive authentication
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apiclient.http import MediaFileUpload

# to compress files
import tarfile
import datetime

import utils



FILE_PATH = "test_folder"
GDRIVE_FOLDER = "Home Assistant Backupss"

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']



def connect_gdrive():
    """
    Connects to Google Drive API and returns the service. 
    Adapted from https://developers.google.com/drive/api/v3/quickstart/python
    """
    creds = None
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

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
        print("Your FILE_PATH variable is incorrect. Is {0} definitely a directory?".format(file_path))
        raise


def google_drive_folder(service, gdrive_folder):
    """
    Creates or retrieves the specified Google Drive folder
    """
    # Checks to see if the folder already exists by searching
    query_string = "mimeType='application/vnd.google-apps.folder' and name = '{0}'".format(gdrive_folder)
    response = service.files().list(q=query_string,
                                          spaces='drive',
                                          fields='files(id, name)').execute()
    
    num_of_folders = len(response.get('files')) # checks how many folders are returned
    if num_of_folders > 1: # multiple folders of the same name, so abort and tell user to delete
        # raises exception to delete one
        print("You have multiple folders in Google Drive called '{0}'. Please delete one and empty it from the Trash".format(gdrive_folder))
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



def upload(service, folder_id):
    file_name = file_package(FILE_PATH)
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
        }
    media = MediaFileUpload(file_name, mimetype='application/x-tar')
    file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    return file.get('id')



if __name__ == '__main__':
    service = connect_gdrive()
    folder_id = google_drive_folder(service, GDRIVE_FOLDER)
    upload(service, folder_id)