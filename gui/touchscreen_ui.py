# # gui/touchscreen_ui.py

# import tkinter as tk
# from tkinter import messagebox

# class ChargingStationUI:
#     def __init__(self, master, on_start_callback):
#         self.master = master
#         self.on_start_callback = on_start_callback

#         self.master.title("Solar Charging Station")
#         self.master.geometry("800x480")

#         self.title = tk.Label(master, text="Welcome to Solar Charger", font=("Helvetica", 24))
#         self.title.pack(pady=20)

#         self.slot_frame = tk.Frame(master)
#         self.slot_frame.pack()

#         self.slot_buttons = []
#         for i in range(4):
#             btn = tk.Button(
#                 self.slot_frame, text=f"Slot {i+1}", font=("Helvetica", 18),
#                 command=lambda i=i: self.start_session(i+1),
#                 width=12, height=2
#             )
#             btn.grid(row=0, column=i, padx=10)
#             self.slot_buttons.append(btn)

#         self.status_label = tk.Label(master, text="Insert coin to begin.", font=("Helvetica", 16))
#         self.status_label.pack(pady=40)

#         self.exit_button = tk.Button(master, text="Exit", font=("Helvetica", 16), command=self.master.quit)
#         self.exit_button.pack(pady=10)

#     def start_session(self, slot_number):
#         response = messagebox.askyesno("Start Charging", f"Start session at Slot {slot_number}?")
#         if response:
#             self.on_start_callback(slot_number)

#     def update_status(self, text):
#         self.status_label.config(text=text)

#     def update_slot_timer(self, slot_number, minutes, seconds):
#         label = f"Slot {slot_number} ({minutes:02d}:{seconds:02d})"
#         self.slot_buttons[slot_number - 1].config(text=label)

#     def reset_slot_button(self, slot_number):
#         self.slot_buttons[slot_number - 1].config(text=f"Slot {slot_number}")
#         self.slot_buttons[slot_number - 1].config(state=tk.NORMAL)

#     def disable_slot_button(self, slot_number):
#         self.slot_buttons[slot_number - 1].config(state=tk.DISABLED)


# gui/touchscreen_ui.py

import tkinter as tk
from tkinter import messagebox

class ChargingStationUI:
    def __init__(self, master, on_start_callback, on_cancel_callback):
        self.master = master
        self.on_start_callback = on_start_callback
        self.on_cancel_callback = on_cancel_callback

        self.master.title("Solar Charging Station")
        self.master.geometry("800x480")

        self.title = tk.Label(master, text="Welcome to Solar Charger", font=("Helvetica", 24))
        self.title.pack(pady=20)

        self.slot_frame = tk.Frame(master)
        self.slot_frame.pack()

        self.slot_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.slot_frame, text=f"Slot {i+1}", font=("Helvetica", 18),
                command=lambda i=i: self.start_session(i+1),
                width=12, height=2
            )
            btn.grid(row=0, column=i, padx=10)
            self.slot_buttons.append(btn)

        self.status_label = tk.Label(master, text="Insert coin to begin.", font=("Helvetica", 16))
        self.status_label.pack(pady=40)

        self.cancel_button = tk.Button(master, text="Cancel Session", font=("Helvetica", 16), command=self.cancel_session)
        self.cancel_button.pack(pady=10)
        self.cancel_button.pack_forget()  # hidden by default

        self.exit_button = tk.Button(master, text="Exit", font=("Helvetica", 16), command=self.master.quit)
        self.exit_button.pack(pady=10)

        self.active_slot = None

    def start_session(self, slot_number):
        response = messagebox.askyesno("Start Charging", f"Start session at Slot {slot_number}?")
        if response:
            self.active_slot = slot_number
            self.on_start_callback(slot_number)

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
