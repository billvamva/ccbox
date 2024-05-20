import sys
import threading
import socketserver
from datetime import date
from ccbox.virtual_drive import Virtual_Drive, Folder
from ccbox.user import User, UserDatabase
from ccbox.authentication import Authentication
from ccbox.storage_handler import AzureStorageHandler
from ccbox.log import Logger


class ApiRequestHandler(socketserver.StreamRequestHandler):
        """
        The request handler for our API server.
        """

        help_message = (
                "Available commands\n\r"
                "  -> quit:\t Close connection\n\r"
                "  -> about:\t Prints a short description\n\r"
                "  -> register <username> <password>:\t Register a new user\n\r"
                "  -> login <username> <password>:\t Log in a user\n\r"
                "  -> mount <username> <dir_path>:\t Mount a directory to the virtual drive\n\r"
                "  -> contents <username>:\t Get the contents of the virtual drive\n\r"
        )

        def setup(self):
                socketserver.StreamRequestHandler.setup(self)
                self._logger = Logger()
                self._logger.info("Client connected")

        def handle(self):
                client_info = "Client connected from %s\n\r" % self.client_address[0]
                self.wfile.write(client_info.encode('utf-8'))
                welcome_message = "Welcome to CCBox (%s). Type \"help\" for a list of all available commands.\n\r" % str(date.today())
                self.wfile.write(welcome_message.encode('utf-8'))

                while True:
                        try:
                                command = self.rfile.readline().strip().decode('utf-8').lower()
                                if command:
                                        self.execute_command(command)
                        except Exception as e:
                                print(f"Error: {e}")

        def execute_command(self, command):
                parts = command.split()
                cmd = parts[0]

                try:
                        if cmd == 'quit':
                                self.wfile.write("Closing connection. Hope to see you again!\n\r".encode('utf-8'))
                                return
                        elif cmd == 'exit':
                                sys.exit(2)
                        elif cmd == 'help':
                                self.wfile.write(self.help_message.encode('utf-8'))
                        elif cmd == 'register' and len(parts) == 3:
                                username, password = parts[1], parts[2]
                                response = self.register_user(username, password)
                                self.wfile.write(response.encode('utf-8'))
                        elif cmd == 'login' and len(parts) == 3:
                                username, password = parts[1], parts[2]
                                response = self.login_user(username, password)
                                self.wfile.write(response.encode('utf-8'))
                        elif cmd == 'mount' and len(parts) == 3:
                                username, dir_path = parts[1], parts[2]
                                response = self.mount_directory(username, dir_path)
                                self.wfile.write(response.encode('utf-8'))
                        elif cmd == 'contents' and len(parts) == 2:
                                username = parts[1]
                                response = self.get_virtual_drive_contents(username)
                                self.wfile.write(response.encode('utf-8'))
                        else:
                                self.wfile.write("Invalid command\n\r".encode('utf-8'))
                except ConnectionResetError:
                        self._logger.error("Broken pipe: client disconnected while sending response")

        def register_user(self, username, password):
                if not username or not password:
                        return "Username and password are required\n\r"

                authenticated_user = Authentication.register(username, password)
                if authenticated_user:
                        return "User created and logged in successfully\n\r"
                else:
                        return "Failed to create user\n\r"

        def login_user(self, username, password):
                if not username or not password:
                        return "Username and password are required\n\r"

                authenticated_user = Authentication.login(username, password)
                if authenticated_user:
                        return "Login successful\n\r"
                else:
                        return "Incorrect username or password\n\r"

        def mount_directory(self, username, dir_path):
                user = Authentication.user_database.get_user_from_db(username)
                if not user:
                        return "User not found\n\r"
                
                print(user.username)

                account_url = 'https://saccbox.blob.core.windows.net'
                container_name = f'virtual-drive-{user.virtual_drive._id}'
                azure_storage = AzureStorageHandler(account_url, container_name=container_name)

                user.virtual_drive.add_remote(azure_storage)
                user.virtual_drive.mount_directory(dir_path)
                user.virtual_drive.upload_contents()

                return "Directory mounted successfully\n\r"

        def get_virtual_drive_contents(self, username):
                user = Authentication.user_database.get_user_from_db(username)
                if not user:
                        return "User not found\n\r"

                virtual_drive_contents = user.virtual_drive.to_dict()
                return f"{virtual_drive_contents}\n\r"

        def finish(self):
                socketserver.StreamRequestHandler.finish(self)
                self._logger.info("Client disconnected")


class ApiServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    This class implements the API server.
    """

    def __init__(self, host, port):
        self._logger = Logger()

        self.server_address = (host, port)
        socketserver.TCPServer.__init__(self, self.server_address, ApiRequestHandler)

        # Start a thread with the server -- that thread will start one
        # more thread for each request
        server_thread = threading.Thread(target=self.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        self._logger.info("API server listening on " + host + ", " + str(port))


if __name__ == '__main__':
        api_server = ApiServer('localhost', 9999)
        api_server.serve_forever()
