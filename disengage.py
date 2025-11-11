import os
import time
import threading
from tkinter import Tk, Toplevel, Label, Button, StringVar, Frame
import pygame
from screeninfo import get_monitors

# Suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Initialize pygame GLOBALLY at module level
pygame.init()

# Constants
BREAK_INTERVAL_SHORT = 58 * 60  # 58 minutes
BREAK_DURATION_SHORT = 2 * 60    # 2 minutes
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
    """Fullscreen break enforcer with music - supports multiple monitors"""
    
    def __init__(self, duration_seconds):
        self.duration = duration_seconds
        self.music_file = MUSIC_FILE
        self.windows = []  # Store all monitor windows
        
    def play_music_blocking(self):
        """
        Play music and WAIT for it to finish
        """
        try:
            # Check if file exists
            if not os.path.exists(self.music_file):
                print(f"ERROR: Music file '{self.music_file}' not found!")
                print(f"Current directory: {os.getcwd()}")
                return
            
            # Initialize mixer
            pygame.mixer.init()
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(-1)  # -1 = loop indefinitely
            
            print(f"Music started: {self.music_file}")
            
            # Wait for duration while checking if music is still playing
            elapsed = 0
            while elapsed < self.duration:
                if pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    elapsed += 0.1
                else:
                    # Music stopped, restart it
                    pygame.mixer.music.play(-1)
                
        except Exception as e:
            print(f"Music playback error: {e}")
        finally:
            try:
                pygame.mixer.music.stop()
            except:
                pass
            
    def create_blackout_window(self, monitor, is_primary=False):
        """
        Create a fullscreen blackout window for a specific monitor
        
        Args:
            monitor: Monitor object from screeninfo
            is_primary: Whether this is the primary monitor (for main Tk window)
        """
        if is_primary:
            # Use Tk() for the first window
            win = Tk()
        else:
            # Use Toplevel() for additional monitors
            win = Toplevel()
            
        win.title("Break Time")
        
        # Position window on specific monitor using geometry
        # Format: WIDTHxHEIGHT+X_OFFSET+Y_OFFSET
        geometry_string = f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}"
        win.geometry(geometry_string)
        
        print(f"Creating window on monitor: {monitor.name} at {geometry_string}")
        
        # ============================================================
        # Window Appearance Settings
        # ============================================================
        win.configure(bg='black')
        
        # ============================================================
        # Window Frame Override
        # ============================================================
        win.overrideredirect(True)
        
        # ============================================================
        # Keep window on top
        # ============================================================
        win.attributes('-topmost', True)
        
        # ============================================================
        # Input Focus Control
        # ============================================================
        win.focus_force()
        if is_primary:
            win.grab_set()  # Only grab input on primary window
        
        # ============================================================
        # Window Close Prevention
        # ============================================================
        win.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # ============================================================
        # Keyboard Shortcut Blocking (only on primary window)
        # ============================================================
        if is_primary:
            win.bind('<Escape>', lambda e: None)
            win.bind('<Alt-F4>', lambda e: None)
            win.bind('<Alt-Tab>', lambda e: None)
            win.bind('<Control-Alt-Delete>', lambda e: None)
            win.bind('<Super_L>', lambda e: None)
            win.bind('<Super_R>', lambda e: None)
        
        # Message in center (only on primary monitor)
        if is_primary or monitor.is_primary:
            label = Label(
                win, 
                text=f"Break Time - {self.duration//60} minutes\n\nPlease rest your eyes and stretch\n\nMusic is playing...",
                font=("Helvetica", 24),
                fg="white",
                bg="black"
            )
            label.place(relx=0.5, rely=0.5, anchor="center")
        
        return win
    
    def fullscreen_blackout_multimonitor(self):
        """Create fullscreen blackout windows on ALL monitors"""
        
        # Get all monitors
        monitors = get_monitors()
        #print(f"Detected {len(monitors)} monitor(s)")
        
        # Create windows for each monitor
        for idx, monitor in enumerate(monitors):
            is_primary = (idx == 0)  # First window is primary
            win = self.create_blackout_window(monitor, is_primary)
            self.windows.append(win)
        
        # Schedule all windows to close after duration
        # Use the first (primary) window for scheduling
        if self.windows:
            self.windows[0].after(int(self.duration * 1000), self.close_all_windows)
            
            # Start mainloop on primary window
            self.windows[0].mainloop()
    
    def close_all_windows(self):
        """Close all blackout windows"""
        for win in self.windows:
            try:
                win.destroy()
            except:
                pass
        self.windows.clear()
        
    def enforce(self):
        """
        Main enforcement method - blackout all monitors with music
        """
        # Start music in a separate thread
        music_thread = threading.Thread(target=self.play_music_blocking, daemon=False)
        music_thread.start()
        
        # Small delay to ensure music starts
        time.sleep(0.2)
        
        # Show fullscreen blackout on ALL monitors
        self.fullscreen_blackout_multimonitor()
        
        # Wait for music thread to finish
        music_thread.join(timeout=5)


def main_loop():
    """Main timer loop"""
    start_time = time.time()
    last_short_break = start_time
    last_long_break = start_time
    
    print("Disengagement script started...")
    print(f"Music file: {MUSIC_FILE}")
    print(f"Short break interval: {BREAK_INTERVAL_SHORT//60} minutes")
    print(f"Long break interval: {BREAK_INTERVAL_LONG//3600} hours")
    
    # Detect monitors at startup
    monitors = get_monitors()
    print(f"\nDetected {len(monitors)} monitor(s):")
    for monitor in monitors:
        print(f"  - {monitor.name}: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y})")
    
    while True:
        current_time = time.time()
        elapsed_since_short = current_time - last_short_break
        elapsed_since_long = current_time - last_long_break
        
        # Check for 3-hour long break first (higher priority)
        if elapsed_since_long >= BREAK_INTERVAL_LONG - 60:
            print("\n3-hour break triggered!")
            popup = DisengagePopup(countdown_seconds=60)
            snooze, clicked = popup.show()
            
            if snooze == 0 or not clicked:
                enforcer = BreakEnforcer(BREAK_DURATION_LONG)
                enforcer.enforce()
                last_long_break = time.time()
                last_short_break = time.time()
            else:
                print(f"User snoozed for {snooze//60} minutes")
                time.sleep(snooze)
                enforcer = BreakEnforcer(BREAK_DURATION_LONG)
                enforcer.enforce()
                last_long_break = time.time()
                last_short_break = time.time()
                
        # Check for regular 58-minute break
        elif elapsed_since_short >= BREAK_INTERVAL_SHORT - 60:
            print("\n58-minute break triggered!")
            popup = DisengagePopup(countdown_seconds=60)
            snooze, clicked = popup.show()
            
            if snooze == 0 or not clicked:
                enforcer = BreakEnforcer(BREAK_DURATION_SHORT)
                enforcer.enforce()
                last_short_break = time.time()
            else:
                print(f"User snoozed for {snooze//60} minutes")
                time.sleep(snooze)
                enforcer = BreakEnforcer(BREAK_DURATION_SHORT)
                enforcer.enforce()
                last_short_break = time.time()
        else:
            # Sleep for a minute before checking again
            time.sleep(60)


if __name__ == "__main__":
    main_loop()
