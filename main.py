# # main.py

# import tkinter as tk
# import threading
# import time

# from gui.touchscreen_ui import ChargingStationUI
# from hardware.coin_slot import CoinSlot
# from hardware.relay_controller import RelayController
# from config import COIN_SLOT_PIN, RELAY_PINS, COIN_TIME_MAP

# def handle_session(slot_number):
#     ui.update_status(f"Slot {slot_number} selected. Insert coin...")
#     ui.disable_slot_button(slot_number)

#     def session_thread():
#         try:
#             coin_slot = CoinSlot(COIN_SLOT_PIN)
#             coin_value = coin_slot.wait_for_coin()

#             minutes = COIN_TIME_MAP.get(coin_value, 0)
#             if minutes == 0:
#                 ui.update_status("Invalid coin inserted.")
#                 ui.reset_slot_button(slot_number)
#                 return

#             total_seconds = minutes * 60
#             ui.update_status(f"{coin_value} pesos accepted. Charging for {minutes} minutes...")

#             relay_pin = RELAY_PINS.get(slot_number)
#             relay = RelayController(relay_pin)
#             relay.turn_on()

#             for remaining in range(total_seconds, 0, -1):
#                 mins, secs = divmod(remaining, 60)
#                 ui.update_slot_timer(slot_number, mins, secs)
#                 time.sleep(1)

#             relay.turn_off()
#             ui.update_status(f"Charging complete for Slot {slot_number}.")
#         finally:
#             ui.reset_slot_button(slot_number)

#     threading.Thread(target=session_thread).start()

# if __name__ == "__main__":
#     root = tk.Tk()
#     ui = ChargingStationUI(root, handle_session)
#     root.mainloop()


# main.py

import tkinter as tk
import threading
import time

from gui.touchscreen_ui import ChargingStationUI
from hardware.coin_slot import CoinSlot
from hardware.relay_controller import RelayController
from hardware.fingerprint import FingerprintScanner
from config import COIN_SLOT_PIN, RELAY_PINS, COIN_TIME_MAP

fingerprint = FingerprintScanner()
cancel_flags = {}

def handle_session(slot_number):
    ui.update_status(f"Slot {slot_number} selected. Insert coin...")
    ui.disable_slot_button(slot_number)

    cancel_flags[slot_number] = threading.Event()

    def session_thread():
        try:
            coin_slot = CoinSlot(COIN_SLOT_PIN)
            coin_value = coin_slot.wait_for_coin()
            if cancel_flags[slot_number].is_set():
                ui.update_status("Session cancelled.")
                return

            minutes = COIN_TIME_MAP.get(coin_value, 0)
            if minutes == 0:
                ui.update_status("Invalid coin inserted.")
                return

            ui.update_status("Please scan your fingerprint to register...")
            ui.show_cancel_button()
            fingerprint_id = fingerprint.enroll_fingerprint()
            if cancel_flags[slot_number].is_set():
                ui.update_status("Session cancelled.")
                return

            ui.update_status(f"Fingerprint saved. Charging will begin in {minutes} minutes...")
            total_seconds = minutes * 60

            for remaining in range(total_seconds, 0, -1):
                if cancel_flags[slot_number].is_set():
                    ui.update_status("Session cancelled.")
                    return
                mins, secs = divmod(remaining, 60)
                ui.update_slot_timer(slot_number, mins, secs)
                time.sleep(1)

            ui.update_status("Please scan your fingerprint to unlock the charging slot...")
            match_id = None
            while match_id != fingerprint_id:
                if cancel_flags[slot_number].is_set():
                    ui.update_status("Session cancelled.")
                    return
                match_id = fingerprint.authenticate_fingerprint()
                if match_id != fingerprint_id:
                    ui.update_status("Fingerprint mismatch. Try again.")

            relay_pin = RELAY_PINS.get(slot_number)
            relay = RelayController(relay_pin)
            relay.turn_on()
            ui.update_status("Access granted. Charging started!")

            time.sleep(10)  # Simulated charge time
            relay.turn_off()
            ui.update_status(f"Charging complete for Slot {slot_number}.")

        finally:
            ui.reset_slot_button(slot_number)
            cancel_flags.pop(slot_number, None)

    threading.Thread(target=session_thread).start()

def handle_cancel(slot_number):
    if slot_number in cancel_flags:
        cancel_flags[slot_number].set()

if __name__ == "__main__":
    root = tk.Tk()
    ui = ChargingStationUI(root, handle_session, handle_cancel)
    root.mainloop()
