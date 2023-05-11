import socket
import sys
import tarfile


def client_program():
    if(len(sys.argv) != 3):
        print("Usage: python client.py <server_(IP)_address> <server_port_number>")
        sys.exit()
    port = int(sys.argv[2])
    server_ip = socket.gethostbyname(sys.argv[1])

    print("Client has requested to start connection with host" + str(server_ip) + " on port " + str(port) + "\n")

    server_addr = (server_ip, port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    client_socket.connect(server_addr)  # connect to the server

    while True:
        folders = client_socket.recv(1024).decode()  # receive folders
        folders = folders.split('\n')
        print('Folders on server: ' + ', '.join(folders))

        message = input(" -> ")  # take input
        if message.lower().strip() == ';;;': break
        client_socket.send(message.encode())  # send message, default encoding encoding="utf-8", errors="strict"
        message = message.lower().strip()
        cmd = message[:message.index(" ")]
        folder = message[message.index(" ") + 1:]
        
        if cmd == 'access': # Access Folder
            while True:
                files = client_socket.recv(1024).decode()  # receive files
                files = files.split('\n')
                print('Files in ' + folder + ': ' + ', '.join(files))

                message = input(" -> ")  # take input
                if message.lower().strip() == ';;;': break
                client_socket.send(message.encode())  # send message, default encoding encoding="utf-8", errors="strict"
                message = message.lower().strip()
                if message == 'back': break # Go back to Folder View
                cmd = message[:message.index(" ")]
                file = message[message.index(" ") + 1:]

                if cmd == 'access': # Access File
                    print('\tAccess has not been implemented.')
                elif cmd == 'download': # Download File
                    print('What directory would you like to save to?')
                    file_path = input(" -> ")
                    file_path = file_path.lower().strip()
                    file_path = file_path + file
                    with open(file_path, "wb") as f:
                        while True:
                            data = client_socket.recv(1024)
                            if not data: break
                            f.write(data)
                            if len(data) < 1024: break
                    print('\tFile has been downloaded.')
                    done = "done"
                    client_socket.send(done.encode())
                elif cmd == 'upload': # Upload File: Done
                    file_path = './' + file
                    try:
                        with open(file_path, "rb") as f:
                            while True:
                                data = f.read(1024)
                                if not data: break
                                client_socket.sendall(data)
                                if len(data) < 1024: break
                    except FileNotFoundError:
                        print('\tFile does not exist.')
                    print('\tFile has been uploaded.')
                elif cmd == 'delete': # Delete File: Done
                    print('\tFile has been deleted.')
                else: print('\tPlease use commands: access, download, upload, and delete.')
        elif cmd == 'download': # Download Folder: Done
            with tarfile.open(mode="r|", fileobj=client_socket.makefile("rb")) as tar:
                tar.extractall()
            print('\tFolder has been downloaded.')
        elif cmd == 'create': # Create Folder: Done
            print('\tFolder has been created.')
        elif cmd == 'delete': #Delete Folder: Done
            print('\tFolder has been deleted.')
        else: print('\tPlease use commands: access, download, create, and delete.')

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()