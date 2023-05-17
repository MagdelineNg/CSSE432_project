import socket
import sys
import os
import tarfile
import shutil


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
            if len(folders) == 0: folders = 'empty\n'
            conn.sendall(folders.encode())  # send folders to the client
            print('folders:',folders)

            print("\tNow listening for incoming messages...\n")
            # receive data stream. it won't accept data packet greater than 1024 bytes
            message = conn.recv(1024).decode()
            if not message: break
            cmd = message[:message.index(" ")]
            folder = message[message.index(" ") + 1:]

            if cmd == 'access': # Access Folder
                while True:
                    folder_path = os.path.join(os.getcwd(), folder)
                    dir_contents = os.listdir(folder_path)
                    files = [d for d in dir_contents if os.path.isfile(os.path.join(folder_path, d))]
                    files = '\n'.join(files)
                    if len(files) == 0: files = 'empty\n'
                    conn.sendall(files.encode())  # send files to the client
                    print('files:',files)

                    message = conn.recv(1024).decode()
                    if not message: break
                    if message == 'back': break # Go back to Folder View
                    cmd = message[:message.index(" ")]
                    file = message[message.index(" ") + 1:]

                    if cmd == 'access': # Access File
                        file_path = folder + '/' + file
                        with open(file_path, "rb") as f:
                            while True:
                                data = f.read(1024)
                                if not data: break
                                conn.sendall(data)
                                if len(data) < 1024: break
                        print('\tFile was sent.')
                        b = conn.recv(1024).decode()
                        if b == 'back': continue
                    elif cmd == 'download': # Download File
                        file_path = folder + '/' + file
                        with open(file_path, "rb") as f:
                            while True:
                                data = f.read(1024)
                                if not data: break
                                conn.sendall(data)
                                if len(data) < 1024: break
                        print('\tFile was sent.')
                        conn.recv(1024)
                    elif cmd == 'upload': #Upload File: Done
                        file_path = './' + folder + '/' + file
                        with open(file_path, "wb") as f:
                            while True:
                                data = conn.recv(1024)
                                if not data: break
                                f.write(data)
                                if len(data) < 1024: break
                        print('\tFile was uploaded.')
                    elif cmd == 'delete': #Delete File: Done
                        file_path = os.path.join(folder_path, file)
                        os.remove(file_path)
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
                folder_path = os.path.join(os.getcwd(), folder)
                os.makedirs(folder_path)
                print('\tFolder was created.')
            elif cmd == 'delete': # Delete Folder: Done
                folder_path = os.path.join(os.getcwd(), folder)
                shutil.rmtree(folder_path)
                print('\tFolder was deleted.')
            else: print('\tPlease use commands: access, download, create, and delete.')

        print("\tClient finished, now waiting to service another client...\n")
        print("***********************************************************\n")
        conn.close()  # close the connection


if __name__ == '__main__':
    server_program()