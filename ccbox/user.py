
from typing import Union, List, Dict, Optional, Any, ClassVar
from dataclasses import dataclass, field, asdict
import string
from itertools import count
import sqlite3
import json

from virtual_drive import Virtual_Drive, Folder


@dataclass
class User:
        """Class for keeping track of user data"""
        username: str
        _id: int = field(default_factory=lambda: next(User.id_counter))
        virtual_drive: Virtual_Drive = field(default_factory=Virtual_Drive)

        id_counter: count = count()

        def to_dict(self) -> dict:
                return {
                "username": self.username,
                "_id": self._id,
                "virtual_drive": self.virtual_drive.to_dict()
                }
        @classmethod
        def from_dict(cls, data: dict) -> 'User':

                user = cls(username=data["username"], _id=data["_id"])
                user.virtual_drive = Virtual_Drive(virtual_drive_id=data["virtual_drive"]["virtual_drive_id"], locked=data["virtual_drive"]["locked"], _from_dict=True)
                folders = {name: Folder.from_dict(data=f, parent_dir=user.virtual_drive) for name, f in data["virtual_drive"]["folders"].items()}
                for folder_name, folder_obj in folders.items():
                       user.virtual_drive.add_folder(name=folder_name, folder_obj=folder_obj)
                return user


class UserDatabase:
        """Class for interacting with the user database"""

        
        def __init__(self, db_path: str):
                self.db_path = db_path
                self.connection = sqlite3.connect(self.db_path)
                self.cursor = self.connection.cursor()
                self._create_tables()
                self._initialize_counters()

        def _initialize_counters(self):
                self.cursor.execute('SELECT MAX(id) FROM users')
                max_user_id = self.cursor.fetchone()[0]
                if max_user_id is None:
                        max_user_id = 0

                self.cursor.execute('SELECT MAX(json_extract(virtual_drive, "$.virtual_drive_id")) FROM users')
                max_drive_id = self.cursor.fetchone()[0]
                if max_drive_id is None:
                        max_drive_id = 0

                User.id_counter = count(max_user_id + 1)
                Virtual_Drive.id_counter = count(max_drive_id + 1)

        def _create_tables(self):
                self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        virtual_drive TEXT NOT NULL
                )
                ''')
                self.connection.commit()

        def add_user_to_db(self, user_obj: User) -> None:
                user_data = user_obj.to_dict()
                user_data['virtual_drive'] = json.dumps(user_data['virtual_drive'])
                try:
                        self.cursor.execute('''
                                INSERT INTO users (id, username, virtual_drive) VALUES (?, ?, ?)
                        ''', (user_data['_id'], user_data['username'], user_data['virtual_drive']))
                        self.connection.commit()
                except sqlite3.IntegrityError as error:
                        print(error)

        def get_user_from_db(self, username: str) -> Optional[User]:
                self.cursor.execute('''
                SELECT * FROM users WHERE username = ?
                ''', (username,))
                row = self.cursor.fetchone()
                if row:
                        virtual_drive_data = json.loads(row[2])
                        return User.from_dict({
                                "username": row[1],
                                "_id": row[0],
                                "virtual_drive": virtual_drive_data
                        })
                return None
        
        def update_virtual_drive_in_db(self, user_obj: User) -> None:
                """Update virtual drive value in the database for a specific user."""
                user_data = user_obj.to_dict()
                user_data['virtual_drive'] = json.dumps(user_data['virtual_drive'])
                try:
                        self.cursor.execute('''
                                UPDATE users SET virtual_drive = ? WHERE id = ?
                        ''', (user_data['virtual_drive'], user_data['_id']))
                        self.connection.commit()

                except sqlite3.IntegrityError as error:
                        print(error)

        def close(self):
                self.connection.close()