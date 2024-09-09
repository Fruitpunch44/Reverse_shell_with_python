import os
import socket
import sys
import threading
from tqdm import tqdm

# store list of connected clients
connected_clients = []


def handle_client(client_sock):
    if client_sock not in connected_clients:
        connected_clients.append(client_sock)
        print(f'new client connected {client_sock.getpeername()} \n')
    else:
        print(f'client {client_sock} is already connected ')

    while True:
        # my terminal kinda
        command = input("$eyi: ")
        if command == "exit":
            client_sock.send(b'closed')
            client_sock.close()
            print("waiting for another connection")

        # non windows/unix command exceptions
        elif command.startswith('download'):
            try:
                client_sock.send(command.encode())
                filename = command.split()[1]
                receive_files(client_sock, filename)
            except IndexError as e:
                print(f'no{e}')

        elif command.startswith('send'):
            try:
                client_sock.send(command.encode())
                filename = command.split()[1]
                send_files(client_sock, filename)
            except IndexError as e:
                print(f'no{e}')

        elif command.startswith('list'):
            print(f'Connected clients: {len(connected_clients)}')
            for i, client in enumerate(connected_clients, 1):
                print(f'client {i}: {client.getpeername()}')

        elif command.strip():
            try:
                client_sock.send(command.encode())
                # always set a high buffer size
                # if you want to receive a large amount of info
                response = client_sock.recv(4096).decode()
                print(response)
            except Exception as e:
                print(f'{e}')

            except IndexError as e:
                print(f'{e}')


def receive_files(sock, filename):
    # receive file size of the target file to be acquired
    file_size = int(sock.recv(4096).decode().strip())
    print(f' the size of the file to receive is {file_size} bytes')

    # set the progress bar with the total file size gotten
    progress = tqdm(total=file_size, desc=f'downloading {filename}',
                    unit='B',
                    unit_scale=False,
                    unit_divisor=1024
                    )
    try:
        with open(filename, 'wb') as file:
            total_received = 0
            while total_received < file_size:
                # recv  the file in chunks
                data = sock.recv(min(4096, file_size - total_received))
                # dubugging purposes
                # print(f'{total_received} bytes')
                if not data:
                    print("nothing to send again")
                    break
                file.write(data)
                total_received += len(data)
                progress.update((len(data)))
        progress.close()
    except FileNotFoundError as e:
        print(f'{e} not found')


def send_files(sock, filename):
    # get size of target file
    file_size = os.path.getsize(filename)
    sock.sendall(f'{file_size}'.encode())
    # set progress bar
    progress = tqdm(total=file_size, desc=f'sending {filename}',
                    unit='B',
                    unit_scale=False,
                    unit_divisor=1024)
    try:
        with open(filename, 'rb') as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                file_size_sent = 0
                while file_size_sent < file_size:
                    sock.sendall(data)
                    file_size_sent += len(data)
                    progress.update((len(data)))
            progress.close()
    except FileNotFoundError as e:
        print(f'not found {e}')
    except Exception as e:
        print(f'error sending {e}')


def server():
    # define connection parameters
    port = 8080
    target = "192.168.0.138"

    # set socket option
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((target, port))
        sock.listen()
        print(f'currently listening for connection from {port}:{target}')
        # accept incoming connections

        while True:
            client_sock, client_addr = sock.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_sock,))
            client_thread.start()
            print(f'accepted connection from {client_addr} \n')

    except Exception as e:
        print(f'an error occurred {e}')
        sys.exit(1)


if __name__ == '__main__':
    server()
