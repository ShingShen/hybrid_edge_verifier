#include "driver.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <errno.h>
#include <sys/select.h> 

static struct termios old_stdin_tty;
static int stdin_configured = 0;

static int get_baud_speed(int baud, speed_t *speed) {
    switch (baud) {
        case 9600: *speed = B9600; break;
        case 19200: *speed = B19200; break;
        case 38400: *speed = B38400; break;
        case 57600: *speed = B57600; break;
        case 115200: *speed = B115200; break;
        default: return -1; 
    }
    return 0;
}

static int set_serial_raw(int fd, speed_t speed) {
    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) return -1;

    cfmakeraw(&tty);
    cfsetspeed(&tty, speed);
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~CRTSCTS;

    if (tcsetattr(fd, TCSANOW, &tty) != 0) return -1;
    return 0;
}

// Set STDIN Raw Mode, and backup old setting
static int set_stdin_raw() {
    if (tcgetattr(STDIN_FILENO, &old_stdin_tty) != 0) return -1;
    
    struct termios tty = old_stdin_tty;
    tty.c_lflag &= ~(ICANON | ECHO);
    // Set VMIN = 1 to ensure the CPU does not go to 100% usage.
    tty.c_cc[VMIN] = 1; 
    tty.c_cc[VTIME] = 0;

    if (tcsetattr(STDIN_FILENO, TCSANOW, &tty) != 0) return -1;
    
    stdin_configured = 1;
    return 0;
}

static void restore_stdin() {
    if (stdin_configured) {
        tcsetattr(STDIN_FILENO, TCSANOW, &old_stdin_tty);
        stdin_configured = 0;
    }
}

int start_serial_terminal(const char *device, int baudrate) {
    int serial_fd = -1;
    speed_t speed;
    int ret_code = 0;

    // Check baud rate
    if (get_baud_speed(baudrate, &speed) != 0) {
        fprintf(stderr, "C Error: Unsupported baud rate %d\n", baudrate);
        return -1;
    }

    // Start Serial Port
    serial_fd = open(device, O_RDWR | O_NOCTTY);
    if (serial_fd < 0) {
        perror("C Error: open serial");
        return -2;
    }

    // Set Serial attributes
    if (set_serial_raw(serial_fd, speed) != 0) {
        perror("C Error: set_serial_raw");
        ret_code = -3;
        goto cleanup;
    }

    // Set STDIN as Raw Mode
    if (set_stdin_raw() != 0) {
        perror("C Error: set_stdin_raw");
        ret_code = -4;
        goto cleanup;
    }

    printf("Connected to %s at %d baud. (C Module)\n", device, baudrate);
    fflush(stdout);

    while (1) {
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(serial_fd, &readfds);
        FD_SET(STDIN_FILENO, &readfds);

        int max_fd = (serial_fd > STDIN_FILENO) ? serial_fd : STDIN_FILENO;

        int ret = select(max_fd + 1, &readfds, NULL, NULL, NULL);
        if (ret < 0) {
            if (errno == EINTR) continue; // rery if the signal is interrupted.
            perror("C Error: select");
            ret_code = -5;
            break;
        }

        // Read Serial -> Write STDOUT
        if (FD_ISSET(serial_fd, &readfds)) {
            char buf[256];
            // Fix: prestore space for '\0'，to prevent from overflow
            int len = read(serial_fd, buf, sizeof(buf) - 1);
            if (len > 0) {
                buf[len] = '\0'; // Although 'write' is not nessassary，it is a good habit.
                if (write(STDOUT_FILENO, buf, len) < 0) { /* handle error if needed */ }
            } else {
                // Serial device may be unplugged
                fprintf(stderr, "\nSerial device disconnected.\n");
                break; 
            }
        }

        // Read STDIN -> Write Serial
        if (FD_ISSET(STDIN_FILENO, &readfds)) {
            char ch;
            int len = read(STDIN_FILENO, &ch, 1);
            if (len > 0) {
                // if (ch == 1) break; 
                
                if (ch == '\n') ch = '\r';
                if (write(serial_fd, &ch, 1) < 0) { /* handle error */ }
            }
        }
    }

// cleanup tags: Handle resource cleanup in a unified manner
cleanup:
    restore_stdin();     // reset terminal
    if (serial_fd >= 0) {
        close(serial_fd); // close serial
    }
    
    return ret_code; // return Rust
}