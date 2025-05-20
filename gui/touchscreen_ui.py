# gui/touchscreen_ui.py

import tkinter as tk
from tkinter import messagebox

class ChargingStationUI:
    def __init__(self, master, on_start_callback, on_cancel_callback):
        self.master = master
        self.on_start_callback = on_start_callback
        self.on_cancel_callback = on_cancel_callback

        self.master.title("Solar Charging Station")
        self.master.geometry("1920x1080")
        self.master.minsize(1200, 700)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(expand=True, fill="both")
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        self.title = tk.Label(self.main_frame, text="Please select your charging slot:", font=("Helvetica", 24, "bold"), fg="#168bfa")
        self.title.pack(pady=(20, 10))

        # Phone Slots Section
        self.phone_label = tk.Label(self.main_frame, text="Phone Slots:", font=("Helvetica", 18, "bold"), fg="#168bfa")
        self.phone_label.pack()

        self.phone_frame = tk.Frame(self.main_frame)
        self.phone_frame.pack(expand=True, fill="both", pady=(0, 20))
        for r in range(3):
            self.phone_frame.rowconfigure(r, weight=1)
        for c in range(3):
            self.phone_frame.columnconfigure(c, weight=1)

        self.slot_buttons = []
        phone_locker = [False, True, True, False, True, True, False, True, True]  # 1-indexed
        self.button_fonts = []
        for i in range(9):
            row = i // 3
            col = i % 3
            locker_text = "Locker" if phone_locker[i] else "No Locker"
            btn_font = ("Helvetica", 18, "bold")
            btn = tk.Button(
                self.phone_frame,
                text=f"Slot {i+1}\n{locker_text}",
                font=btn_font,
                bg="#168bfa", fg="white",
                command=lambda i=i: self.start_session(i+1)
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.slot_buttons.append(btn)
            self.button_fonts.append(btn_font)

        # Laptop Slots Section
        self.laptop_label = tk.Label(self.main_frame, text="Laptop Slots:", font=("Helvetica", 18, "bold"), fg="#168bfa")
        self.laptop_label.pack(pady=(10, 0))

        self.laptop_frame = tk.Frame(self.main_frame)
        self.laptop_frame.pack(expand=True, fill="x", pady=(0, 20))
        for c in range(4):
            self.laptop_frame.columnconfigure(c, weight=1)

        for i in range(4):
            slot_num = 10 + i
            btn_font = ("Helvetica", 18, "bold")
            btn = tk.Button(
                self.laptop_frame,
                text=f"Slot {i+1}\nLocker",
                font=btn_font,
                bg="#168bfa", fg="white",
                command=lambda slot_num=slot_num: self.start_session(slot_num)
            )
            btn.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.slot_buttons.append(btn)
            self.button_fonts.append(btn_font)

        # Responsive font resizing
        self.master.bind('<Configure>', self._on_resize)

        self.status_label = tk.Label(master, text="Insert coin to begin.", font=("Helvetica", 16))
        self.status_label.pack(pady=40)

        self.cancel_button = tk.Button(master, text="Cancel Session", font=("Helvetica", 16), command=self.cancel_session)
        self.cancel_button.pack(pady=10)
        self.cancel_button.pack_forget()  # hidden by default

        self.exit_button = tk.Button(master, text="Exit", font=("Helvetica", 16), command=self.master.quit)
        self.exit_button.pack(pady=10)

        self.active_slot = None

    def _on_resize(self, event):
        # Dynamically adjust font size based on window size, favoring height for widescreen
        w = self.master.winfo_width()
        h = self.master.winfo_height()
        base_size = h // 30
        for btn in self.slot_buttons:
            btn.config(font=("Helvetica", base_size, "bold"))
        self.title.config(font=("Helvetica", base_size+6, "bold"))
        self.phone_label.config(font=("Helvetica", base_size+2, "bold"))
        self.laptop_label.config(font=("Helvetica", base_size+2, "bold"))

    def start_session(self, slot_number):
        if self.active_slot == slot_number:
            # Session is running for this slot
            response = messagebox.askquestion(
                "Session Active",
                f"Slot {slot_number} is currently charging.\nWould you like to add time (insert coin) or terminate charging?",
                icon='question',
                type='yesnocancel',
                default='yes',
                detail='Yes: Add Time\nNo: Terminate Charging\nCancel: Do Nothing'
            )
            if response == 'yes':
                if self._fingerprint_prompt():
                    self.on_start_callback(slot_number)  # Add time
            elif response == 'no':
                if self._fingerprint_prompt():
                    self.on_cancel_callback(slot_number)  # Terminate
            # Cancel does nothing
            return
        # Normal session start
        response = messagebox.askyesno("Start Charging", f"Start session at Slot {slot_number}?")
        if response:
            self.active_slot = slot_number
            self.on_start_callback(slot_number)

    def _fingerprint_prompt(self):
        # Placeholder for fingerprint scan dialog
        return messagebox.askokcancel("Fingerprint Required", "Please scan your fingerprint to continue.")

    def update_status(self, text):
        self.status_label.config(text=text)

    def update_slot_timer(self, slot_number, minutes, seconds):
        label = f"Slot {slot_number} ({minutes:02d}:{seconds:02d})"
        self.slot_buttons[slot_number - 1].config(text=label)

    def reset_slot_button(self, slot_number):
        self.slot_buttons[slot_number - 1].config(text=f"Slot {slot_number}", state=tk.NORMAL)
        self.cancel_button.pack_forget()
        self.active_slot = None

    def disable_slot_button(self, slot_number):
        self.slot_buttons[slot_number - 1].config(state=tk.DISABLED)

    def show_cancel_button(self):
        self.cancel_button.pack()

    def cancel_session(self):
        if self.active_slot:
            self.on_cancel_callback(self.active_slot)
