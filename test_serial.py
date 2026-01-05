import ruserial

device = "/dev/ttyUSB0"
baud_rate = 115200
 
ruserial.start_serial(device, baud_rate) 

# try:
#     ruserial.start_serial(device, baud_rate)    

# except ValueError as e:
#     print(f"Input error: {e}")

# except RuntimeError as e:
#     print(f"Driver error: {e}")

# except KeyboardInterrupt as e:
#     print(f"Keyboard Interrupt")
