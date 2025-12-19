#!/usr/bin/env python3
# -------------------------------------------------------------------
# CS-350 — Module 3 — Milestone Two
# SerialTest-Read: read lines from Pi UART (/dev/ttyS0)
# -------------------------------------------------------------------

import serial

DEV  = "/dev/ttyS0"
BAUD = 9600

def main():
    with serial.Serial(DEV, BAUD, timeout=1) as ser:
        print(f"Reading from {DEV} @ {BAUD}. Ctrl-C to stop.")
        while True:
            raw = ser.readline()
            if raw:
                line = raw.decode("utf-8", errors="ignore").rstrip("\r\n")
                print(line)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
