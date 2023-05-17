import select
from time import sleep
from tkinter import *
import socket
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import threading
import tarfile
import sys
import shutil

root = Tk()
root.title("Shared Folder")
root.geometry("450x560+500+200")
root.configure(bg="#f4fdfe")
root.resizable(False,False)
global port
port = 9000

def receive_option():
    # Load and resize receive icons
    receive_img = Image.open("../assets/icons/receive.png")

    #Update bg color of icon - Composite the original image on top of the new image
    new_receive_image = Image.new("RGBA", receive_img.size, "#f4fdfe")
    new_receive_image.paste(receive_img, (0, 0), receive_img)

    new_receive_image = new_receive_image.resize((50, 50), Image.ANTIALIAS)
    new_receive_image = ImageTk.PhotoImage(new_receive_image)
    return new_receive_image


def delete_option():
    # Load and resize delete icons
    delete_img = Image.open("../assets/icons/delete.png")

    #Update bg color of icon - Composite the original image on top of the new image
    new_delete_image = Image.new("RGBA", delete_img.size, "#f4fdfe")
    new_delete_image.paste(delete_img, (0, 0), delete_img)

    new_delete_image = new_delete_image.resize((50, 50), Image.ANTIALIAS)
    new_delete_image = ImageTk.PhotoImage(new_delete_image)
    return new_delete_image
    #delete_btn.grid(row=0, column=2, sticky=tkinter.E)

def CreateFolder():
    #filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select directory to create folder")

    # Create a new window for folder name input
    input_window = tkinter.Toplevel(root)

    def create_new_folder():
        # Get the entered folder name
        folder_name = folder_name_entry.get()

        # Create the full path for the new folder
        new_folder_path = os.path.join(os.getcwd(), folder_name)

        # Create the new folder
        os.makedirs(new_folder_path)

        current_directory = os.getcwd()

        # Get all items (files and directories) in the current directory
        items = os.listdir(current_directory)

        # Filter out the directories from the list of items
        folders = [item for item in items if os.path.isdir(os.path.join(current_directory, item))]

        print(f"New folder created at: {new_folder_path}")

        #close previous folder window
        global window
        window.destroy()

        #Close the input window
        input_window.destroy()

        #Add new folder window
        Send()

    # Create a label and entry for folder name input
    folder_name_label = tkinter.Label(input_window, text="Enter folder name:")
    folder_name_label.pack()

    folder_name_entry = tkinter.Entry(input_window)
    folder_name_entry.pack()

    # Create a button to create the new folder
    create_button = tkinter.Button(input_window, text="Create Folder", command=create_new_folder)
    create_button.pack()
 

def upload_folder(window):
    bottom_frame = LabelFrame(window)
    bottom_frame.pack(side=tkinter.BOTTOM, expand=False, fill=BOTH)

    #button to add new folders
    create_folder_icon = Button(bottom_frame, text='Create folder',font='arial 14 bold',bg="#f4fdfe", command=CreateFolder)
    # create_folder_icon.pack(side=tkinter.BOTTOM)
    create_folder_icon.pack(side=tkinter.RIGHT, expand=False, fill="y")
   
    window.mainloop() 

def upload_files(window):
    bottom_frame = LabelFrame(window)
    bottom_frame.pack(side=tkinter.BOTTOM, expand=False, fill=BOTH)

    #button to add new folders
    create_folder_icon = Button(bottom_frame, text='Create file',font='arial 14 bold',bg="#f4fdfe", command=CreateFolder)
    # create_folder_icon.pack(side=tkinter.BOTTOM)
    create_folder_icon.pack(side=tkinter.RIGHT, expand=False, fill="y")
   
    window.mainloop() 

