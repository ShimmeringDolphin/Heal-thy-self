import os
import sys
import time
import threading
from tkinter import Tk, Label, Button, StringVar
import pygame

BREAK_INTERVAL = 58 * 60            # 58 minutes in seconds
SNOOZE_OPTIONS = [0, 15 * 60, 30 * 60, 60 * 60]  # 0, 15, 30, 60 min in seconds
BREAK_DURATION = 2 * 60             # 2 min disengagement in seconds
MUSIC_FILE = "soothing.mp3"

def lock_or_blackout():
    try:
        # Try locking the workstation
        os.system("rundll32.exe user32.dll,LockWorkStation")
    except Exception:
        # Blackout fallback (fullscreen black window)
        win = Tk()
        win.attributes('-fullscreen', True)
        win.configure(bg='black')
        win.after(BREAK_DURATION * 1000, lambda: win.destroy())
        win.mainloop()

def play_music():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.play()
    except Exception as e:
        print("Unable to play music:", e)

def disengage():
    # Blackout or lock, and play music (in parallel if possible)
    t = threading.Thread(target=play_music)
    t.start()
    lock_or_blackout()
    pygame.mixer.music.stop()

# Tkinter popup with countdown timer
class DisengagePopup:
    def __init__(self):
        self.snooze_time = 0
        self.ok_clicked = False
        self.root = Tk()
        self.root.title("Time to be healthy!")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.label_var = StringVar()
        self.label = Label(self.root, textvariable=self.label_var, font=("Helvetica", 24))
        self.label.pack(pady=30)
        b_frame = []
        for text, snooze_s in zip(["OK", "15 min", "30 min", "60 min"], SNOOZE_OPTIONS):
            btn = Button(self.root, text=text, font=("Helvetica", 16), width=8,
                         command=lambda st=snooze_s: self.on_button(st))
            btn.pack(side="left", padx=5, expand=True)
            b_frame.append(btn)
        self.seconds = 60

    def on_button(self, snooze_sec):
        self.snooze_time = snooze_sec
        self.ok_clicked = True
        self.root.destroy()

    def countdown(self):
        if self.seconds >= 0:
            self.label_var.set(f"Time to be healthy again in\n{self.seconds} seconds")
            self.seconds -= 1
            self.root.after(1000, self.countdown)
        else:
            self.root.destroy()

    def show(self):
        self.countdown()
        self.root.mainloop()
        return self.snooze_time, self.ok_clicked

def main_loop():
    t0 = time.time()
    while True:
        t_elapsed = time.time() - t0
        # Wait for 57 minutes
        to_wait = BREAK_INTERVAL - 60 - (t_elapsed % BREAK_INTERVAL)
        if to_wait > 0:
            time.sleep(to_wait)
        # At 57 minutes, popup countdown
        popup = DisengagePopup()
        snooze, clicked = popup.show()
        # Wait for snooze; 0 = OK or no click
        if snooze == 0 or not clicked:
            disengage()
            time.sleep(BREAK_DURATION)
        else:
            time.sleep(snooze)
            disengage()
            time.sleep(BREAK_DURATION)

if __name__ == "__main__":
    main_loop()
