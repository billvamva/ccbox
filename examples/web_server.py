import concurrent.futures
import requests
import threading

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

register_data = [
    {
    'username': 'thread_user_1',
    'password': 'example_password'
    },
    {
    'username': 'thread_user_2',
    'password': 'example_password'
    },
    {
    'username': 'thread_user_3',
    'password': 'example_password'
    },
    {
    'username': 'thread_user_4',
    'password': 'example_password'
    },
]

def register_user(data:dict) -> None:
    session = get_session()
    with session.post('http://localhost:5000/register', json=register_data) as response:
        print(response.json())  # Output: {'message': 'User created and logged in successfully'}
    
def register_users():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for user in register_data:
            futures.append(executor.submit(register_data, data=user))
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

# Log in the user
login_data = {
    'username': 'example_user',
    'password': 'example_password'
}
response = requests.post('http://localhost:5000/login', json=login_data)
print(response.json())  # Output: {'message': 'Login successful'}

# Mount a directory to the virtual drive
mount_data = {
    'username': 'example_user',
    'dir_path': '/Users/vasvamva1/Documents/ccbox/data/mnt'
}
response = requests.post('http://localhost:5000/mount', json=mount_data)
print(response.json())  # Output: {'message': 'Directory mounted successfully'}

# Get virtual drive contents
response = requests.get('http://localhost:5000/virtual_drive/example_user/contents')
print(response.json())  # Output: Virtual drive contents JSON data