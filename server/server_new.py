import socket
import sys
import os
import tarfile

port = 9000

#init server socket
host = socket.gethostname()
host_ip = socket.gethostbyname(host)

print("Serial Server on host " + str(host_ip) + " is listening on port " + str(port) + "\n")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', port)) 

# configure how many client the server can listen simultaneously
server_socket.listen(2)
print("Serial Server starting, listening on port " + str(port) + "\n")

while True: # keep looping looking for new clients when previous closes
    conn, address = server_socket.accept()  # accept new connection
    print("Received connection request from " + str(address) + "\n")
    print("***********************************************************\n")
    while True:
        #send all folders to client to display
        dir_contents = os.listdir(os.getcwd())
        folders = [d for d in dir_contents if os.path.isdir(os.path.join(os.getcwd(), d))]
        folders = '\n'.join(folders)
        if len(folders) == 0: folders = 'empty'
        conn.sendall(folders.encode())  # send folders to the client

        print("\tNow listening for incoming messages...\n")

        message = conn.recv(1024).decode()
        if not message: break
        cmd = message[:message.index(" ")]
        folder = message[message.index(" ") + 1:]

        print("folder gotten: " + folder)
        print("CMD: " + cmd)
        
        if cmd == "GET": 
            #send files in folder to client to display
            folder_path = os.path.join(os.getcwd(), folder)
            dir_contents = os.listdir(folder_path)
            files = [d for d in dir_contents if os.path.isfile(os.path.join(folder_path, d))]
            files = '\n'.join(files)
            if len(files) == 0: files = 'empty'
            conn.sendall(files.encode())  # send files to the client
