# hardware/gpio_mock.py

BCM = "BCM"
IN = "IN"
PUD_UP = "PUD_UP"
LOW = 0
HIGH = 1
OUT = "OUT"

_pin_state = {}

def setmode(mode):
    print(f"[GPIO MOCK] Mode set to {mode}")

def setup(pin, mode, pull_up_down=None):
    print(f"[GPIO MOCK] Setup pin {pin} as {mode}, pull_up_down={pull_up_down}")
    _pin_state[pin] = HIGH

def input(pin):
    # Simulate coin insert on press
    # response = input(f"[GPIO MOCK] Press Enter to simulate coin insert on pin {pin}...")
    response = ""  # Simulate no input for testing
    return LOW if response == "" else HIGH

def output(pin, state):
    print(f"[GPIO MOCK] Output pin {pin} set to {'HIGH' if state == HIGH else 'LOW'}")
    _pin_state[pin] = state
