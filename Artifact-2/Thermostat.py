#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CS-350 Final Project — Smart Thermostat (AHT20 + LCD + LEDs + Buttons + UART)

WIRING (BCM numbering)
  AHT20         : I2C (board.SCL/board.SDA), 3.3 V power
  LCD 16x2 (4b) : RS=26, E=19, D4=13, D5=6, D6=5, D7=11   (VSS->GND, VDD->+5V, RW->GND, Vo via pot)
  RED LED (HEAT): GPIO 18 (PWM) with current-limiting resistor
  BLUE LED(COOL): GPIO 23 (PWM) with current-limiting resistor
  Buttons       : GREEN=24 (MODE), BLUE=16 (SP down), RED=12 (SP up) — to GND; internal pull-ups

BEHAVIOR (per rubric)
  - Default set point = 72.0 °F
  - AHT20 temp => read in °C, convert to °F for all logic & display
  - If HEAT and temp < setpoint -> red LED fades; else red solid (>= setpoint)
  - If COOL and temp > setpoint -> blue LED fades; else blue solid (<= setpoint)
  - Buttons: GREEN cycles OFF→HEAT→COOL; BLUE lowers SP by 0.5 °F; RED raises SP by 0.5 °F
  - LCD: line 1 = date/time (always); line 2 alternates every 2 s between:
      (a) current temperature; (b) "<state> SP:<setpoint>"
  - UART (9600 8N1): emit CSV every 30 s: state,current_f,setpoint_f
    * Auto-detect /dev/serial0, /dev/ttyAMA0, /dev/ttyS0; mirror CSV always.
