
#include <unistd.h>

int main(void) {
    // copy stdin to stdout with read & write syscalls
    while (1) {
        char bytes[4096];

        // system call number 0 == read
        // read system call takes 3 arguments:
        //   1) file descriptor, 1 == stdin
        //   2) memory address to put bytes read
        //   3) maximum number of bytes read
        // returns number of bytes actually read

        long bytes_read = syscall(0, 0, bytes, 4096);

        if (bytes_read <= 0) {
            break;
        }

        syscall(1, 1, bytes, bytes_read); // prints bytes to stdout
    }

    return 0;
}