#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <sys/socket.h> 
#include <sys/types.h> 
#include <netinet/in.h> 
#include <netdb.h> 
#include <arpa/inet.h>

bool readLine(char** line, size_t* size, size_t* length);

//get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa) {
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }
    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

int main(int argc, char *argv[]) {
    int sockfd, numbytes;
    struct addrinfo hints, *servinfo, *p;
    int rv;
    char s[INET6_ADDRSTRLEN];

    if(argc != 3) {
        fprintf(stderr,"usage: client hostname port\n");
        exit(1);
    }

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if((rv = getaddrinfo(argv[1], argv[2], &hints, &servinfo)) != 0) {
        printf(stderr, "getaddrinfo: %s/n", gai_strerror(rv));
        return 1;
    }

    for(p = servinfo; p != NULL; p = p->ai_next) {
        if((sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == 1) {
            perror("client: socket\n");
            close(sockfd);
            continue;
        }

        if(connect(sockfd, p->ai_addr, p->ai_addrlen) == 1) {
            perror("client: connect\n");
            close(sockfd);
            continue;
        }

        break;
    }

    inet_ntop(p->ai_family, get_in_addr((struct sockaddr *)p->ai_addr), s, sizeof s);
    printf("Client has requested to start connection with host %s on port %s\n\n", s, argv[2]);
    printf("****************************************************\n\n");

    if(p == NULL) {
        fprintf(stderr, "client: failed to connect\n");
        return 2;
    }

    // Step 1. The client connects to the server.
    printf("\tConnection established\n\n");

    freeaddrinfo(servinfo);

    char* line = NULL;
    size_t size = 0;
    size_t len;

    // Step 2. The client receives all the names of all the folders the server has.
    char folder_names[1024];
    if((numbytes = recv(sockfd, folder_names, 99, 0)) == -1) {
        perror("recv");
        exit(1);
    }
    folder_names[numbytes] = '\0';
    printf("\tFolders on the server:\n");
    char folder_name[1024];
    int j = 0;
    for(int i = 0; i < strlen(folder_names); i++) {
        if(folder_names[i] == ',') {
            printf("\t\t%s\n", folder_name);
            folder_name[0] = '\0';
            j = 0;
            i++;
        }
        folder_name[j] = folder_names[i];
        j++;
    }

    while(readLine(&line, &size, &len)) {
        printf("\n");

        // Step 3. The client sends the server either of the following messages:
        //  “access foldername”, “download foldername”, “create foldername”, “delete foldername”
        if(send(sockfd, line, len, 0) == -1) {
            perror("send");
        }

        //  recv parsed cmd
        char cmd[1024];
        if((numbytes = recv(sockfd, cmd, 99, 0)) == -1) {
            perror("recv");
            exit(1);
        }
        cmd[numbytes] = '\0';
        printf("\tReceived response from server of\n\n");
        printf("\t\t\"%s\"\n\n", cmd);

        if(strcmp(cmd, "access") == 0) {
            // Step 3a. 
        }
        if(strcmp(cmd, "download") == 0) {
            // Step 3b. 
        }
        if(strcmp(cmd, "create") == 0) {
            // Step 3c. 
        }
        if(strcmp(cmd, "delete") == 0) {
            // Step 3d. 
        }
    }

    printf("User entered sentinel of \";;;\", now stopping client\n\n");
    printf("****************************************************\n\n");

    printf("Attempting to shut down client sockets and other streams\n\n");

    close(sockfd);

    printf("Shut down successful... goodbye\n\n");

    return 0;
}

bool readLine(char** line, size_t* size, size_t* length) {
    while(1) {
        printf("\t> ");
        size_t len = getline(line, size, stdin);
        if(len == -1) return false;
        if((*line)[len-1] == '\n') (*line)[--len] = '\0';
        *length = len;
        if(len == 0) continue;
        return (strcmp(*line, "exit") != 0) && len > 0;
    }
}