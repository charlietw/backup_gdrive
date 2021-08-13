import unittest
from main import *
from utils import *

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


        



if __name__ == '__main__':
    unittest.main()

