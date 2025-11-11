import os
import time
import threading
import random
from tkinter import Tk, Toplevel, Label, Button, StringVar, Frame
import pygame
from screeninfo import get_monitors

# Suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Initialize pygame GLOBALLY at module level
pygame.init()

# ============================================================
# CONFIGURATION CONSTANTS
# ============================================================
BREAK_INTERVAL_SHORT = 60 * 60      # 60 minutes (in seconds)
BREAK_DURATION_SHORT = 2 * 60       # 2 minutes (in seconds)
BREAK_INTERVAL_LONG = 3 * 60 * 60   # 3 hours = 180 minutes (in seconds)
BREAK_DURATION_LONG = 5 * 60        # 5 minutes (in seconds)

# ============================================================
# SKIP THRESHOLD: If long break is within this time, skip short break
# Recommended: 20-30 minutes to avoid rushed transitions
# ============================================================
SKIP_THRESHOLD = 25 * 60            # 25 minutes (in seconds)

# ============================================================
# MUSIC CONFIGURATION
# Support single file or multiple files
# Examples:
#   MUSIC_FILES = ["soothing.wav"]
#   MUSIC_FILES = ["soothing.mp3", "ambient.wav", "calm.mp3"]
# ============================================================
MUSIC_FILES = ["soothing.mp3"]      # Add more files for variety

# ============================================================
# WELLNESS MESSAGES - Displayed during breaks
# Can use SEQUENTIAL or RANDOM mode below
# ============================================================
WELLNESS_MESSAGES = [
    "Rest your eyes and stretch",
    "Look 20 feet away for 20 seconds",
    "Stand up and walk around",
    "Drink water and stay hydrated",
    "Deep breathing - In for 4, hold for 4, out for 4",
    "Neck and shoulder rolls",
    "Blink slowly 10 times",
    "Relax your jaw and neck",
]

# ============================================================
# MESSAGE SELECTION MODE
# Options: "SEQUENTIAL" or "RANDOM"
# SEQUENTIAL: Messages cycle through in order each break
# RANDOM: Random message selected each break
# ============================================================
MESSAGE_MODE = "RANDOM"

# Track for sequential mode
_message_counter = 0


def get_next_message():
    """Get next wellness message based on MODE setting"""
    global _message_counter
    
    if MESSAGE_MODE == "SEQUENTIAL":
        msg = WELLNESS_MESSAGES[_message_counter % len(WELLNESS_MESSAGES)]
        _message_counter += 1
        return msg
    else:  # RANDOM
        return random.choice(WELLNESS_MESSAGES)


def get_next_music_file():
    """Select next music file"""
    return random.choice(MUSIC_FILES)


