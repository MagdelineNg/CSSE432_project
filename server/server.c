#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h> 
#include <sys/wait.h>
#include <errno.h>
#include <sys/socket.h> 
#include <netinet/in.h> 
#include <netdb.h> 
#include <arpa/inet.h> 
#include <ctype.h>
#include <dirent.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/sendfile.h>

#define BACKLOG 10 //how many pending connections queue will hold

void accessFolder(int new_fd, char* foldername);
void downloadFolder(int new_fd, char* foldername);

void sigchild_handler(int s) {
    (void)s; //quiet unused vriable warning

    //waitpid() might overwrite erno, so we save and restore it:
    int saved_errno = errno;

    while(waitpid(-1, NULL, WNOHANG) > 0);

    errno = saved_errno;
}

//get sockaddr, IPv4 or IPv6:
//localhost in IPv4=127.0.0.1, IPv6=::1
void *get_in_addr(struct sockaddr *sa) {
    if(sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

int main(int argc, char *argv[]) {
    int sockfd, new_fd, numbytes; //listen on sock_fd, new connection on new_fd
    struct addrinfo hints, *servinfo, *p;
    struct sockaddr_storage their_addr; //connector's address information
    socklen_t sin_size;
    struct sigaction sa;
    int yes = 1;
    char s[INET6_ADDRSTRLEN];
    int rv;

    if(argc != 2) {
        fprintf(stderr,"usage: server port\n");
        exit(1);
    }

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    if((rv = getaddrinfo(NULL, argv[1], &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 1;
    }

    //loop through all the results and bind to the first we can
    for(p = servinfo; p != NULL; p = p->ai_next) {
        if((sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == -1) {
            perror("server: socket");
            continue;
        }

        if(setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) == -1) {
            perror("setsockopt");
            exit(1);
        }

        if(bind(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            close(sockfd);
            perror("server: bind");
            continue;
        }

        break;
    }

    freeaddrinfo(servinfo); //all done with this structure

    if(p == NULL) {
        fprintf(stderr, "server: failed to bind\n");
        exit(1);
    }

    if(listen(sockfd, BACKLOG) == -1) {
        perror("listen");
        exit(1);
    }

    sa.sa_handler = sigchild_handler; //reap all dead processes
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    if(sigaction(SIGCHLD, &sa, NULL) == -1) {
        perror("sigaction");
        exit(1);
    }

    printf("Serial Server on host 0.0.0.0/0.0.0.0 is listening on port %s\n\n", argv[1]);
    printf("Serial Server starting, listeneing on port %s\n\n",argv[1]);

    while(1) { //main accept() loop
        sin_size = sizeof their_addr;
        new_fd = accept(sockfd, (struct sockaddr *)&their_addr, &sin_size);
        if(new_fd == -1) {
            perror("accept");
            continue;
        }

        inet_ntop(their_addr.ss_family, get_in_addr((struct sockdr *)&their_addr), s, sizeof s);
        printf("Received connection request from %s\n\n", s);
        printf("****************************************************\n\n");

        char buf[1024];
        int status;
        int pid = fork();
        
        if(!pid) { //this is the child process
            close(sockfd); //child doesn't need the listener

            // Step 2. The server sends the names of all the folders it has.
            char folder_names[1024] = "";
            struct dirent *de;
            DIR *dr = opendir(".");
            if (dr == NULL) {
                printf("Could not open current directory\n\n" );
                exit(1);
            }
            while ((de = readdir(dr)) != NULL) {
                if (de->d_type == DT_DIR && strcmp(de->d_name, ".") != 0 && strcmp(de->d_name, "..") != 0) {
                    strcat(folder_names, de->d_name);
                    strcat(folder_names, ",");
                }
            }
            closedir(dr);
            printf("Folders on the server: %s\n\n", folder_names);
            if(send(new_fd, folder_names, strlen(folder_names), 0) == -1) {
                perror("send");
            }

            printf("\tNow listening for incoming messages...\n\n");
            while(1) {
                // Step 3. The server receives/parses either of the following messages:
                //  “access foldername”, “download foldername”, “create foldername”, “delete foldername”
                if((numbytes = recv(new_fd, buf, 99, 0)) == -1) {
                    perror("recv");
                    exit(1);
                }
                buf[numbytes] = '\0';
                printf("\tReceived the following message from client:\n\n");
                printf("\t\t\"%s\"\n\n", buf);

                if(strlen(buf) == 0 || strcmp(buf, "exit") == 0) break;


                char cmd[15];
                char foldername[256];
                int j = 0;
                int atFolderName = 0;
                for(int i = 0; i < strlen(buf); i++) {
                    if(buf[i] == ' ') {
                        atFolderName = 1;
                        cmd[i] = '\0';
                    }
                    else if(atFolderName == 1) {
                        foldername[j] = buf[i];
                        j++;
                    }
                    else cmd[i] = buf[i];
                    
                }
                foldername[j] = '\0';

                printf("cmd: %s\n", cmd);
                printf("folder: %s\n", foldername);

                printf("\tNow sending parsed string back...\n\n");
                if(send(new_fd, cmd, strlen(cmd), 0) == -1) {
                    perror("send");
                }

                if(strcmp(cmd, "access") == 0) {
                    // Step 3a. The server continues to step 4. DONE
                    accessFolder(new_fd, foldername);
                }
                else if(strcmp(cmd, "download") == 0) {
                    // Step 3b. The server sends all files that are in the folder. DONE
                    downloadFolder(new_fd, foldername);
                }
                else if(strcmp(cmd, "create") == 0) {
                    // Step 3c. The server creates the folder. DONE
                    if (mkdir(foldername, 0777) != 0) {
                        printf("Error: could not create folder '%s'\n\n", foldername);
                    }
                    printf("Folder '%s' created successfully.\n\n", foldername);
                }
                else if(strcmp(cmd, "delete") == 0) {
                    // Step 3d. The server deletes the folder. DONE
                    if (rmdir(foldername) != 0) {
                        printf("Error: could not delete folder '%s'\n\n", foldername);
                    } else {
                        printf("Folder '%s' deleted successfully\n\n", foldername);
                    }
                } else {
                    printf("Please use commands: access, download, create, and delete.\n");
                }
            }
            printf("\tClient finished, now waiting to service another client...\n\n");
            printf("****************************************************\n\n");
            close(new_fd);
            exit(0);
        }
        close(new_fd); //parent doesn't need this
    }

    return 0;
}

void accessFolder(int new_fd, char* foldername) {
    //Step 4. The server sends the names of all the files in the folder.
    char file_names[1024] = "";
    struct dirent *de;
    DIR *dr = opendir(foldername);
    if (dr == NULL) {
        printf("Could not open current directory\n\n" );
        exit(1);
    }
    while ((de = readdir(dr)) != NULL) {
        if (de->d_type == DT_REG && strcmp(de->d_name, ".") != 0 && strcmp(de->d_name, "..") != 0) {
            strcat(file_names, de->d_name);
            strcat(file_names, ",");
        }
    }
    closedir(dr);
    printf("Files in %s: %s\n\n", foldername, file_names);
    if(send(new_fd, file_names, strlen(file_names), 0) == -1) {
        perror("send");
    }

    printf("\tNow listening for incoming messages...\n\n");
    char buf[1024];
    int numbytes;
    while(1) {
        // Step 5. The server receives/parses either of the following messages:
        //  “access filename”, “download filename”, "upload filename”, “delete filename”
        if((numbytes = recv(new_fd, buf, 99, 0)) == -1) {
            perror("recv");
            exit(1);
        }
        buf[numbytes] = '\0';
        printf("\tReceived the following message from client:\n\n");
        printf("\t\t\"%s\"\n\n", buf);

        if(strlen(buf) == 0 || strcmp(buf, "exit") == 0) break;


        char cmd[15];
        char filename[256];
        int j = 0;
        int atFileName = 0;
        for(int i = 0; i < strlen(buf); i++) {
            if(buf[i] == ' ') {
                atFileName = 1;
                cmd[i] = '\0';
            }
            else if(atFileName == 1) {
                filename[j] = buf[i];
                j++;
            }
            else cmd[i] = buf[i];
            
        }
        filename[j] = '\0';

        printf("cmd: %s\n", cmd);
        printf("file: %s\n", filename);

        char path[256] = "./";
        strcat(path, foldername);
        strcat(path, "/");
        strcat(path, filename);
        printf("path: %s\n", path);

        printf("\tNow sending parsed string back...\n\n");
        if(send(new_fd, cmd, strlen(cmd), 0) == -1) {
            perror("send");
        }

        if(strcmp(cmd, "access") == 0) {
            // Step 5a. The server sends the file. DONE
            FILE *fp = fopen(path, "rb");
            for (;;) {
                unsigned char download[1024]={0};
                int nread = fread(download,1,1024,fp);
                if(nread > 0) {
                    write(new_fd, download, nread);
                }
                if (nread < 1024) {
                    if (feof(fp))
                        printf("    file transfer of %d bytes to server complete and placed in %s\n", nread, foldername);
                    if (ferror(fp)) {
                        perror("read");
                    }
                    break;
                }
            }
            fclose(fp);
        }
        else if(strcmp(cmd, "download") == 0) {
            // Step 5b. The server sends the file. DONE
            FILE *fp = fopen(path, "rb");
            for (;;) {
                unsigned char download[1024]={0};
                int nread = fread(download,1,1024,fp);
                if(nread > 0) {
                    write(new_fd, download, nread);
                }
                if (nread < 1024) {
                    if (feof(fp))
                        printf("    file transfer of %d bytes to server complete and placed in %s\n", nread, foldername);
                    if (ferror(fp)) {
                        perror("read");
                    }
                    break;
                }
            }
            fclose(fp);
        }
        else if(strcmp(cmd, "upload") == 0) {
            // Step 5c. The server recieves and saves the file. DONE
            FILE *fp = fopen(path, "ab");
            if(fp == NULL) {
                perror("open file");
                exit(1);
            }
            int bytesReceived = 0;
            int totalBytes = 0;
            char upload[1024];
            memset(upload, '0', sizeof(upload));
            while((bytesReceived = read(new_fd, upload, 1024)) > 0) {
                fwrite(upload, 1, bytesReceived, fp);
                totalBytes += bytesReceived;
                if(bytesReceived < 1024) break;
            }
            printf("    file transfer of %d bytes complete and placed in %s\n",totalBytes, foldername);
            if(bytesReceived < 0) {
                perror("read");
                exit(1);
            }
            fclose(fp);
        }
        else if(strcmp(cmd, "delete") == 0) {
            // Step 5d. The server deletes the file. DONE
            if(remove(path) != 0) {
                printf("Error deleting file: '%s'\n\n", filename);
            } else {
                printf("File '%s' deleted successfully\n\n", filename);
            }
        } else if (strcmp(cmd, "back") == 0) {
            // Step 5e. The server return to step 2. DONE
            break;
        }
        else {
            printf("Please use commands: access, download, upload, and delete.\n");
        }
    }
    return;
}

void downloadFolder(int new_fd, char* foldername) {
    char file_names[1024] = "";
    struct dirent *de;
    DIR *dr = opendir(foldername);
    if (dr == NULL) {
        printf("Could not open current directory\n\n" );
        exit(1);
    }
    while ((de = readdir(dr)) != NULL) {
        if (de->d_type == DT_REG && strcmp(de->d_name, ".") != 0 && strcmp(de->d_name, "..") != 0) {
            char path[256] = "./";
            strcat(path, foldername);
            strcat(path, "/");
            strcat(path, de->d_name);
            printf("path: %s\n", path);
            FILE *fp = fopen(path, "rb");
            if(fp == NULL) {
                printf("File '%s' could not be found.\n", de->d_name);
                closedir(dr);
                fclose(fp);
            }
            printf("    file transfer started...\n");
            for (;;) {
                unsigned char buf[1024]={0};
                int nread = fread(buf,1,1024,fp);
                if(nread > 0) {
                    write(new_fd, buf, nread);
                }
                if (nread < 1024) {
                    if (feof(fp))
                        printf("    file transfer of %d bytes to server complete.\n", nread);
                    if (ferror(fp)) {
                        perror("read");
                    }
                    break;
                }
            }
            fclose(fp);
        }
    }
    closedir(dr);
    return;
}

