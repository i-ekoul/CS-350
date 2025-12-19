#!/usr/bin/env python3
# -------------------------------------------------------------------
# CS-350 — Module 3 — Milestone Two
# Serial Light Control — SERVER (runs on the Pi UART)
#
# Original template intent (preserved):
#   - Configure /dev/ttyS0 and listen for ASCII commands:
#       "ON"  -> LED on (GPIO18 HIGH)
#       "OFF" -> LED off (GPIO18 LOW)
#       "EXIT"/"QUIT" -> acknowledge and terminate
#   - Use try/except for graceful shutdown
#   - Restore GPIO to a safe state on exit
# -------------------------------------------------------------------
# Wiring:
#   LED anode -> ~220 Ω resistor -> GPIO18 (BCM 18, physical pin 12)
#   LED cathode -> GND
#   USB-TTL: black->GND, white->Pi RXD0 (GPIO15/P15), green->Pi TXD0 (GPIO14/P14), red unused
# -------------------------------------------------------------------

import time
import serial
import RPi.GPIO as GPIO

LED_PIN = 18
SER_DEV = "/dev/ttyS0"   # Pi’s onboard UART
BAUD    = 9600

def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

def main():
    setup_gpio()
    ser = None
    try:
        ser = serial.Serial(SER_DEV, BAUD, timeout=1)
        time.sleep(0.1)  # settle

        while True:
            raw = ser.readline()
            if not raw:
                continue
            cmd = raw.decode("utf-8", errors="ignore").strip().upper()

            if cmd == "ON":
                GPIO.output(LED_PIN, GPIO.HIGH)
                ser.write(b"ACK ON\n")
            elif cmd == "OFF":
                GPIO.output(LED_PIN, GPIO.LOW)
                ser.write(b"ACK OFF\n")
            elif cmd in ("EXIT", "QUIT"):
                ser.write(b"BYE\n")
                break
            else:
                ser.write(b"ERR\n")

    except KeyboardInterrupt:
        pass
    finally:
        try:
            if ser and ser.is_open:
                ser.flush()
                ser.close()
        except Exception:
            pass
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.cleanup()

if __name__ == "__main__":
    main()