def display_files(folder_name):
    window = Toplevel(root)
    window.title("All files")
    window.geometry("450x560+500+200")
    window.configure(bg="#f4fdfe")
    window.resizable(False,False)

    top_frame = LabelFrame(window,background="#f4fdfe")
    top_frame.pack(side=tkinter.TOP, expand=False, fill=BOTH)

    header_title = Label(top_frame, text=folder_name, background="#f4fdfe", height=4, font=("Helvetica",35, "bold"),anchor=tkinter.W)
    #header_title.grid(row=0, column=0, columnspan=3)
    header_title.pack(side=tkinter.TOP, expand=True, fill=BOTH)

    #file labelframe
    file_frame = LabelFrame(top_frame,background="#f4fdfe")
    file_frame.pack(expand=False, fill=BOTH)

    message= "GET " + folder_name
    print("client send msg: " + message)
    client_socket.send(message.encode())  # send message, default encoding encoding="utf-8", errors="strict"
    
    sleep(1)
    
    files = client_socket.recv(1024).decode()  # receive files
    files = files.split('\n')
    
    print("files in folder:", files)

    if 'empty' in files:
        no_file = Label(file_frame, text="Current folder is empty", background="#f4fdfe", bd=0,  anchor=tkinter.W)
        no_file.pack()
        return
    
    receive_img = Image.open("../assets/icons/receive.png")

    #Update bg color of icon - Composite the original image on top of the new image
    new_receive_image = Image.new("RGBA", receive_img.size, "#f4fdfe")
    new_receive_image.paste(receive_img, (0, 0), receive_img)

    new_receive_image = new_receive_image.resize((50, 50), Image.ANTIALIAS)
    new_receive_image = ImageTk.PhotoImage(new_receive_image)

    delete_img = Image.open("../assets/icons/delete.png")

    #Update bg color of icon - Composite the original image on top of the new image
    new_delete_image = Image.new("RGBA", delete_img.size, "#f4fdfe")
    new_delete_image.paste(delete_img, (0, 0), delete_img)

    new_delete_image = new_delete_image.resize((50, 50), Image.ANTIALIAS)
    new_delete_image = ImageTk.PhotoImage(new_delete_image)

    #display all files on client
    for index,f in enumerate(files):
        indiv_file = Label(file_frame, text=f, background="#f4fdfe", cursor="arrow", anchor=tkinter.W)
        # TO ADD: click file to open
        indiv_file.grid(row=index, column=0, sticky="w")

        receive_btn = tkinter.Button(file_frame, image=new_receive_image, anchor=tkinter.E, command=Download)
        receive_btn.configure(borderwidth=0, highlightthickness=0, relief="flat")
        #receive_btn.pack(side=tkinter.RIGHT)
        receive_btn.grid(row=index, column=1)

        delete_btn = tkinter.Button(file_frame, image=new_delete_image, anchor=tkinter.E)
        delete_btn.configure(borderwidth=0, highlightthickness=0, relief="flat")
        #delete_btn.pack(side=tkinter.RIGHT)      
        delete_btn.grid(row=index, column=2)

        upload_files(window)

def folder_clicked(event):
    print("Folder clicked")
    folder_name = event.widget.cget("text")
    display_files(folder_name)

# def get_client_folders():
#     host = socket.gethostname()
#     print("Client has requested to start connection with host " + host + " on port " + str(port) + "\n")
#     print("server_adr: ", socket.gethostbyname("localhost"))

#     server_addr = (socket.gethostbyname(host), port)

#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
#     client_socket.connect(server_addr)  # connect to the server

#     print("client is connected to server")

#     folders = client_socket.recv(1024).decode()  # receive folders from server
#     folders = folders.split('\n')
#     print("folders: ", folders)
#     return folders

    #client_socket.close()  # close the connection

#Handle delete folder function
def Delete():
    print('\tFolder has been deleted.')

