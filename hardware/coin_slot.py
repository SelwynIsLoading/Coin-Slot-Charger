# hardware/coin_slot.py

import RPi.GPIO as GPIO
import time

class CoinSlot:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def wait_for_coin(self):
        print("[COIN SLOT] Waiting for coin insert...")
        while True:
            if GPIO.input(self.pin) == GPIO.LOW:
                value = self.get_coin_value()
                return value
            time.sleep(0.1)

    def get_coin_value(self):
        # TODO: Implement actual coin value detection based on hardware
        raise NotImplementedError("Coin value detection not implemented")
