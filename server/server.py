import socket
import sys
import os
import tarfile


def server_program():
    # get the hostname
    host = socket.gethostname()
    host_ip = socket.gethostbyname(host)
    # print("Host name: " + str(host))
    # print("Host IP: " + str(host_ip))
    # host = 'localhost'
    if(len(sys.argv) != 2):
       print("Usage: python server.py <port_number>")
       sys.exit()
    port = int(sys.argv[1])

    print("Serial Server on host " + str(host_ip) + " is listening on port " + str(port) + "\n")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind(('', port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    print("Serial Server starting, listeneing on port " + str(port) + "\n")

    while True: # keep looping looking for new clients when previous closes
        conn, address = server_socket.accept()  # accept new connection
        print("Received connection request from " + str(address) + "\n")
        print("***********************************************************\n")
        while True:
            dir_contents = os.listdir(os.getcwd())
            folders = [d for d in dir_contents if os.path.isdir(os.path.join(os.getcwd(), d))]
            folders = '\n'.join(folders)
            if len(folders) == 0: folders = 'empty'
            conn.sendall(folders.encode())  # send folders to the client

            print("\tNow listening for incoming messages...\n")
            # receive data stream. it won't accept data packet greater than 1024 bytes
            message = conn.recv(1024).decode()
            if not message: break
            cmd = message[:message.index(" ")]
            folder = message[message.index(" ") + 1:]

            if cmd == 'access': # Access Folder
                while True:
                    path = os.path.join(os.getcwd(), folder)
                    dir_contents = os.listdir(path)
                    files = [d for d in dir_contents if os.path.isfile(os.path.join(path, d))]
                    files = '\n'.join(files)
                    if len(files) == 0: files = 'empty'
                    conn.sendall(files.encode())  # send files to the client

                    message = conn.recv(1024).decode()
                    if not message: break
                    if message == 'back': break # Go back to Folder View
                    cmd = message[:message.index(" ")]
                    file = message[message.index(" ") + 1:]

                    if cmd == 'access': # Access File
                        print('\tAccess has not been implemented.')
                    elif cmd == 'download': # Download File
                        file_path = os.path.join(path, file)
                        with open(file_path, "rb") as file:
                            while True:
                                data = file.read(1024)
                                if not data: break
                                conn.sendall(data)
                        print('\tFile was sent.')
                    elif cmd == 'upload': #Upload File
                        file_path = os.path.join(path, file)
                        with open(path, "wb") as file:
                            while True:
                                data = conn.recv(1024)
                                if not data: break
                                file.write(data)
                        print('\tFile was uploaded.')
                    elif cmd == 'delete': #Delete File: Done
                        file_path = os.path.join(path, file)
                        os.remove(path)
                        print('\tFile was deleted.')
                    else: print('\tPlease use commands: access, download, upload, and delete.')
            elif cmd == 'download': #Download Folder: Done
                with tarfile.open(mode="w|", fileobj=conn.makefile("wb")) as tar:
                    for root, dirs, files in os.walk(folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            tar.add(file_path)
                print('\tFolder was sent.')
            elif cmd == 'create': #Create Folder: Done
                path = os.path.join(os.getcwd(), folder)
                os.makedirs(path)
                print('\tFolder was created.')
            elif cmd == 'delete': # Delete Folder: Done
                path = os.path.join(os.getcwd(), folder)
                os.rmdir(path)
                print('\tFolder was deleted.')
            else: print('\tPlease use commands: access, download, create, and delete.')

        print("\tClient finished, now waiting to service another client...\n")
        print("***********************************************************\n")
        conn.close()  # close the connection


if __name__ == '__main__':
    server_program()