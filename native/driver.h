#ifndef DRIVER_H
#define DRIVER_H

int open_serial(const char *device, int baudrate);
int write_serial(int fd, const char *cmd);
int read_serial(int fd, char *buf, int max_len);
void close_serial(int fd);
void start_serial_terminal(const char *device, int baudrate);
int run_command_on_serial(int fd, const char *cmd, char *output, int outmax);

#endif
