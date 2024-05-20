import socket
import argparse

def send_command(command, host='localhost', port=9999):
    try:
        # Create a socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        # Send the command to the server
        client_socket.sendall(command.encode('utf-8') + b'\n')
        
        # Receive the response from the server
        response = client_socket.recv(4096).decode('utf-8')
        print("Response from server:", response)
        
    finally:
        client_socket.close()

def main():
    parser = argparse.ArgumentParser(description="CLI for interacting with the virtual drive server")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Register command
    register_parser = subparsers.add_parser('register', help='Register a new user')
    register_parser.add_argument('username', type=str, help='Username for the new user')
    register_parser.add_argument('password', type=str, help='Password for the new user')

    # Login command
    login_parser = subparsers.add_parser('login', help='Log in a user')
    login_parser.add_argument('username', type=str, help='Username of the user')
    login_parser.add_argument('password', type=str, help='Password of the user')

    # Mount command
    mount_parser = subparsers.add_parser('mount', help='Mount a directory to the virtual drive')
    mount_parser.add_argument('username', type=str, help='Username of the user')
    mount_parser.add_argument('dir', type=str, help='Path of the directory to mount')

    # Contents command
    contents_parser = subparsers.add_parser('contents', help='Get the contents of the virtual drive')
    contents_parser.add_argument('username', type=str, help='Username of the user')

    args = parser.parse_args()

    if args.command == 'register':
        send_command(f"register {args.username} {args.password}")
    elif args.command == 'login':
        send_command(f"login {args.username} {args.password}")
    elif args.command == 'mount':
        send_command(f"mount {args.username} {args.dir}")
    elif args.command == 'contents':
        send_command(f"contents {args.username}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()