class DisengagePopup:
    """Popup window with countdown and snooze options (59-minute warning)"""
    
    def __init__(self, countdown_seconds=60, is_long_break=False):
        self.snooze_time = 0
        self.ok_clicked = False
        self.root = Tk()
        
        # Title based on break type
        if is_long_break:
            self.root.title("Long Break Coming!")
        else:
            self.root.title("Short Break Time!")
        
        # FIX: Calculate window size dynamically based on screen resolution
        # Get primary screen resolution for scaling
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Scale window based on monitor DPI/resolution
        # For 1920x1080: use 600x320
        # For 2560x1600: use 700x400 (scaled up proportionally)
        if screen_height >= 1600:
            # High-resolution monitor detected
            window_width = 700
            window_height = 400
        else:
            # Standard resolution monitor
            window_width = 600
            window_height = 320
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(False, False)
        
        # CRITICAL: Make window always on top
        self.root.wm_attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        
        # Message label with adjusted wraplength
        self.label_var = StringVar()
        self.label = Label(
            self.root, 
            textvariable=self.label_var, 
            font=("Helvetica", 28, "bold"),
            fg="red",
            wraplength=window_width - 50  # Dynamic wraplength
        )
        self.label.pack(pady=20)  # Reduced from 30 to save space
        
        # Button frame
        btn_frame = Frame(self.root)
        btn_frame.pack(pady=15)  # Reduced from 20 to save space
        
        snooze_options = [(0, "OK"), (15*60, "15 min"), (30*60, "30 min"), (60*60, "60 min")]
        for snooze_sec, text in snooze_options:
            btn = Button(
                btn_frame, 
                text=text, 
                font=("Helvetica", 12),  # Slightly smaller font for more space 
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
    
    def __init__(self, duration_seconds, is_long_break=False):
        self.duration = duration_seconds
        self.is_long_break = is_long_break
        self.windows = []  # Store all monitor windows
        self.countdown_var = None
        self.root_window = None
        
    def play_music_blocking(self):
        """
        Play music and WAIT for it to finish.
        Supports multiple music files with random selection.
        """
        try:
            # Get a music file (random selection if multiple available)
            music_file = get_next_music_file()
            
            # Check if file exists
            if not os.path.exists(music_file):
                print(f"ERROR: Music file '{music_file}' not found!")
                print(f"Current directory: {os.getcwd()}")
                print(f"Available files: {os.listdir('.')}")
                return
            
            # Initialize mixer
            pygame.mixer.init()
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)  # -1 = loop indefinitely
            
            print(f"Music started: {music_file}")
            
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
        Create a fullscreen blackout window for a specific monitor.
        Includes dynamic countdown timer (updates every minute).
        
        Args:
            monitor: Monitor object from screeninfo
            is_primary: Whether this is the primary monitor (for main Tk window)
        """
        if is_primary:
            # Use Tk() for the first window
            win = Tk()
            self.root_window = win
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
            # Create frame for centered content
            content_frame = Frame(win, bg='black')
            content_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            # ============================================================
            # DYNAMIC COUNTDOWN TIMER (updates every minute)
            # Format: "Break Time - M:SS" where M is minutes
            # ============================================================
            self.countdown_var = StringVar()
            self.countdown_label = Label(
                content_frame,
                textvariable=self.countdown_var,
                font=("Helvetica", 32, "bold"),
                fg="cyan",
                bg="black"
            )
            self.countdown_label.pack(pady=20)
            
            # Initialize countdown display
            self.update_countdown(self.duration)
            
            # ============================================================
            # WELLNESS MESSAGE (random or sequential)
            # ============================================================
            wellness_msg = get_next_message()
            
            message_label = Label(
                content_frame,
                text=f"{wellness_msg}\n\nMusic is playing...",
                font=("Helvetica", 20),
                fg="white",
                bg="black",
                wraplength=400,
                justify="center"
            )
            message_label.pack(pady=20)
        
        return win
    
    def update_countdown(self, remaining):
        """
        Update countdown timer display every minute.
        Called recursively until break ends.
        """
        if remaining > 0 and self.countdown_var and self.root_window:
            # Calculate minutes and seconds
            mins = int(remaining) // 60
            secs = int(remaining) % 60
            
            # Update display (shows MM:SS format, updates every minute)
            # Only update when seconds reach 0 (cleaner display)
            if secs == 0 or remaining < 60:
                self.countdown_var.set(f"Break Time - {mins}:{secs:02d}")
            
            # Schedule next update in 1 second
            # But we'll only show changes every 60 seconds
            if self.root_window:
                self.root_window.after(1000, lambda: self.update_countdown(remaining - 1))
    
    def fullscreen_blackout_multimonitor(self):
        """Create fullscreen blackout windows on ALL monitors"""
        
        # Get all monitors
        monitors = get_monitors()
        print(f"Detected {len(monitors)} monitor(s)")
        
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
    """
    Main timer loop with corrected break logic.
    
    NEW LOGIC:
    - Tracks both short (58 min) and long (180 min) break timers
    - Long break takes absolute priority
    - If long break is coming within SKIP_THRESHOLD, short break is skipped
    - Only resets both timers on long break execution
    - Only resets short timer on short break execution
    """
    start_time = time.time()
    last_short_break = start_time
    last_long_break = start_time
    
    print("=" * 70)
    print("Disengagement Script Started")
    print("=" * 70)
    print(f"Short break interval: {BREAK_INTERVAL_SHORT//60} minutes")
    print(f"Short break duration: {BREAK_DURATION_SHORT//60} minutes")
    print(f"Long break interval: {BREAK_INTERVAL_LONG//3600} hours ({BREAK_INTERVAL_LONG//60} minutes)")
    print(f"Long break duration: {BREAK_DURATION_LONG//60} minutes")
    print(f"Skip threshold: {SKIP_THRESHOLD//60} minutes (skip short break if long within this)")
    print(f"Music files: {MUSIC_FILES}")
    print(f"Message mode: {MESSAGE_MODE}")
    print("=" * 70)
    
    # Detect monitors at startup
    monitors = get_monitors()
    print(f"\nDetected {len(monitors)} monitor(s):")
    for monitor in monitors:
        print(f"  - {monitor.name}: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y})")
    print("=" * 70 + "\n")
    
    while True:
        current_time = time.time()
        elapsed_since_short = current_time - last_short_break
        elapsed_since_long = current_time - last_long_break
        
        # ============================================================
        # PRIORITY 1: CHECK FOR LONG BREAK (takes absolute priority)
        # ============================================================
        if elapsed_since_long >= BREAK_INTERVAL_LONG - 60:
            print("\n" + "=" * 70)
            print(f"[{time.strftime('%H:%M:%S')}] LONG BREAK TRIGGERED (3 hours elapsed)")
            print("=" * 70)
            
            popup = DisengagePopup(countdown_seconds=60, is_long_break=True)
            snooze, clicked = popup.show()
            
            if snooze == 0 or not clicked:
                # No snooze, enforce break
                print("User pressed OK - Executing long break")
                enforcer = BreakEnforcer(BREAK_DURATION_LONG, is_long_break=True)
                enforcer.enforce()
                last_long_break = time.time()
                last_short_break = time.time()  # Reset both timers
            else:
                # Snooze requested
                snooze_mins = snooze // 60
                print(f"User snoozed for {snooze_mins} minutes")
                time.sleep(snooze)
                enforcer = BreakEnforcer(BREAK_DURATION_LONG, is_long_break=True)
                enforcer.enforce()
                last_long_break = time.time()
                last_short_break = time.time()  # Reset both timers
                
        # ============================================================
        # PRIORITY 2: CHECK FOR SHORT BREAK (with skip logic)
        # ============================================================
        elif elapsed_since_short >= BREAK_INTERVAL_SHORT - 60:
            # Calculate time remaining until long break
            time_until_long = BREAK_INTERVAL_LONG - elapsed_since_long
            
            # ============================================================
            # SKIP LOGIC: If long break is coming too soon, skip this short break
            # ============================================================
            if time_until_long <= SKIP_THRESHOLD:
                print(f"\n[{time.strftime('%H:%M:%S')}] Short break SKIPPED (long break in {time_until_long//60:.0f} min)")
                time.sleep(60)  # Wait a minute before rechecking
                
            else:
                print("\n" + "=" * 70)
                print(f"[{time.strftime('%H:%M:%S')}] SHORT BREAK TRIGGERED (58 minutes elapsed)")
                print("=" * 70)
                
                popup = DisengagePopup(countdown_seconds=60, is_long_break=False)
                snooze, clicked = popup.show()
                
                if snooze == 0 or not clicked:
                    # No snooze, enforce break
                    print("User pressed OK - Executing short break")
                    enforcer = BreakEnforcer(BREAK_DURATION_SHORT, is_long_break=False)
                    enforcer.enforce()
                    last_short_break = time.time()
                    # ✅ DON'T reset last_long_break - keep it advancing
                    
                else:
                    # Snooze requested
                    snooze_mins = snooze // 60
                    print(f"User snoozed for {snooze_mins} minutes")
                    time.sleep(snooze)
                    enforcer = BreakEnforcer(BREAK_DURATION_SHORT, is_long_break=False)
                    enforcer.enforce()
                    last_short_break = time.time()
                    # ✅ DON'T reset last_long_break
        
        else:
            # Calculate time until next break
            time_to_short = (BREAK_INTERVAL_SHORT - 60 - elapsed_since_short) / 60
            time_to_long = (BREAK_INTERVAL_LONG - 60 - elapsed_since_long) / 60
            
            status = f"⏳ Waiting... Short in {time_to_short:5.1f}m | Long in {time_to_long:5.1f}m"
            print(f"[{time.strftime('%H:%M:%S')}] {status}", end='\r')
            
            # Sleep for a minute before checking again
            time.sleep(60)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\nDisengagement script stopped by user.")
        pygame.mixer.music.stop()
        exit(0)
