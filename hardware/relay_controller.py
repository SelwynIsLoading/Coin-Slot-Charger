# hardware/relay_controller.py

import RPi.GPIO as GPIO
import time

class RelayController:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)  # OFF by default

    def turn_on(self):
        print(f"[RELAY] Slot ON (pin {self.pin})")
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self):
        print(f"[RELAY] Slot OFF (pin {self.pin})")
        GPIO.output(self.pin, GPIO.LOW)
