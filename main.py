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
slot_timers = {}  # slot_number: remaining_seconds
slot_fingerprints = {}  # slot_number: fingerprint_id
slot_threads = {}  # slot_number: thread

def handle_session(slot_number):
    # If session is running, add time
    if slot_number in slot_timers and slot_timers[slot_number] > 0:
        ui.update_status(f"Slot {slot_number}: Insert coin to add time...")
        coin_slot = CoinSlot(COIN_SLOT_PIN)
        coin_value = coin_slot.wait_for_coin()
        minutes = COIN_TIME_MAP.get(coin_value, 0)
        if minutes == 0:
            ui.update_status("Invalid coin inserted.")
            return
        ui.update_status("Please scan your fingerprint to add time...")
        fingerprint_id = slot_fingerprints.get(slot_number)
        if fingerprint_id is None:
            ui.update_status("No fingerprint registered for this slot.")
            return
        match_id = fingerprint.authenticate_fingerprint()
        if match_id != fingerprint_id:
            ui.update_status("Fingerprint mismatch. Time not added.")
            return
        slot_timers[slot_number] += minutes * 60
        ui.update_status(f"Time added! {minutes} minutes. New total: {slot_timers[slot_number]//60} min {slot_timers[slot_number]%60} sec.")
        return

    # New session
    ui.update_status(f"Slot {slot_number} selected. Insert coin...")
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
            if fingerprint_id is None:
                ui.update_status("Fingerprint enrollment failed. Please try again.")
                return
            if cancel_flags[slot_number].is_set():
                ui.update_status("Session cancelled.")
                return
            slot_fingerprints[slot_number] = fingerprint_id
            slot_timers[slot_number] = minutes * 60
            ui.update_status(f"Fingerprint saved. Charging will begin in {minutes} minutes...")
            while slot_timers[slot_number] > 0:
                if cancel_flags[slot_number].is_set():
                    ui.update_status("Session cancelled.")
                    return
                mins, secs = divmod(slot_timers[slot_number], 60)
                ui.update_slot_timer(slot_number, mins, secs)
                time.sleep(1)
                slot_timers[slot_number] -= 1
            ui.update_status("Please scan your fingerprint to unlock the charging slot...")
            match_id = None
            attempts = 0
            max_attempts = 3
            while match_id != fingerprint_id and attempts < max_attempts:
                if cancel_flags[slot_number].is_set():
                    ui.update_status("Session cancelled.")
                    return
                match_id = fingerprint.authenticate_fingerprint()
                if match_id != fingerprint_id:
                    attempts += 1
                    remaining_attempts = max_attempts - attempts
                    if remaining_attempts > 0:
                        ui.update_status(f"Fingerprint mismatch. {remaining_attempts} attempts remaining.")
                    else:
                        ui.update_status("Maximum authentication attempts reached. Session cancelled.")
                        return
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
            slot_timers.pop(slot_number, None)
            slot_fingerprints.pop(slot_number, None)
            slot_threads.pop(slot_number, None)

    t = threading.Thread(target=session_thread)
    slot_threads[slot_number] = t
    t.start()

def handle_cancel(slot_number):
    if slot_number in cancel_flags:
        ui.update_status("Please scan your fingerprint to terminate session...")
        fingerprint_id = slot_fingerprints.get(slot_number)
        if fingerprint_id is None:
            ui.update_status("No fingerprint registered for this slot.")
            return
        match_id = fingerprint.authenticate_fingerprint()
        if match_id != fingerprint_id:
            ui.update_status("Fingerprint mismatch. Session not terminated.")
            return
        cancel_flags[slot_number].set()

if __name__ == "__main__":
    root = tk.Tk()
    ui = ChargingStationUI(root, handle_session, handle_cancel)
    root.mainloop()
