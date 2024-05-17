from flask import Flask, request, jsonify
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import threading
import logging

from ccbox.virtual_drive import Virtual_Drive, Folder
from ccbox.user import User, UserDatabase
from ccbox.authentication import Authentication
from ccbox.storage_handler import AzureStorageHandler

app = Flask(__name__)

# Route for registering a new user
@app.route('/register', methods=['POST'])
def register():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
                return jsonify({'error': 'Username and password are required'}), 400
        
        authenticated_user = Authentication.register(username, password)
        if authenticated_user:
                return jsonify({'message': 'User created and logged in successfully'})
        else:
                return jsonify({'error': 'Failed to create user'}), 400

# Route for logging in a user
@app.route('/login', methods=['POST'])
def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
                return jsonify({'error': 'Username and password are required'}), 400
        
        authenticated_user = Authentication.login(username, password)
        if authenticated_user:
                return jsonify({'message': 'Login successful'})
        else:
                return jsonify({'error': 'Incorrect username or password'}), 401

# Route for mounting a directory to virtual drive
@app.route('/mount', methods=['POST'])
def mount_directory():
        data = request.get_json()
        username = data.get('username')
        dir_path = data.get('dir_path')
        
        # Get user from database
        user = Authentication.user_database.get_user_from_db(username)
        if not user:
                return jsonify({'error': 'User not found'}), 404
        
        # Create Azure Storage Handler
        account_url = 'https://saccbox.blob.core.windows.net'
        container_name = f'virtual-drive-{user.virtual_drive._id}'
        azure_storage = AzureStorageHandler(account_url, container_name=container_name)
        
        # Mount directory to virtual drive
        user.virtual_drive.add_remote(azure_storage)
        user.virtual_drive.mount_directory(dir_path)
        
        # Upload contents to Azure Storage
        user.virtual_drive.upload_contents()
        
        return jsonify({'message': 'Directory mounted successfully'})

# Route for accessing virtual drive contents
@app.route('/virtual_drive/<username>/contents', methods=['GET'])
def get_virtual_drive_contents(username):
        # Get user from database
        user = Authentication.user_database.get_user_from_db(username)
        if not user:
                return jsonify({'error': 'User not found'}), 404
        
        # Serialize virtual drive contents to JSON
        virtual_drive_contents = user.virtual_drive.to_dict()
        return jsonify(virtual_drive_contents)


class TornadoServer:
        def __init__(self, flask_app, port):
                self.flask_app = flask_app
                self.port = port
                self.http_server = HTTPServer(WSGIContainer(self.flask_app))
                self.server_thread = threading.Thread(target=self.start_server)
                self.server_thread.daemon = False
                self.server_thread.start()

        def start_server(self):
                try:
                        logging.info(f"Starting Tornado server on port {self.port}")
                        self.http_server.listen(self.port)
                        IOLoop.instance().start()
                except Exception as e:
                        logging.error(f"Failed to start Tornado server: {e}")


if __name__ == '__main__':
        logging.basicConfig(level=logging.ERROR)
        tornado_server = TornadoServer(app, port=5000)  

