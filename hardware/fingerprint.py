import time
import serial
from pyfingerprint.pyfingerprint import PyFingerprint

class FingerprintScanner:
    def __init__(self, port='/dev/ttyAMA0', baudrate=57600):
        """
        Initialize fingerprint scanner with serial connection
        Args:
            port: Serial port (default '/dev/ttyAMA0' for Raspberry Pi)
            baudrate: Serial baudrate (default 57600)
        """
        try:
            # Enable UART on Raspberry Pi
            self.finger = PyFingerprint(port, baudrate)
            if not self.finger.verifyPassword():
                raise RuntimeError("[FINGERPRINT] Failed to verify password")
            
            print(f"[FINGERPRINT] Found {self.finger.getTemplateCount()} fingerprint templates")
            print("[FINGERPRINT] Scanner initialized successfully")
            self._next_location = self.finger.getTemplateCount() + 1
        except Exception as e:
            raise RuntimeError(f"[FINGERPRINT] Failed to initialize: {str(e)}")

    def _get_fingerprint(self):
        """Get a fingerprint image and template it"""
        for _ in range(3):  # Try 3 times
            try:
                if self.finger.readImage():
                    if self.finger.convertImage(0x01):
                        return True
            except Exception as e:
                print(f"[FINGERPRINT] Error reading fingerprint: {str(e)}")
            time.sleep(1)
        return False

    def enroll_fingerprint(self):
        """
        Enroll a new fingerprint
        Returns the ID of the enrolled fingerprint or None if failed
        """
        print("[FINGERPRINT] Place finger on sensor...")
        
        if not self._get_fingerprint():
            return None

        print("[FINGERPRINT] Remove finger...")
        time.sleep(1)
        
        print("[FINGERPRINT] Place same finger again...")
        time.sleep(2)
        
        if not self._get_fingerprint():
            return None

        try:
            if self.finger.createTemplate():
                location = self._next_location
                if self.finger.storeTemplate(location):
                    self._next_location += 1
                    return location
        except Exception as e:
            print(f"[FINGERPRINT] Error enrolling fingerprint: {str(e)}")
        
        return None

    def authenticate_fingerprint(self):
        """
        Try to match the current fingerprint against enrolled prints
        Returns the ID of the matching fingerprint or None if no match
        """
        print("[FINGERPRINT] Place finger to authenticate...")
        
        if not self._get_fingerprint():
            return None

        try:
            if self.finger.searchTemplate():
                return self.finger.getTemplateIndex()
        except Exception as e:
            print(f"[FINGERPRINT] Error authenticating fingerprint: {str(e)}")
        
        return None