"""

import os, glob, time, signal
import RPi.GPIO as GPIO
from gpiozero import PWMLED, Button
import board, busio
import adafruit_ahtx0
import serial

# ----------------- LCD 16x2 minimal driver (4-bit, HD44780) -----------------
LCD_RS, LCD_E = 26, 19
LCD_D4, LCD_D5, LCD_D6, LCD_D7 = 13, 6, 5, 11

class LCD1602:
    LCD_CLR   = 0x01
    LCD_HOME  = 0x02
    LCD_ENTRY = 0x06
    LCD_ON    = 0x0C
    LCD_FUNC  = 0x28
    LCD_LINE1 = 0x80
    LCD_LINE2 = 0xC0

    def __init__(self, rs, e, d4, d5, d6, d7):
        self.rs, self.e = rs, e
        self.d4, self.d5, self.d6, self.d7 = d4, d5, d6, d7
        for p in (rs, e, d4, d5, d6, d7):
            GPIO.setup(p, GPIO.OUT)
            GPIO.output(p, False)
        self._init()

    def _pulse(self):
        GPIO.output(self.e, False); time.sleep(1e-6)
        GPIO.output(self.e, True);  time.sleep(1e-6)
        GPIO.output(self.e, False); time.sleep(5e-5)

    def _nibble(self, x):
        GPIO.output(self.d4, bool(x & 0x01))
        GPIO.output(self.d5, bool(x & 0x02))
        GPIO.output(self.d6, bool(x & 0x04))
        GPIO.output(self.d7, bool(x & 0x08))
        self._pulse()

    def _byte(self, b, is_data=False):
        GPIO.output(self.rs, is_data)
        self._nibble((b >> 4) & 0x0F)
        self._nibble(b & 0x0F)

    def _cmd(self, c): self._byte(c, False)

    def _init(self):
        time.sleep(0.05)
        GPIO.output(self.rs, False)
        for _ in range(3):
            self._nibble(0x03); time.sleep(0.005)
        self._nibble(0x02)
        self._cmd(self.LCD_FUNC)
        self._cmd(self.LCD_ON)
        self.clear()
        self._cmd(self.LCD_ENTRY)

    def clear(self):
        self._cmd(self.LCD_CLR); time.sleep(0.002)

    def set_cursor(self, col, row):
        self._cmd((self.LCD_LINE1 if row == 0 else self.LCD_LINE2) + col)

    def write(self, s):
        for ch in s[:16]:
            self._byte(ord(ch), True)

    def print_lines(self, l1="", l2=""):
        self.set_cursor(0, 0); self.write(l1.ljust(16)[:16])
        self.set_cursor(0, 1); self.write(l2.ljust(16)[:16])

# --------------------------- Helpers & constants -----------------------------
# Buttons (BCM) — matches your wiring + semantics
BTN_MODE = 24   # GREEN: cycle OFF→HEAT→COOL
BTN_BLUE = 16   # BLUE : COOL action => LOWER setpoint
BTN_RED  = 12   # RED  : HEAT action => RAISE setpoint

# LEDs (PWM)
PIN_RED, PIN_BLUE = 18, 23

# Timing
LCD_ALT_PERIOD = 2.0      # seconds between alternated line-2 views
UART_PERIOD    = 30.0     # seconds between UART/CSV records

# Setpoint defaults & steps (Fahrenheit)
DEFAULT_SP_F = 72.0
STEP_F       = 0.5

def c_to_f(c): return (c * 9.0 / 5.0) + 32.0

def find_uart_port():
    """Detect a usable built-in UART; return its path or None."""
    for cand in ("/dev/serial0", "/dev/ttyAMA0", "/dev/ttyS0"):
        if os.path.exists(cand):
            return cand
    for pat in ("/dev/ttyAMA*", "/dev/ttyS*"):
        for dev in sorted(glob.glob(pat)):
            if os.path.exists(dev):
                return dev
    return None

# --------------------------------- App --------------------------------------
class Thermostat:
    def __init__(self):
        # Basic GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # LCD
        self.lcd = LCD1602(LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7)

        # I2C + sensor
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.aht = adafruit_ahtx0.AHTx0(self.i2c)  # AHT20 @ 0x38

        # LEDs
        self.red  = PWMLED(PIN_RED, frequency=200)   # heat
        self.blue = PWMLED(PIN_BLUE, frequency=200)  # cool

        # Buttons (pull-up; pressed -> GND)
        self.btn_mode = Button(BTN_MODE, pull_up=True, bounce_time=0.08)
        self.btn_blue = Button(BTN_BLUE, pull_up=True, bounce_time=0.08)  # cool => SP down
        self.btn_red  = Button(BTN_RED,  pull_up=True, bounce_time=0.08)  # heat => SP up
        self.btn_mode.when_pressed = self._cycle_mode
        self.btn_blue.when_pressed = self._sp_down
        self.btn_red.when_pressed  = self._sp_up

        # State machine
        self.state = "off"    # "off" | "heat" | "cool"
        self.setpoint_f = DEFAULT_SP_F
        self.current_f  = None

        # Track current LED modes to avoid restarting pulse each loop
        self._red_mode  = "off"   # "off" | "solid" | "pulse"
        self._blue_mode = "off"

        # UART (auto-detect)
        self.uart = None
        self.uart_port = find_uart_port()
        if self.uart_port:
            try:
                self.uart = serial.Serial(self.uart_port, 9600, timeout=1)
                print(f"[UART] Using {self.uart_port} @ 9600 8N1")
            except Exception as e:
                print(f"[WARN] UART open failed on {self.uart_port}: {e}")
                self.uart = None
        else:
            print("[WARN] No UART device found (serial0/ttyAMA0/ttyS0). CSV mirror only.")

        # CSV mirror (always)
        self.csv_path = "/var/tmp/thermostat_uart.csv"
        try:
            if not os.path.exists(self.csv_path):
                with open(self.csv_path, "w") as f:
                    f.write("timestamp,state,current_f,setpoint_f\n")
        except Exception as e:
            print(f"[WARN] Could not create CSV at {self.csv_path}: {e}")

        # Timers/flags
        self._running   = True
        self._last_uart = 0.0
        self._last_alt  = 0.0
        self._show_temp = True  # toggles second line

        # Signals
        signal.signal(signal.SIGINT,  self._sigexit)
        signal.signal(signal.SIGTERM, self._sigexit)

    # ---- button handlers ----
    def _cycle_mode(self):
        self.state = {"off": "heat", "heat": "cool", "cool": "off"}[self.state]

    def _sp_up(self):
        self.setpoint_f = round(self.setpoint_f + STEP_F, 1)

    def _sp_down(self):
        self.setpoint_f = round(self.setpoint_f - STEP_F, 1)

    # ---- graceful exit ----
    def _sigexit(self, *_):
        self._running = False

    # ---- internal: change LED mode only when it actually changes ----
    def _set_red_mode(self, mode):
        if mode == self._red_mode:
            return
        # stop any previous behavior
        self.red.off()
        if mode == "solid":
            self.red.value = 1.0
        elif mode == "pulse":
            self.red.pulse(fade_in_time=0.7, fade_out_time=0.7, n=None, background=True)
        # "off" already handled by .off()
        self._red_mode = mode

    def _set_blue_mode(self, mode):
        if mode == self._blue_mode:
            return
        self.blue.off()
        if mode == "solid":
            self.blue.value = 1.0
        elif mode == "pulse":
            self.blue.pulse(fade_in_time=0.7, fade_out_time=0.7, n=None, background=True)
        self._blue_mode = mode

    # ---- LED policy per rubric (no restarting of pulse) ----
    def _apply_leds(self):
        if self.state == "heat":
            # red active, blue off
            self._set_blue_mode("off")
            if self.current_f is not None and self.current_f < self.setpoint_f:
                self._set_red_mode("pulse")   # needs heating
            else:
                self._set_red_mode("solid")   # at/above setpoint
        elif self.state == "cool":
            # blue active, red off
            self._set_red_mode("off")
            if self.current_f is not None and self.current_f > self.setpoint_f:
                self._set_blue_mode("pulse")  # needs cooling
            else:
                self._set_blue_mode("solid")  # at/below setpoint
        else:  # off
            self._set_red_mode("off")
            self._set_blue_mode("off")

    # ---- UART + CSV every 30 seconds ----
    def _emit_uart(self):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        cur = f"{self.current_f:.2f}" if self.current_f is not None else "nan"
        line = f"{self.state},{cur},{self.setpoint_f:.2f}\n"

        if self.uart:
            try:
                self.uart.write(line.encode("utf-8"))
                self.uart.flush()
            except Exception:
                pass

        try:
            with open(self.csv_path, "a") as f:
                f.write(f"{ts},{self.state},{cur},{self.setpoint_f:.2f}\n")
        except Exception:
            pass

    # ---- main loop ----
    def run(self):
        self.lcd.print_lines(time.strftime("%b %d %H:%M"), "Thermostat ready")
        time.sleep(0.8)

        while self._running:
            # Read sensor
            try:
                t_c = self.aht.temperature
                self.current_f = c_to_f(t_c)
            except Exception:
                time.sleep(0.2)
                continue

            # LEDs per state (with mode caching for smooth fade)
            self._apply_leds()

            # LCD update
            now = time.time()
            self.lcd.print_lines(
                time.strftime("%b %d %H:%M"),
                (f"{self.current_f:5.1f} F"
                 if self._show_temp
                 else f"{self.state:>4} SP:{self.setpoint_f:5.1f}")
            )
            if now - self._last_alt >= LCD_ALT_PERIOD:
                self._show_temp = not self._show_temp
                self._last_alt = now

            # UART/CSV periodic
            if now - self._last_uart >= UART_PERIOD:
                self._emit_uart()
                self._last_uart = now

            time.sleep(0.1)

        # shutdown visual
        self._set_red_mode("off")
        self._set_blue_mode("off")
        self.lcd.clear()
        self.lcd.print_lines("Thermostat", "Stopped.")
        time.sleep(0.6)

    def close(self):
        try:
            self.btn_mode.close(); self.btn_blue.close(); self.btn_red.close()
            if self.uart:
                try: self.uart.close()
                except Exception: pass
        except Exception:
            pass
        GPIO.cleanup()

# --------------------------------- main --------------------------------------
def main():
    t = Thermostat()
    try:
        t.run()
    finally:
        t.close()

if __name__ == "__main__":
    main()
