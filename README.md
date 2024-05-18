# Virtual Drive Management System

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Authentication](#authentication)
  - [Virtual Drive](#virtual-drive)
  - [Web Server](#web-server)
  - [API Server](#api-server)
- [Database Integration](#database-integration)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project is a Virtual Drive Management System that allows users to register, log in, and manage their virtual drives. The system supports mounting directories and interacting with Azure Storage. It includes a web server implemented with Flask and Tornado, and an API server for CLI interactions.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   ```

2. Set up a virtual environment and install dependencies:
   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Install teh module:
   ```sh
   python install .
   ```

## Usage

### Authentication

The `authentication.py` module handles user registration and login. Here is an example of how to use it:

```python
from ccbox.authentication import Authentication

# Register a new user
authenticated_user = Authentication.register("username", "password")

# Log in an existing user
authenticated_user = Authentication.login("username", "password")
```

### Virtual Drive

The `virtual_drive.py` module allows users to manage their virtual drives. Here is an example of how to use it:

```python
from ccbox.virtual_drive import Virtual_Drive, Folder

# Initialize a virtual drive
virtual_drive = Virtual_Drive()

# Mount a directory
virtual_drive.mount_directory("/path/to/mount")

# Add Azure Storage Handler and upload contents
from ccbox.storage_handler import AzureStorageHandler
account_url = 'https://saccbox.blob.core.windows.net'
container_name = f'virtual-drive-{virtual_drive._id}'
azure_storage = AzureStorageHandler(account_url, container_name=container_name)
virtual_drive.add_remote(azure_storage)
virtual_drive.upload_contents()
```

### Web Server

The web server is implemented using Flask and Tornado. It provides endpoints for user registration, login, and virtual drive management.

#### Running the Web Server

1. Ensure you have the `web_server.py` script ready as provided earlier.

2. Start the web server:
   ```sh
   python web_server.py
   ```

3. The server will start on port 5000 by default. You can access the following endpoints:

   - **Register a new user:**
     ```sh
     curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d '{"username":"yourusername","password":"yourpassword"}'
     ```

   - **Log in a user:**
     ```sh
     curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"username":"yourusername","password":"yourpassword"}'
     ```

   - **Mount a directory:**
     ```sh
     curl -X POST http://localhost:5000/mount -H "Content-Type: application/json" -d '{"username":"yourusername","dir_path":"/path/to/mount"}'
     ```

   - **Get virtual drive contents:**
     ```sh
     curl -X GET http://localhost:5000/virtual_drive/yourusername/contents
     ```

### API Server

The API server provides CLI-based interactions with the Virtual Drive Management System.

#### Running the API Server

1. Ensure you have the `api_server.py` script ready as provided earlier.

2. Start the API server:
   ```sh
   python api_server.py
   ```

3. The server will run on `localhost` and port `9999` by default. The setup.py scirpt has an entry point to the cli.py file so you will be able to run the commands from your command line interface.:

   ```sh
   ccbox
   ```

4. Available commands include:
   - **Register a new user:**
     ```sh
     ccbox register --username <username> --password <password>
     ```
     Follow the prompts to enter username and password.

   - **Log in a user:**
     ```sh
     ccbox login --username <username> --password <password>
     ```
     Follow the prompts to enter username and password.
   
   - **Mount:**
     ```sh
     ccbox mount --username <username> --dir <dir_path>
     ```
     Follow the prompts to enter the mounted directory's path.
   
   - **Contents:**
     ```sh
     ccbox contents --username <username> 
     ```
     Follow the prompts to enter the mounted directory's path.

   - **Quit the connection:**
     ```sh
     ccbox quit
     ```

### Database Integration

The application uses SQLite for database integration. Here is an example of user database interaction. Currently there is not threading implementation:

```python
import sqlite3

class UserDatabase:
    def __init__(self, db_path='users.db'):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        self.connection.commit()

    def add_user(self, username, password):
        self.cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        self.connection.commit()

    def get_user(self, username):
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()

    def user_exists(self, username):
        user = self.get_user(username)
        return user is not None

# Example usage
user_db = UserDatabase()
user_db.add_user('testuser', 'testpass')
print(user_db.user_exists('testuser'))
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---
