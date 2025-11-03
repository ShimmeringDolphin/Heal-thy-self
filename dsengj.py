import os
import sys
import time
import threading
from tkinter import Tk, Label, Button, StringVar, Frame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# Suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Constants
BREAK_INTERVAL_SHORT = 1 * 60  # 58 minutes
BREAK_DURATION_SHORT = 0.5 * 60    # 2 minutes
BREAK_INTERVAL_LONG = 3 * 60 * 60  # 3 hours
BREAK_DURATION_LONG = 5 * 60     # 5 minutes
MUSIC_FILE = "soothing.mp3"

class DisengagePopup:
    """Popup window with countdown and snooze options"""
    
    def __init__(self, countdown_seconds=60):
        self.snooze_time = 0
        self.ok_clicked = False
        self.root = Tk()
        self.root.title("Time to be healthy!")
        self.root.geometry("500x250")
        self.root.resizable(False, False)
        
        # CRITICAL: Make window always on top
        self.root.wm_attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        
        # Message label
        self.label_var = StringVar()
        self.label = Label(
            self.root, 
            textvariable=self.label_var, 
            font=("Helvetica", 28, "bold"),
            fg="red"
        )
        self.label.pack(pady=30)
        
        # Button frame
        btn_frame = Frame(self.root)
        btn_frame.pack(pady=20)
        
        snooze_options = [(0, "OK"), (15*60, "15 min"), (30*60, "30 min"), (60*60, "60 min")]
        for snooze_sec, text in snooze_options:
            btn = Button(
                btn_frame, 
                text=text, 
                font=("Helvetica", 14), 
                width=10,
                height=2,
                command=lambda st=snooze_sec: self.on_button(st)
            )
            btn.pack(side="left", padx=5)
        
        self.seconds = countdown_seconds
        self.running = True
        
    def on_button(self, snooze_sec):
        self.snooze_time = snooze_sec
        self.ok_clicked = True
        self.running = False
        self.root.destroy()
        
    def countdown(self):
        if self.running and self.seconds >= 0:
            self.label_var.set(f"Time to be healthy again in\n{self.seconds} seconds")
            self.seconds -= 1
            self.root.after(1000, self.countdown)
        elif self.running:
            # Countdown finished, user didn't respond
            self.running = False
            self.root.destroy()
            
    def show(self):
        self.countdown()
        self.root.mainloop()
        return self.snooze_time, self.ok_clicked


class BreakEnforcer:
    """Fullscreen break enforcer with music"""
    
    def __init__(self, duration_seconds):
        self.duration = duration_seconds
        self.music_file = MUSIC_FILE
        
    def lock_workstation_with_delay(self):
        """Lock workstation and keep music playing"""
        # Start music first
        music_thread = threading.Thread(target=self.play_music, daemon=False)
        music_thread.start()
        
        # Small delay to ensure music starts
        time.sleep(0.5)
        
        # Try to lock workstation
        '''try:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            # Wait for break duration even after lock
            # Music will continue in background
            time.sleep(self.duration)
        except Exception as e:
            print(f"Lock failed: {e}")
            # Fallback to blackout
            self.fullscreen_blackout()
        finally:
            # Ensure music stops
            pygame.mixer.music.stop()'''
            
    def play_music(self):
        """Play music for the break duration"""
        try:
            if os.path.exists(self.music_file):
                pygame.mixer.init()
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.play()
                # Wait for break duration
                time.sleep(self.duration)
                pygame.mixer.music.stop()
        except Exception as e:
            print(f"Music playback error: {e}")
            
    def fullscreen_blackout(self):
        """Create unescapable fullscreen blackout window"""
        root = Tk()
        root.title("Break Time")
        
        # Fullscreen and always on top
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)
        root.configure(bg='black')
        
        # Prevent window manager decorations
        root.overrideredirect(True)
        
        # Grab all input focus
        root.focus_force()
        root.grab_set()
        
        # Disable Alt+F4
        root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Bind escape attempts to do nothing
        root.bind('<Escape>', lambda e: None)
        root.bind('<Alt-F4>', lambda e: None)
        root.bind('<Alt-Tab>', lambda e: None)
        
        # Message in center
        label = Label(
            root, 
            text=f"Break Time - {self.duration//60} minutes\n\nPlease rest your eyes and stretch",
            font=("Helvetica", 24),
            fg="white",
            bg="black"
        )
        label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Auto-close after duration
        root.after(self.duration * 1000, root.destroy)
        
        root.mainloop()
        
    def enforce(self):
        """Main enforcement method"""
        self.lock_workstation_with_delay()


def main_loop():
    """Main timer loop"""
    start_time = time.time()
    last_short_break = start_time
    last_long_break = start_time
    
    while True:
        current_time = time.time()
        elapsed_since_short = current_time - last_short_break
        elapsed_since_long = current_time - last_long_break
        
        # Check for 3-hour long break first (higher priority)
        if elapsed_since_long >= BREAK_INTERVAL_LONG - 60:
            # 3-hour break popup at 2h59m
            popup = DisengagePopup(countdown_seconds=60)
            snooze, clicked = popup.show()
            
            if snooze == 0 or not clicked:
                # No snooze, enforce break
                enforcer = BreakEnforcer(BREAK_DURATION_LONG)
                enforcer.enforce()
                last_long_break = time.time()
                last_short_break = time.time()  # Reset short break too
            else:
                # Snooze requested
                time.sleep(snooze)
                enforcer = BreakEnforcer(BREAK_DURATION_LONG)
                enforcer.enforce()
                last_long_break = time.time()
                last_short_break = time.time()
                
        # Check for regular 58-minute break
        elif elapsed_since_short >= BREAK_INTERVAL_SHORT - 60:
            # Regular break popup at 57 minutes
            popup = DisengagePopup(countdown_seconds=60)
            snooze, clicked = popup.show()
            
            if snooze == 0 or not clicked:
                enforcer = BreakEnforcer(BREAK_DURATION_SHORT)
                enforcer.enforce()
                last_short_break = time.time()
            else:
                time.sleep(snooze)
                enforcer = BreakEnforcer(BREAK_DURATION_SHORT)
                enforcer.enforce()
                last_short_break = time.time()
        else:
            # Sleep for a minute before checking again
            time.sleep(60)


if __name__ == "__main__":
    main_loop()
