import pytest
from unittest.mock import MagicMock
from ccbox.virtual_drive import Virtual_Drive, Folder
import os

@pytest.fixture
def virtual_drive():
        return Virtual_Drive()

def test_virtual_drive_initialization(virtual_drive):
        assert virtual_drive.name == "VD"
        assert virtual_drive.locked is True
        assert 'default' in virtual_drive.folders
        assert virtual_drive.folders['default'].name == 'default'

def test_virtual_drive_unlock_lock(virtual_drive):
        virtual_drive.unlock()
        assert virtual_drive.locked is False
        virtual_drive.lock()
        assert virtual_drive.locked is True

def test_virtual_drive_add_folder(virtual_drive):
        folder = virtual_drive.add_folder("new_folder")
        assert folder.name == "new_folder"
        assert folder in virtual_drive.contents
        assert "new_folder" in virtual_drive.folders

def test_virtual_drive_add_duplicate_folder(virtual_drive):
        virtual_drive.add_folder("new_folder")
        with pytest.raises(Exception) as e:
                virtual_drive.add_folder("new_folder")
        assert str(e.value) == "A folder with the name new_folder already exists."

def test_virtual_drive_add_file(virtual_drive):
        file_obj = MagicMock()
        virtual_drive.add_file(file_obj)
        assert file_obj in virtual_drive.contents

def test_virtual_drive_mount_directory(mocker, virtual_drive):
        # Mock os functions to simulate directory structure
        mocker.patch('os.listdir', return_value=['file1.txt', 'dir1'])
        mocker.patch('os.path.isdir', side_effect=lambda x: x == 'test_path/dir1')
        mocker.patch('os.path.isfile', side_effect=lambda x: x == 'test_path/file1.txt')
        
        # Mock the open function to simulate file objects
        mock_open = mocker.mock_open(read_data="data")
        mocker.patch('builtins.open', mock_open)

        # Mount the directory
        virtual_drive.mount_directory('test_path')

        # Verify the mount directory
        assert 'test_path' in virtual_drive.folders
        mount_folder = virtual_drive.folders['test_path']

        # Check file and directory names in the contents
        content_names = [os.path.basename(f.name) if hasattr(f, 'name') else f.name for f in mount_folder.contents]
        print(content_names)  # Print for debugging
        assert 'file1.txt' in content_names
        assert 'dir1' in mount_folder.folders

def test_virtual_drive_to_dict(virtual_drive):
        virtual_drive.unlock()
        data = virtual_drive.to_dict()
        assert data['virtual_drive_id'] == virtual_drive.virtual_drive_id
        assert data['locked'] is False
        assert 'default' in data['folders']

def test_virtual_drive_add_save_callable_attr(virtual_drive):
        mock_user = MagicMock()
        mock_save_method = MagicMock()
        virtual_drive.add_save_callable_attr(curr_user=mock_user, _save_method=mock_save_method)
        assert virtual_drive.user_obj == mock_user
        assert virtual_drive._save_method == mock_save_method

def test_virtual_drive_save(virtual_drive):
        mock_user = MagicMock()
        mock_save_method = MagicMock()
        virtual_drive.add_save_callable_attr(curr_user=mock_user, _save_method=mock_save_method)
        virtual_drive._save()
        mock_save_method.assert_called_once_with(mock_user)
