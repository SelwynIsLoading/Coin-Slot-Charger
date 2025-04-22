# hardware/fingerprint.py

from pyfingerprint.pyfingerprint import PyFingerprint
import time


class FingerprintScanner:
    def __init__(self, port='/dev/ttyUSB0', baudrate=57600):
        try:
            self.f = PyFingerprint(port, baudrate, 0xFFFFFFFF, 0x00000000)
            if not self.f.verifyPassword():
                raise ValueError('The given fingerprint sensor password is wrong!')
            print('[FINGERPRINT] Initialized successfully.')
        except Exception as e:
            print(f'[FINGERPRINT] Failed to initialize sensor: {e}')
            raise e

    def enroll_fingerprint(self):
        print('[FINGERPRINT] Waiting for finger...')
        while not self.f.readImage():
            pass

        self.f.convertImage(0x01)
        result = self.f.searchTemplate()
        positionNumber = result[0]

        if positionNumber >= 0:
            print(f'[FINGERPRINT] Finger already enrolled at position #{positionNumber}')
            return positionNumber

        print('[FINGERPRINT] Remove finger...')
        time.sleep(2)

        print('[FINGERPRINT] Place same finger again...')
        while not self.f.readImage():
            pass

        self.f.convertImage(0x02)
        if self.f.compareCharacteristics() == 0:
            raise Exception('[FINGERPRINT] Fingerprints do not match')

        self.f.createTemplate()
        positionNumber = self.f.storeTemplate()
        print(f'[FINGERPRINT] Finger enrolled at position #{positionNumber}')
        return positionNumber

    def authenticate_fingerprint(self):
        print('[FINGERPRINT] Waiting for fingerprint authentication...')
        while not self.f.readImage():
            pass

        self.f.convertImage(0x01)
        result = self.f.searchTemplate()
        positionNumber = result[0]

        if positionNumber == -1:
            print('[FINGERPRINT] No match found.')
            return None
        else:
            print(f'[FINGERPRINT] Match found at position #{positionNumber}')
            return positionNumber
