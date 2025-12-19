#!/usr/bin/env python3
# -------------------------------------------------------------------
# CS-350 — Module 3 — Milestone Two
# Serial Light Control — CLIENT (talks over USB-TTL)
#
# Type commands at the prompt: ON, OFF, EXIT/QUIT
# -------------------------------------------------------------------

import sys
import serial

DEV  = "/dev/ttyUSB0"   # USB-to-TTL adapter on the Pi
BAUD = 9600

def main():
    with serial.Serial(DEV, BAUD, timeout=1) as ser:
        print("Connected to", DEV, "@", BAUD)
        print("Type ON / OFF / EXIT and press Enter.")
        while True:
            try:
                line = input("> ").strip()
                if not line:
                    continue
                ser.write((line + "\n").encode("utf-8"))
                resp = ser.readline().decode("utf-8", errors="ignore").strip()
                if resp:
                    print("<", resp)
                if line.upper() in ("EXIT", "QUIT"):
                    break
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()
