import tkinter as tk
import socket
import threading
import os
import sys
import tarfile

# Shared folder path
SHARED_FOLDER = 'shared_folder'

class FileShareApp(tk.Tk):
    def __init__(self, server_ip, port):
        super().__init__()
        self.server_ip = server_ip
        self.port = port
        self.geometry("500x300+300+200")
        self.title("Client Window")
        self.lbl_status = tk.Label(self, text="Client: Not connected")
        self.lbl_status.pack(pady=5)
        self.btn_connect = tk.Button(self, text="Connect", command=self.connect_to_server)
        self.btn_connect.pack(pady=10)
        self.btn_disconnect = tk.Button(self, text="Disconnect", command=self.disconnect_from_server, state=tk.DISABLED)
        self.btn_disconnect.pack(pady=5)
        self.btn_list_folders = tk.Button(self, text="List Folders", command=self.list_folders, state=tk.DISABLED)
        self.btn_list_folders.pack(pady=5)

    def connect_to_server(self):
        server_addr = (self.server_ip, self.port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(server_addr)
        self.lbl_status.config(text="Client: Connected")
        self.btn_connect.config(state=tk.DISABLED)
        self.btn_disconnect.config(state=tk.NORMAL)
        self.btn_list_folders.config(state=tk.NORMAL)

    def disconnect_from_server(self):
        self.client_socket.close()
        self.lbl_status.config(text="Client: Not connected")
        self.btn_connect.config(state=tk.NORMAL)
        self.btn_disconnect.config(state=tk.DISABLED)
        self.btn_list_folders.config(state=tk.DISABLED)

    def list_folders(self):
        self.btn_list_folders.config(state=tk.DISABLED)
        self.destroy()
        folder_view = FolderView(self.client_socket)
        folder_view.grid()

class FolderView(tk.Tk):
    def __init__(self, client_socket: socket.socket):
        super().__init__()
        self.geometry("500x300+300+200")
        self.title("Client Window")
        self.client_socket = client_socket
        folders = self.client_socket.recv(1024).decode()  # receive folders
        folders = folders.split('\n')
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        for index, f in enumerate(folders):
            if f == 'empty':
                self.empty = tk.Label(self, text="folder is empty")
                self.empty.pack(pady=5)
                break
            else:
                tk.Button(button_frame, text=f, command=lambda folder=f: self.list_files(folder)).grid(row=index, column=0, pady=5)
                tk.Button(button_frame, text='delete', command=lambda folder=f: self.delete_folder(folder)).grid(row=index, column=1, pady=5)
                tk.Button(button_frame, text='download', command=lambda folder=f: self.download_folder_popup(folder)).grid(row=index, column=2, pady=5)
        self.btn_create_folder = tk.Button(self, text="Create Folder", command=self.create_folder_popup)
        self.btn_create_folder.pack(pady=5)
        self.btn_upload_folder = tk.Button(self, text="Upload Folder", command=self.upload_folder_popup)
        self.btn_upload_folder.pack(pady=5)
        self.btn_back = tk.Button(self, text='Disconnect', command=self.back)
        self.btn_back.pack(pady=5)

    def back(self):
        self.destroy()
        self.client_socket.close()
        view = FileShareApp(server_ip, port)
        view.mainloop()

    def create_folder_popup(self):
        popup = tk.Toplevel()
        popup.geometry("160x75+475+300")
        popup.title("Input")
        entry_label = tk.Label(popup, text="Folder name:")
        entry_label.pack()
        entry = tk.Entry(popup)
        entry.pack()
        self.submit_button = tk.Button(popup, text="Submit", command=lambda: self.create_folder(entry.get(), popup))
        self.submit_button.pack()

    def download_folder_popup(self, folder_name):
        popup = tk.Toplevel()
        popup.geometry("160x75+475+300")
        popup.title("Input")
        entry_label = tk.Label(popup, text="Download location:")
        entry_label.pack()
        entry = tk.Entry(popup)
        entry.pack()
        self.submit_button = tk.Button(popup, text="Submit", command=lambda: self.download_folder(entry.get(), popup, folder_name))
        self.submit_button.pack()

    def upload_folder_popup(self):
        popup = tk.Toplevel()
        popup.geometry("160x75+475+300")
        popup.title("Input")
        entry_label = tk.Label(popup, text="Upload location:")
        entry_label.pack()
        entry = tk.Entry(popup)
        entry.pack()
        self.submit_button = tk.Button(popup, text="Submit", command=lambda: self.upload_folder(entry.get(), popup))
        self.submit_button.pack()

    def create_folder(self, folder_name, popup: tk.Toplevel):
        print("User input:", folder_name)
        popup.destroy()
        message  = "create " + folder_name
        self.client_socket.send(message.encode()) 
        self.destroy()
        self.__init__(self.client_socket)

    def list_files(self, folder_name):
        message  = "access " + folder_name
        self.client_socket.send(message.encode())
        self.destroy()
        file_view = FileView(self.client_socket, folder_name)
        file_view.grid()

    def delete_folder(self, folder_name):
        message  = "delete " + folder_name
        self.client_socket.send(message.encode())
        self.destroy()
        self.__init__(self.client_socket)
        
    def download_folder(self, download_loc, popup: tk.Toplevel, folder_name):
        print("User input:", download_loc)
        popup.destroy()
        message  = "download " + folder_name
        self.client_socket.send(message.encode())
        # download stuff- works with input './' as current directory
        with tarfile.open(mode="r|", fileobj=self.client_socket.makefile("rb")) as tar:
            tar.extractall()

    def upload_folder(self, upload_loc, popup: tk.Toplevel):
        print("User input:", upload_loc)
        popup.destroy()
        message  = "upload " + upload_loc
        self.client_socket.send(message.encode())
        # do upload folder stuff
        # with tarfile.open(mode="w|", fileobj=self.client_socket.makefile("wb")) as tar:
        #     for root, dirs, files in os.walk(upload_loc):
        #         for file in files:
        #             file_path = os.path.join(root, file)
        #             tar.add(file_path)
        files = [os.path.join(root, file) for root, dirs, files in os.walk(upload_loc) for file in files]
        with tarfile.open(mode="w|", fileobj=self.client_socket.makefile("wb")) as tar:
            if files:
                last_file = files[-1]
                parent_dir = os.path.dirname(last_file)
                tar.add(parent_dir, arcname=os.path.basename(parent_dir))
        print('\tFolder was sent.')
        self.destroy()
        self.__init__(self.client_socket)

class FileView(tk.Tk):
    def __init__(self, client_socket: socket.socket, folder_name):
        super().__init__()
        self.geometry("500x300+300+200")
        self.title("Client Window")
        self.client_socket = client_socket
        self.folder_name = folder_name
        tk.Label(self, text=folder_name).pack(pady=5)
        files = self.client_socket.recv(1024).decode()  # receive files
        files = files.split('\n')
        self.buttons = [] 
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        for index, f in enumerate(files):
            if f == 'empty':
                self.empty = tk.Label(self, text="folder is empty")
                self.empty.pack(pady=5)
                break
            else:
                tk.Button(button_frame, text=f, command=lambda file=f: self.access_file(file)).grid(row=index, column=0, pady=5)
                tk.Button(button_frame, text='delete', command=lambda file=f: self.delete_file(file)).grid(row=index, column=1, pady=5)
                tk.Button(button_frame, text='download', command=lambda file=f: self.btn_download_file_popup(file)).grid(row=index, column=2, pady=5)
        self.btn_upload_file = tk.Button(self, text="Upload File", command=self.btn_upload_file_popup)
        self.btn_upload_file.pack(pady=5)
        self.btn_back = tk.Button(self, text='Go Back', command=self.back)
        self.btn_back.pack(pady=5)

    def back(self):
        message  = 'back'
        self.client_socket.send(message.encode()) 
        self.destroy()
        folder_view = FolderView(self.client_socket)
        folder_view.mainloop()

    def btn_upload_file_popup(self):
        popup = tk.Toplevel()
        popup.geometry("160x75+475+300")
        popup.title("Input")
        entry_label = tk.Label(popup, text="Upload location:")
        entry_label.pack()
        entry = tk.Entry(popup)
        entry.pack()
        self.submit_button = tk.Button(popup, text="Submit", command=lambda: self.upload_file(entry.get(), popup))
        self.submit_button.pack()

    def upload_file(self, file_loc, popup: tk.Toplevel):
        print("User input:", file_loc)
        popup.destroy()
        message  = "upload " + file_loc
        self.client_socket.send(message.encode()) 
        # works with realtive path: ./folder1/file.txt
        try:
            with open(file_loc, "rb") as f:
                while True:
                    data = f.read(1024)
                    if not data: break
                    self.client_socket.sendall(data)
                    if len(data) < 1024: break
        except FileNotFoundError:
            print('\tFile does not exist.')
        self.destroy()
        self.__init__(self.client_socket, self.folder_name)

    def access_file(self, file_name):
        message  = "access " + file_name
        self.client_socket.send(message.encode()) 
        self.destroy()
        file_view = SingleFileView(self.client_socket, file_name)
        file_view.grid()

    def delete_file(self, file_name):
        message  = "delete " + file_name
        self.client_socket.send(message.encode()) 
        self.destroy()
        self.__init__(self.client_socket, self.folder_name)

    def btn_download_file_popup(self, file_name):
        popup = tk.Toplevel()
        popup.geometry("160x75+475+300")
        popup.title("Input")
        entry_label = tk.Label(popup, text="Download location:")
        entry_label.pack()
        entry = tk.Entry(popup)
        entry.pack()
        self.submit_button = tk.Button(popup, text="Submit", command=lambda: self.download_file(entry.get(), popup, file_name))
        self.submit_button.pack()

    def download_file(self, download_loc, popup: tk.Toplevel, file_name):
        print("User input:", download_loc)
        popup.destroy()
        message  = "download " + file_name
        self.client_socket.send(message.encode()) 
        # works with input './folder' as input to folder1
        download_loc = download_loc + '/' + file_name
        with open(download_loc, "wb") as f:
            while True:
                data = self.client_socket.recv(1024)
                if not data: break
                f.write(data)
                if len(data) < 1024: break
        print('\tFile has been downloaded.')
        done = "done"
        self.client_socket.send(done.encode())

class SingleFileView(tk.Tk):
    def __init__(self, client_socket: socket.socket, file_name):
        super().__init__()
        self.geometry("500x300+300+200")
        self.title("Client Window")
        tk.Label(self, text=file_name).pack(pady=5)
        self.file_name = file_name
        self.client_socket = client_socket
        self.btn_back = tk.Button(self, text="Go Back", command=self.back)
        self.btn_back.pack(pady=5)
        text_widget = tk.Text(self)
        text_widget.pack()
        while True:
            data = client_socket.recv(1024)
            if not data: break
            text_widget.insert(tk.END, data)
            if len(data) < 1024: break

    def back(self):
        message  = 'back'
        self.client_socket.send(message.encode()) 
        self.destroy()
        file_view = FileView(self.client_socket, self.file_name)
        file_view.mainloop()

if __name__ == '__main__':
    if(len(sys.argv) != 3):
        print("Usage: python gui.py <server_(IP)_address> <server_port_number>")
        sys.exit()
    port = int(sys.argv[2])
    server_ip = socket.gethostbyname(sys.argv[1])
    app = FileShareApp(server_ip, port)
    app.mainloop()