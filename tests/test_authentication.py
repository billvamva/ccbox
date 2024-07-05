import pytest
from unittest.mock import patch, Mock, MagicMock
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
        mocker.patch.object(Authentication, 'user_exists', return_value=False)
        mocker.patch.object(Authentication, 'validate_input', return_value=True)
        mocker.patch.object(Authentication, 'save_user')
        mocker.patch.object(Authentication, 'login', return_value=MagicMock())
        
        authenticated_user = Authentication.register('username', 'password')
        assert authenticated_user


def test_login(mock_user_database, mocker):
        mock_user_db = mocker.patch('ccbox.authentication.UserDatabase')
        mock_user_db().get_user_from_db.return_value = MagicMock()
        mocker.patch.object(Authentication, 'user_exists', return_value=True)
        mocker.patch.object(Authentication, 'authenticate_user', return_value=True)

        authenticated_user = Authentication.login('username', 'password')
        assert authenticated_user


def test_login_non_existing_user(mock_user_database):
        username = "non_existing_user"
        password = "test_password"
        with patch.object(Authentication, 'user_database', mock_user_database):
                # Execute
                authenticated_user = Authentication.login(username, password)
                # Assert
                assert authenticated_user is None
