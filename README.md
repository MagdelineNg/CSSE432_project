CSSE432_project: Shared Folder

This is a shared folder application where the server holds multiple folders that have 
multiple files of various types.

When the server is running, the client can open the application by running the command:
    python gui.py server_ip port

Once the client has the application running, they can 'Connect' to the server and then
they will be able to 'Disconnect' or 'List Folders' in the server. If the client disconnects
they will have the option to 'Connect' again or close the application. If the client decided
to 'List Folders' then the application will open a new window that has all the different
folders that are in the server. The client will have the option to:
    1. 'access' the folder by clicking on the button with the folder name. This will
        bring the client to a new page that displays all the files in the folder requested.
        (continued below...)
    2. 'delete' a folder by clicking on the delete button next to the folder name. 
        The folder will not longer be present after hitting submit.
    3. 'download' a folder by clicking on the download button next to the folder name.
        a. using the relative path: ./folder
        b. using the absolute path: /path/parent/folder
    4. 'create' a folder by hitting the create folder button and then putting a folder name
        in the pop up box presented. The new folder will be present after hitting submit.
    5. 'upload' a folder by hitting the upload folder button and either:
        a. using the relative path: ./folder
        b. using the absolute path: /path/parent/folder
        The new folder will be present after hitting submit.
    6. 'disconnect' from the server. This will bring you back to the first page where
        the client can recconect.

If the client is now viewing the files in a specific folder they will have the option to:
    1. 'access' the file by clicking on the button with the file name on it. This will 
        bring the client to a new page displaying what is inside the file.
    2. 'delete' a file by clicking on the download button next to the file name.
        The file will not longer be present after hitting submit.
    3. 'download' a file by clicking on the download button next to the file name.
        a. using the relative path: ./folder
        b. using the absolute path: /path/parent/folder
    4. 'upload' a file by hitting the upload file button and either:
        a. using the relative path: ./folder/file.ext
        b. using the absolute path: /path/parent/folder/file.ext
        The new file will be present after hitting submit.
    5. 'back' brings the client back to the folder view of the server.

If the client is currently viewing the inside of a specific file, they also have the
option to 'Go Back' at any time and this will bring them back to the file view of
the folder they previously were on.
