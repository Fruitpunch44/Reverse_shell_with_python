# About #
This is a Python-based reverse application that allows file transfer (upload/download) between the server and connected clients as well as remote command executon
The server can handle multiple clients and execute system commands on the client machine although weird things happen if the clinets connected are differnt os . 


# Features #
1. File Transfer: Upload and download files between server and clients.
2. Command Execution: Execute commands on the client machine directly from the server.
3. Multiple Clients: Handle multiple clients simultaneously, each having their own session.
4. Progress Bar: Display file transfer progress using tqdm.
5. Client Management: Track and list connected clients with their IP addresses.

# How to run #
1. start the server to listen for conncetions:
   python reverse_shell_server.py
   
2. start the client script to connect to the server:
   python reverse_shell_client.py

