import requests



register_data = {
    'username': 'example_user',
    'password': 'example_password'
}
response = requests.post('http://localhost:5000/register', json=register_data)
print(response.json())  # Output: {'message': 'User created and logged in successfully'}

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
    'dir_path': '/path/to/directory'
}
response = requests.post('http://localhost:5000/mount', json=mount_data)
print(response.json())  # Output: {'message': 'Directory mounted successfully'}

# Get virtual drive contents
response = requests.get('http://localhost:5000/virtual_drive/example_user/contents')
print(response.json())  # Output: Virtual drive contents JSON data