import unittest
from main import *
from utils import *


FILE_PATH = 'test_folder'
GDRIVE_FOLDER = 'test_backup'
BACKUPS_TO_KEEP = 1


class TestSetEnvVars(unittest.TestCase):


    def test_set_env_vars(self):
        """
        Assert that it raises error without filepath there
        """
        set_envvars()



class TestConnectGDrive(unittest.TestCase):

    def test_connect(self):
        """
        Test that it can connect to GDrive
        (no assertions can be made)
        """
        service = connect_gdrive()


class TestFolderFunctions(unittest.TestCase):

    def setUp(self):
        self.file_path = "test_folder"

    def tearDown(self):
        remove_test_file_structure(self.file_path)

    def test_create_folder(self):
        """
        Test that it can create folders locally
        """
        make_test_file_structure(self.file_path)

    def test_tar(self):
        """
        Test that it can create folders locally
        """
        make_test_file_structure(self.file_path)
        make_tarfile("test.tar.gz", self.file_path)

    def test_package(self):
        """
        Test that it can create folders locally
        """
        make_test_file_structure(self.file_path)
        file_package(self.file_path)



class TestFolderMissingFunctions(unittest.TestCase):

    def setUp(self):
        self.file_path = "test_folder"


    def test_package_does_not_exist(self):
        """
        Assert that it raises error without filepath there
        """
        self.assertRaises(FileNotFoundError, file_package, self.file_path)








class TestGoogleFolderFunctions(unittest.TestCase):

    def setUp(self):
        self.gdrive_folder = "test_gdrive"
        self.service = connect_gdrive()

    def tearDown(self):
        remove_google_drive_folder(self.service, self.folder_id)

    def test_create_folder(self):
        """
        Test that it can add folder to gdrive when it doesn't exist
        """
        self.folder_id = None 
        self.folder_id = google_drive_folder(self.service, self.gdrive_folder) # creates folder
        self.assertIsNotNone(self.folder_id)
        # then goes on to create duplicate folder
        file_metadata = {
            'name': self.gdrive_folder,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.service.files().create(body=file_metadata,
                                            fields='id').execute()
        self.assertRaises(
            Exception,
            google_drive_folder,
            service=self.service,
            gdrive_folder=self.gdrive_folder) # ensures that function raises error

        remove_google_drive_folder(self.service, file.get('id')) # cleans up, removing second folder
        # then checks with the one folder
        self.folder_id_again = google_drive_folder(self.service, self.gdrive_folder)
        self.assertEqual(self.folder_id, self.folder_id_again)


class TestRun(unittest.TestCase):

    def setUp(self):
        self.service = connect_gdrive()
        make_test_file_structure(FILE_PATH)
        self.folder_id = google_drive_folder(self.service, GDRIVE_FOLDER) # creates folder

    def tearDown(self):
        remove_test_file_structure(FILE_PATH)
        remove_google_drive_folder(self.service, self.folder_id)


    def test_run(self):
        """
        Test the run function without any files in GDrive (to ensure none are deleted)
        """
        files_deleted = run(FILE_PATH, GDRIVE_FOLDER, BACKUPS_TO_KEEP)
        self.assertEqual(files_deleted, 0)


    def test_delete_with_files(self):
        """
        Test the delete function with multiple files in GDrive to ensure they are deleted
        """
        times_to_upload = 5
        index = 0
        folder_id = google_drive_folder(self.service, GDRIVE_FOLDER) # gets the folder
        while index < times_to_upload:
            
            file_name = file_package(FILE_PATH) # zips the file
            upload(self.service, file_name, folder_id) # uploads the file
            index += 1
        files = google_drive_folder_children(self.service, folder_id)
        self.assertEqual(len(files), times_to_upload) # assert that five files have been uploaded as expected
        files_which_should_be_deleted = len(files) - BACKUPS_TO_KEEP
        files_deleted = google_drive_delete(self.service, files, BACKUPS_TO_KEEP)
        self.assertEqual(files_deleted, files_which_should_be_deleted) # assert that the correct number have been deleted


if __name__ == '__main__':
    unittest.main()

