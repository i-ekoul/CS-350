#!/usr/bin/env python3
# -------------------------------------------------------------------
# CS-350 — Module 3 — Milestone Two
# SerialTest-Write: send an incrementing counter over USB-TTL
# -------------------------------------------------------------------

import time
import serial

DEV  = "/dev/ttyUSB0"
BAUD = 9600

def main():
    with serial.Serial(DEV, BAUD, timeout=1) as ser:
        n = 0
        print(f"Writing to {DEV} @ {BAUD}. Ctrl-C to stop.")
        while True:
            msg = f"{n}\n"
            ser.write(msg.encode("utf-8"))
            n += 1
            time.sleep(0.25)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