#Handle download folder function
def Download(content_dir):
    # with tarfile.open(mode="r|", fileobj=client_socket.makefile("rb")) as tar:
    #     tar.extractall()
    directory_path = filedialog.askdirectory()  # Open the file dialog to select a directory
    if directory_path:
        print("Selected directory:", directory_path)
        print("Original directory:", content_dir)
        # Check if the source is a file
        if os.path.isfile(content_dir):
            # Copy the file to the destination path
            shutil.copy(content_dir, directory_path)
            print("File downloaded successfully!")
        elif os.path.isdir(content_dir):
            # Copy the folder to the destination path
            shutil.rmtree(directory_path)
            shutil.copytree(content_dir, directory_path)
            print("Folder downloaded successfully!")
        else:
            print("Invalid source path!")
    else:
        print("No directory selected.")
    print('\tFolder has been downloaded.')

#Handle send function
def Send():
    message= "GET FOLDERS"
    client_socket.send(message.encode())  # send message, default encoding encoding="utf-8", errors="strict"

    sleep(1)

    folders = client_socket.recv(1024).decode()  # receive folders from server
    folders = folders.split('\n')

    print("folders: ", folders)
    print("Send folders: ", folders)
    global window 
    window = Toplevel(root)
    window.title("Send")
    window.geometry("450x560+500+200")
    window.configure(bg="#f4fdfe")
    window.resizable(False,False)

    #window.grid_rowconfigure(0, weight=1)
    #window.grid_columnconfigure(0, weight=1)

    top_frame = LabelFrame(window,background="#f4fdfe")
    top_frame.pack(side=tkinter.TOP, expand=False, fill=BOTH)

    #title
    header_title = Label(top_frame, text="Folders", background="#f4fdfe", height=4, font=("Helvetica",35, "bold"),anchor=tkinter.W)
    #header_title.grid(row=0, column=0, columnspan=3)
    header_title.pack(side=tkinter.TOP, expand=True, fill=BOTH)

    #file labelframe
    file_frame = LabelFrame(top_frame,background="#f4fdfe")
    file_frame.pack(expand=False, fill=BOTH)

        # Load and resize receive icons
    receive_img = Image.open("../assets/icons/receive.png")

    #Update bg color of icon - Composite the original image on top of the new image
    new_receive_image = Image.new("RGBA", receive_img.size, "#f4fdfe")
    new_receive_image.paste(receive_img, (0, 0), receive_img)

    new_receive_image = new_receive_image.resize((50, 50), Image.ANTIALIAS)
    new_receive_image = ImageTk.PhotoImage(new_receive_image)

    delete_img = Image.open("../assets/icons/delete.png")

    #Update bg color of icon - Composite the original image on top of the new image
    new_delete_image = Image.new("RGBA", delete_img.size, "#f4fdfe")
    new_delete_image.paste(delete_img, (0, 0), delete_img)

    new_delete_image = new_delete_image.resize((50, 50), Image.ANTIALIAS)
    new_delete_image = ImageTk.PhotoImage(new_delete_image)

    for index, f in enumerate(folders):
        folder = Label(file_frame, text=f, background="#f4fdfe", cursor="arrow", anchor=tkinter.W)
        # Bind the label to a click event
        folder.bind("<Button-1>", folder_clicked)
        #folder.pack() 
        folder.grid(row=index, column=0, sticky="w")

        #receive_delete_option(file_frame)
       #new_rcv_img = receive_option()
        receive_btn = tkinter.Button(file_frame, image=new_receive_image, anchor=tkinter.E, command=lambda: Download(f))
        receive_btn.configure(borderwidth=0, highlightthickness=0, relief="flat")
        #receive_btn.pack(side=tkinter.RIGHT)
        receive_btn.grid(row=index, column=1)

        #receive_btn.grid(row=0, column=1, sticky=tkinter.E)
        #new_del_img = delete_option()
        delete_btn = tkinter.Button(file_frame, image=new_delete_image, anchor=tkinter.E, command=Delete)
        delete_btn.configure(borderwidth=0, highlightthickness=0, relief="flat")
        #delete_btn.pack(side=tkinter.RIGHT)      
        delete_btn.grid(row=index, column=2)

    upload_folder(window)

    #display all folders
    # folder1 = Label(file_frame, text="Folder 1", background="#f4fdfe", cursor="arrow", anchor=tkinter.W)
    # # Bind the label to a click event
    # folder1.bind("<Button-1>", folder_clicked)
    # folder1.pack(side=tkinter.LEFT)

    #receive_delete_option(file_frame)
    # new_rcv_img = receive_option()
    # receive_btn = tkinter.Button(file_frame, image=new_rcv_img, anchor=tkinter.E)
    # receive_btn.configure(borderwidth=0, highlightthickness=0, relief="flat")
    # receive_btn.pack(side=tkinter.RIGHT)
    # #receive_btn.grid(row=0, column=1, sticky=tkinter.E)
    # new_del_img = delete_option()
    # receive_btn = tkinter.Button(file_frame, image=new_del_img, anchor=tkinter.E)
    # receive_btn.configure(borderwidth=0, highlightthickness=0, relief="flat")
    # receive_btn.pack(side=tkinter.RIGHT)


