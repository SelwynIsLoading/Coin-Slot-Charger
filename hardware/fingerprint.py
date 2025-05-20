import time

try:
    import adafruit_fingerprint
    import serial
    import busio
    import board
except ImportError:
    print("[FINGERPRINT] Running in simulation mode")

class FingerprintScanner:
    def __init__(self, uart_tx="TX", uart_rx="RX", baudrate=57600):
        """
        Initialize fingerprint scanner with UART connection
        Args:
            uart_tx: TX pin name (default "TX")
            uart_rx: RX pin name (default "RX")
            baudrate: UART baudrate (default 57600)
        """
        try:
            # Try to use board pins for UART
            tx_pin = getattr(board, uart_tx)
            rx_pin = getattr(board, uart_rx)
            uart = busio.UART(tx_pin, rx_pin, baudrate=baudrate)
            self.finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
            
            if not self.finger.read_templates():
                print("[FINGERPRINT] Failed to read templates")
            else:
                print(f"[FINGERPRINT] Found {self.finger.templates} fingerprint templates")
                
            print("[FINGERPRINT] Scanner initialized successfully")
            self._next_location = self.finger.templates + 1
            
        except Exception as e:
            print(f"[FINGERPRINT] Failed to initialize: {str(e)}")
            print("[FINGERPRINT] Running in simulation mode")
            self.finger = None
            self._next_location = 1

    def _get_fingerprint(self):
        """Get a fingerprint image and template it"""
        if self.finger is None:
            # Simulation mode - always succeed
            return True

        for _ in range(3):  # Try 3 times
            if self.finger.get_image() == adafruit_fingerprint.OK:
                if self.finger.image_2_tz(1) == adafruit_fingerprint.OK:
                    return True
            time.sleep(1)
        return False

    def enroll_fingerprint(self):
        """
        Enroll a new fingerprint
        Returns the ID of the enrolled fingerprint or None if failed
        """
        print("[FINGERPRINT] Place finger on sensor...")
        
        if self.finger is None:
            # Simulation mode
            print("[FINGERPRINT] Simulated enrollment successful")
            location = self._next_location
            self._next_location += 1
            return location

        if not self._get_fingerprint():
            return None

        print("[FINGERPRINT] Remove finger...")
        time.sleep(1)
        
        print("[FINGERPRINT] Place same finger again...")
        time.sleep(2)
        
        if not self._get_fingerprint():
            return None

        if self.finger.create_model() != adafruit_fingerprint.OK:
            return None

        location = self._next_location
        if self.finger.store_model(location) != adafruit_fingerprint.OK:
            return None

        self._next_location += 1
        return location

    def authenticate_fingerprint(self):
        """
        Try to match the current fingerprint against enrolled prints
        Returns the ID of the matching fingerprint or None if no match
        """
        print("[FINGERPRINT] Place finger to authenticate...")
        
        if self.finger is None:
            # Simulation mode - always succeed with ID 1
            print("[FINGERPRINT] Simulated authentication successful")
            return 1

        if not self._get_fingerprint():
            return None

        if self.finger.finger_search() != adafruit_fingerprint.OK:
            return None

        return self.finger.finger_id