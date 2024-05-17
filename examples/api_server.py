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
