import argparse
import socket

def send_command(command):
        HOST, PORT = "localhost", 9999
        data = f"{command}\n"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((HOST, PORT))
                sock.sendall(data.encode('utf-8'))

                received = sock.recv(1024).decode('utf-8')
        
        print("Sent:     {}".format(data.strip()))
        print("Received: {}".format(received.strip()))

def main():
        parser = argparse.ArgumentParser(description='CCBox Command Line Interface')

        subparsers = parser.add_subparsers(dest='command')

        # Register command
        register_parser = subparsers.add_parser('register', help='Register a new user')
        register_parser.add_argument('--username', type=str, required=True, help='Username')
        register_parser.add_argument('--password', type=str, required=True, help='Password')

        # Login command
        login_parser = subparsers.add_parser('login', help='Login an existing user')
        login_parser.add_argument('--username', type=str, required=True, help='Username')
        login_parser.add_argument('--password', type=str, required=True, help='Password')
        
        # Mount command
        mount_parser = subparsers.add_parser('mount', help='Mount Directory')
        mount_parser.add_argument('--username', type=str, required=True, help='Username')
        mount_parser.add_argument('--dir', type=str, required=True, help='Directory to mount')
        
        content_parser = subparsers.add_parser('contents', help='View Contents of Current Directory')
        content_parser.add_argument('--username', type=str, required=True, help='Username')

        # Other commands
        subparsers.add_parser('quit', help='Close connection')
        subparsers.add_parser('exit', help='Exit program')
        subparsers.add_parser('version', help='Prints the version')
        subparsers.add_parser('about', help='Prints a short description')
        subparsers.add_parser('help', help='Shows all available commands')

        args = parser.parse_args()

        if args.command == 'register':
                command = f"register {args.username} {args.password}"
                send_command(command)
        elif args.command == 'login':
                command = f"login {args.username} {args.password}"
                send_command(command)
        elif args.command == "mount":
                command = f"login {args.dir}"
                send_command(command)
        elif args.command in ['quit', 'exit', 'version', 'about', 'help', 'contents']:
                send_command(args.command)
        else:
                parser.print_help()

if __name__ == '__main__':
        main()