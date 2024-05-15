import pytest
from unittest.mock import patch, MagicMock
from ccbox.authentication import Authentication
import hashlib


@pytest.fixture
def mock_user_database(mocker):
        mock_db = mocker.Mock()
        Authentication.user_database = mock_db
        return mock_db

def test_generate_password(mocker):
        mocker.patch('secrets.choice', return_value='a')
        password = Authentication.generate_password(12)
        assert password == 'aaaaaaaaaaaa'

def test_hash_password():
        password = 'test_password' 
        hashed_password = Authentication.hash_password(password)
        expected_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        assert hashed_password == expected_hash

def test_register(mocker):
        mocker.patch('builtins.input', side_effect=['new_user', ''])
        mocker.patch('getpass4.getpass', return_value='new_password')
        mocker.patch.object(Authentication, 'user_exists', return_value=False)
        mocker.patch.object(Authentication, 'validate_input', return_value=True)
        mock_save_user = mocker.patch.object(Authentication, 'save_user')
        mock_login = mocker.patch.object(Authentication, 'login', return_value=True)

        Authentication.register()
        
        mock_save_user.assert_called_once()
        mock_login.assert_called_once_with('new_user', 'new_password')


def test_login(mock_user_database, mocker):
        mocker.patch('builtins.input', side_effect=['existing_user', 'password'])
        mocker.patch('getpass4.getpass', return_value='password')
        mock_authenticate_user = mocker.patch.object(Authentication, 'authenticate_user', return_value=True)
        mock_user = MagicMock()
        mock_user.virtual_drive = MagicMock()
        mock_user_database.get_user_from_db.return_value = mock_user
        
        assert Authentication.login()
        mock_user.virtual_drive.unlock.assert_called_once()
        mock_user.virtual_drive.drive_main.assert_called_once_with(
                curr_user=mock_user, _save=Authentication.user_database.update_virtual_drive_in_db)


def test_main_register(mocker):
        mocker.patch('builtins.input', side_effect=['1', 'new_user', ''])
        mocker.patch('getpass4.getpass', return_value='new_password')
        mock_register = mocker.patch.object(Authentication, 'register')

        Authentication.main()
        
        mock_register.assert_called_once()

def test_main_login(mocker):
        mocker.patch('builtins.input', side_effect=['2', 'existing_user', 'password'])
        mocker.patch('getpass4.getpass', return_value='password')
        mock_login = mocker.patch.object(Authentication, 'login', return_value=True)

        Authentication.main()
        
        mock_login.assert_called_once()