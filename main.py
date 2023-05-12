from tkinter import *
import socket
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
import os

root = Tk()
root.title("Shared Folder")
root.geometry("450x560+500+200")
root.configure(bg="#f4fdfe")
root.resizable(False,False)
global port
port = 9000

def receive_option():
    # Load and resize receive icons
    receive_img = Image.open("./assets/icons/receive.png")

    #Update bg color of icon - Composite the original image on top of the new image
    new_receive_image = Image.new("RGBA", receive_img.size, "#f4fdfe")
    new_receive_image.paste(receive_img, (0, 0), receive_img)

    new_receive_image = new_receive_image.resize((50, 50), Image.ANTIALIAS)
    new_receive_image = ImageTk.PhotoImage(new_receive_image)
    return new_receive_image


def delete_option():
    # Load and resize delete icons
    delete_img = Image.open("./assets/icons/delete.png")

    #Update bg color of icon - Composite the original image on top of the new image
    new_delete_image = Image.new("RGBA", delete_img.size, "#f4fdfe")
    new_delete_image.paste(delete_img, (0, 0), delete_img)

    new_delete_image = new_delete_image.resize((50, 50), Image.ANTIALIAS)
    new_delete_image = ImageTk.PhotoImage(new_delete_image)
    return new_delete_image
    #delete_btn.grid(row=0, column=2, sticky=tkinter.E)

def upload_option(window, text):
    bottom_frame = LabelFrame(window)
    bottom_frame.pack(side=tkinter.BOTTOM, expand=False, fill=BOTH)

    #button to add new folders
    create_folder_icon = Button(bottom_frame, text=text,font='arial 14 bold',bg="#f4fdfe")
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

    #display all folders
    file1 = Label(file_frame, text="file.txt", background="#f4fdfe", cursor="arrow", anchor=tkinter.W)
    # Bind the label to a click event
    file1.bind("<Button-1>", folder_clicked)
    file1.pack(side=tkinter.LEFT)

    #receive_delete_option(file_frame)
    new_rcv_img = receive_option()
    receive_btn = tkinter.Button(file_frame, image=new_rcv_img, anchor=tkinter.E)
    receive_btn.configure(borderwidth=0, highlightthickness=0, relief="flat")
    receive_btn.pack(side=tkinter.RIGHT)
    #receive_btn.grid(row=0, column=1, sticky=tkinter.E)
    new_del_img = delete_option()
    receive_btn = tkinter.Button(file_frame, image=new_del_img, anchor=tkinter.E)
    receive_btn.configure(borderwidth=0, highlightthickness=0, relief="flat")
    receive_btn.pack(side=tkinter.RIGHT)

    upload_option(window, "Upload file")

def folder_clicked(event):
    print("Folder clicked")
    folder_name = event.widget.cget("text")
    display_files(folder_name)

def get_client_folders():
    host = socket.gethostname()
    print("Client has requested to start connection with host " + host + " on port " + str(port) + "\n")
    print("server_adr: ", socket.gethostbyname("localhost"))

    server_addr = (socket.gethostbyname(host), port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    client_socket.connect(server_addr)  # connect to the server

    print("client is connected to server")

    while True: 
        folders = client_socket.recv(1024).decode()  # receive folders from server
        folders = folders.split('\n')
        print('get_client_folders: Folders found: ' + ', '.join(folders))

    client_socket.close()  # close the connection

#Handle send function
def Send():
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

    get_client_folders()

    #display all folders
    folder1 = Label(file_frame, text="Folder 1", background="#f4fdfe", cursor="arrow", anchor=tkinter.W)
    # Bind the label to a click event
    folder1.bind("<Button-1>", folder_clicked)
    folder1.pack(side=tkinter.LEFT)

    #receive_delete_option(file_frame)
    new_rcv_img = receive_option()
    receive_btn = tkinter.Button(file_frame, image=new_rcv_img, anchor=tkinter.E)
    receive_btn.configure(borderwidth=0, highlightthickness=0, relief="flat")
    receive_btn.pack(side=tkinter.RIGHT)
    #receive_btn.grid(row=0, column=1, sticky=tkinter.E)
    new_del_img = delete_option()
    receive_btn = tkinter.Button(file_frame, image=new_del_img, anchor=tkinter.E)
    receive_btn.configure(borderwidth=0, highlightthickness=0, relief="flat")
    receive_btn.pack(side=tkinter.RIGHT)

    upload_option(window, "Create folder")

#main
#welcome page 
app_icon = PhotoImage(file="./assets/icons/app.png")
root.iconphoto(False, app_icon)
host = socket.gethostname()
Label(root, text=f'Welcome, {host}', font=("TkSmallCaptionFont", 18, "bold"), bg="#f4fdfe").place(x=20,y=30)

#send icon
send_image = Image.open("./assets/icons/send.png")

#Update bg color of icon - Composite the original image on top of the new image
new_send_img = Image.new("RGBA", send_image.size, "#f4fdfe")
new_send_img.paste(send_image, (0, 0), send_image)

resized_send = send_image.resize((100,100), Image.ANTIALIAS)

send_image =ImageTk.PhotoImage(resized_send)

send = Button(root, image=send_image,bd=0, bg="#f4fdfe", command=Send)
send.place(x=50, y=100)
Label(root, text="Folder", bg="#f4fdfe", font="bold").place(x=75, y=210)

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
    root.mainloop()
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

#receive icon
#Resize send icon
# receive_image = Image.open("./assets/icons/receive.png")
# resized_receive = receive_image.resize((100,100), Image.ANTIALIAS)

# receive_image =ImageTk.PhotoImage(resized_receive)

# receive = Button(root, image=receive_image,bd=0, bg='#f4fdfe',command=Receive)
# receive.place(x=300, y=100)
# Label(root, text="Receive", bg="#f4fdfe", font="bold").place(x=320, y=210)




