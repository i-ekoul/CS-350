#!/usr/bin/env python3
import serial
ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
print("UART listener on /dev/ttyUSB0 @ 9600. Ctrl+C to quit.")
try:
    while True:
        line = ser.readline()
        if line:
            print(line.decode("utf-8", errors="ignore").rstrip())
except KeyboardInterrupt:
    pass
finally:
    ser.close()