# def start_server():
#     #init server socket
#     host = socket.gethostname()
#     host_ip = socket.gethostbyname(host)

#     print("Serial Server on host " + str(host_ip) + " is listening on port " + str(port) + "\n")

#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
#     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     server_socket.bind(('', port)) 

#     # configure how many client the server can listen simultaneously
#     server_socket.listen(2)
#     print("Serial Server starting, listening on port " + str(port) + "\n")

#     while True: # keep looping looking for new clients when previous closes
#         conn, address = server_socket.accept()  # accept new connection
#         print("Received connection request from " + str(address) + "\n")
#         print("***********************************************************\n")
#         while True:
#             dir_contents = os.listdir(os.getcwd())
#             folders = [d for d in dir_contents if os.path.isdir(os.path.join(os.getcwd(), d))]
#             folders = '\n'.join(folders)
#             if len(folders) == 0: folders = 'empty'
#             conn.sendall(folders.encode())  # send folders to the client

#             print("\tNow listening for incoming messages...\n")


#main
#welcome page 
app_icon = PhotoImage(file="../assets/icons/app.png")
root.iconphoto(False, app_icon)
host = socket.gethostname()
Label(root, text=f'Welcome, {host}', font=("TkSmallCaptionFont", 18, "bold"), bg="#f4fdfe").place(x=20,y=30)

#send icon
send_image = Image.open("../assets/icons/send.png")

#Update bg color of icon - Composite the original image on top of the new image
new_send_img = Image.new("RGBA", send_image.size, "#f4fdfe")
new_send_img.paste(send_image, (0, 0), send_image)

resized_send = send_image.resize((100,100), Image.ANTIALIAS)

send_image =ImageTk.PhotoImage(resized_send)

send = Button(root, image=send_image,bd=0, bg="#f4fdfe", command= Send)
send.place(x=50, y=100)
Label(root, text="Folder", bg="#f4fdfe", font="bold").place(x=75, y=210)

# server_thread = threading.Thread(target=start_server)
# server_thread.start()

host = socket.gethostname()
print("Client has requested to start connection with host " + host + " on port " + str(port) + "\n")
print("server_adr: ", socket.gethostbyname("localhost"))

server_addr = (socket.gethostbyname(host), port)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
client_socket.connect(server_addr)  # connect to the server

print("client is connected to server")

# folders = client_socket.recv(1024).decode()  # receive folders from server
# folders = folders.split('\n')
# print("folders: ", folders)

root.mainloop()

#receive icon
#Resize send icon
# receive_image = Image.open("./assets/icons/receive.png")
# resized_receive = receive_image.resize((100,100), Image.ANTIALIAS)

# receive_image =ImageTk.PhotoImage(resized_receive)

# receive = Button(root, image=receive_image,bd=0, bg='#f4fdfe',command=Receive)
# receive.place(x=300, y=100)
# Label(root, text="Receive", bg="#f4fdfe", font="bold").place(x=320, y=210)




