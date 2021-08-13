from pathlib import Path
import shutil

def make_test_file_structure(file_path):
    """
    For testing purposes
    """
    Path(file_path).mkdir(exist_ok=True) # makes a dir if it's not already there

    with open("{0}/file1".format(file_path), 'w'): pass
    with open("{0}/file2".format(file_path), 'w'): pass
    with open("{0}/.hidden".format(file_path), 'w'): pass


def remove_test_file_structure(file_path):
    """
    For testing purposes
    """
    shutil.rmtree(file_path)


def remove_google_drive_folder(service, folder_id):
    """
    Removes the specified Google Drive folder
    """
    file = service.files().delete(fileId=folder_id).execute()
