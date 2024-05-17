from typing import Union, List, Dict, Optional, Any, ClassVar
from dataclasses import dataclass, field, asdict
import secrets
import string
import hashlib
from itertools import count
import json

from ccbox.virtual_drive import Virtual_Drive
from ccbox.user import User, UserDatabase



class Authentication:
        USER_DETAILS_FILEPATH: ClassVar[str] = "../data/users.txt"
        DEFAULT_PASSWORD_LENGTH: ClassVar[int] = 12
        INVALID_LENGTH_MESSAGE: ClassVar[str] = f'''
        Password length must be between 8 and 16. 
        Password length must be a number.
        Generating password with default length of {DEFAULT_PASSWORD_LENGTH} characters.
        '''

        user_database: UserDatabase = UserDatabase("../data/users.db")

        @classmethod
        def generate_password(cls, length: Optional[int]=12) -> str:
                characters = string.ascii_letters + string.digits + string.punctuation
                pwd = ''.join(secrets.choice(characters) for _ in range(length))
                return pwd
        
        @classmethod
        def hash_password(cls, pwd: str) -> str:
                """
                Hash a password using SHA-256 algorithm
                """
                pwd_bytes = pwd.encode('utf-8')
                hashed_pwd = hashlib.sha256(pwd_bytes).hexdigest()
                return hashed_pwd
        
        @classmethod
        def save_user(cls, username: str, hashed_pwd:str) -> None:
                """Save user-details to the users db and file"""
                with open(cls.USER_DETAILS_FILEPATH, "a") as f:
                        f.write(f"{username} {hashed_pwd}\n")
                
                curr_user = User(username=username)
                cls.user_database.add_user_to_db(curr_user)                
                
        
        @classmethod
        def user_exists(cls, username: str) -> bool:
                """Check if users exists in database"""
                user = cls.user_database.get_user_from_db(username)
                return user is not None

        @classmethod
        def authenticate_user(cls, username: str, password: str) -> bool:
                try:
                        with open(cls.USER_DETAILS_FILEPATH, "r") as f:
                                for line in f:
                                        items = line.split()
                                        if items[0] == username and items[1] == cls.hash_password(password):
                                                return True
                                return False
                except:
                        raise ValueError("Invalid password storage location")
                        return False


        @classmethod
        def validate_input(cls, password: str) -> bool:
                try:
                        password_length = len(password)
                        if password_length < 8 or password_length > 16:
                                raise ValueError("Password length must be between 8 and 16")
                        return True
                except ValueError:
                        print(cls.INVALID_LENGTH_MESSAGE)
                        return False
        @classmethod
        def register(cls, username:str, pwd:str) -> None:
                if cls.user_exists(username):
                        print("User already exists.")
                        return
                if pwd != "":
                        if not cls.validate_input(pwd):
                                cls.register()
                        else:
                                password = pwd
                else:
                        password = cls.generate_password(cls.DEFAULT_PASSWORD_LENGTH)
                        print("Your password is:", password)

                hashed_password = cls.hash_password(password)
                cls.save_user(username, hashed_password)
                print("User created successfully. You will now be logged in.\n")
                authenticated_user = cls.login(username, password)
                return authenticated_user

        @classmethod
        def login(cls, username: Optional[str] = "", password: Optional[str] = "") -> "User":
                if not cls.user_exists(username):
                        print("User does not exist.")
                        return False

                if not cls.authenticate_user(username, password):
                        print("Incorrect username or password.")
                        return None

                authenticated_user = cls.user_database.get_user_from_db(username)
                print("Login successful.\n")
                return authenticated_user
                

