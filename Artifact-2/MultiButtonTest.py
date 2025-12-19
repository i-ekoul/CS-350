#!/usr/bin/env python3
from gpiozero import Button
from signal import pause

btn_mode = Button(24, pull_up=True, bounce_time=0.05)
btn_up   = Button(16, pull_up=True, bounce_time=0.05)
btn_down = Button(12, pull_up=True, bounce_time=0.05)

btn_mode.when_pressed = lambda: print("MODE pressed")
btn_up.when_pressed   = lambda: print("UP pressed")
btn_down.when_pressed = lambda: print("DOWN pressed")

btn_mode.when_released = lambda: print("MODE released")
btn_up.when_released   = lambda: print("UP released")
btn_down.when_released = lambda: print("DOWN released")

print("Press buttons (Ctrl+C to exit)...")
pause()
