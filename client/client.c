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

#define MAXDATASIZE 100 //max number of bytes we can get at once

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
    char buf[MAXDATASIZE];
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

    printf("\tConnection established, now waiting for user input...\n\n");

    freeaddrinfo(servinfo);

    char* line = NULL;
    size_t size = 0;
    size_t len;

    while(readLine(&line, &size, &len)) {
        printf("\n");
        printf("\tSending message to Server...\n\n");

        if(send(sockfd, line, len, 0) == -1) {
            perror("send");
        }

        if(strcmp(line,";;;")==0) break;

        char buf2[1024];

        if((numbytes = recv(sockfd, buf2, 99, 0)) == -1) {
            perror("recv");
            exit(1);
        }

        buf2[numbytes] = '\0';

        printf("\tReceived response from server of\n\n");
        printf("\t\t\"%s\"\n\n", buf2);
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
        printf("\tprompt> ");
        size_t len = getline(line, size, stdin);

        if(len == -1)
            return false;

        if((*line)[len-1] == '\n')
            (*line)[--len] = '\0';

        *length = len;

        if(len == 0)
            continue;
        
        return len > 1;
    }
}