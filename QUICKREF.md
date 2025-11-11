# QUICK REFERENCE CARD - Disengage v2.0

## **30-SECOND SETUP**

```bash
# 1. Install dependencies
pip install pygame screeninfo

# 2. Add music file
# Copy soothing.wav (or .mp3) to same folder as script

# 3. Run
python disengage-v2.py
```

---

## **TESTING MODE (2-minute cycle)**

Change these lines at top of script:
```python
BREAK_INTERVAL_SHORT = 2 * 60       # 2 minutes
BREAK_DURATION_SHORT = 10           # 10 seconds
BREAK_INTERVAL_LONG = 6 * 60        # 6 minutes
BREAK_DURATION_LONG = 15            # 15 seconds
SKIP_THRESHOLD = 1 * 60             # 1 minute
```

Then run: `python disengage-v2.py`

---

## **CONFIG CHEAT SHEET**

| What | Line | Value |
|------|------|-------|
| Short break interval | `BREAK_INTERVAL_SHORT` | 58 * 60 |
| Short break duration | `BREAK_DURATION_SHORT` | 2 * 60 |
| Long break interval | `BREAK_INTERVAL_LONG` | 3 * 60 * 60 |
| Long break duration | `BREAK_DURATION_LONG` | 5 * 60 |
| Skip threshold | `SKIP_THRESHOLD` | 25 * 60 |
| Music file(s) | `MUSIC_FILES` | ["soothing.wav"] |
| Message mode | `MESSAGE_MODE` | "RANDOM" |

---

## **BREAK CYCLE (AFTER FIX)**

```
0h 58m   →  SHORT break (2 min)
1h 56m   →  SHORT break (2 min)
2h 54m   →  SHORT break SKIPPED (long in 6 min)
3h 00m   →  LONG break (5 min)  ← Resets both timers
3h 58m   →  SHORT break (2 min)
4h 56m   →  SHORT break (2 min)
5h 54m   →  SHORT break SKIPPED
6h 00m   →  LONG break (5 min)  ← Resets both timers
```

---

## **FILE STRUCTURE**

```
your-project-folder/
├── disengage-v2.py           ← Main script
├── soothing.wav              ← Music file (required)
├── ambient.wav               ← Optional: more music
└── README-v2.md              ← Documentation
```

---

## **KEY IMPROVEMENTS**

✅ **Issue #2 FIXED**: Skip logic prevents conflicting breaks
✅ **Observation #3**: Minute-level countdown (MM:00 format)
✅ **Observation #4**: Random wellness messages (8 different)
✅ **Observation #5**: Multiple music file support (MP3 & WAV)
✅ **Multi-Monitor**: All screens blackout simultaneously

---

## **CONVERT TO .EXE**

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --add-data "soothing.wav;." disengage-v2.py
```

Find exe in: `dist/disengage-v2.exe`

---

## **AUTO-START ON WINDOWS**

1. Press `Win + R`
2. Type: `shell:startup`
3. Copy .exe and music files there
4. Done! Runs on next login

---

## **TROUBLESHOOTING**

| Problem | Solution |
|---------|----------|
| Music not playing | Check file exists in folder + use .wav/.mp3 |
| Popup doesn't appear | Run from terminal (not IDE) |
| Dual monitor not blocked | Verify screeninfo installed |
| Script crashes | Run from terminal to see errors |

---

## **CONSOLE OUTPUT INTERPRETATION**

```
[14:32:45] SHORT BREAK TRIGGERED (58 minutes elapsed)
→ Your short break started

[14:35:22] ⏳ Waiting... Short in 23.4m | Long in 154.6m
→ Normal waiting (safe to ignore)

[16:51:03] Short break SKIPPED (long break in 4 min)
→ Skip logic worked! Waiting for long break

[17:00:00] LONG BREAK TRIGGERED (3 hours elapsed)
→ Your long break started
```

---

## **CUSTOMIZATION EXAMPLES**

### Example A: 90-minute cycles
```python
BREAK_INTERVAL_SHORT = 85 * 60
BREAK_INTERVAL_LONG = 4 * 60 * 60
SKIP_THRESHOLD = 30 * 60
```

### Example B: Random music + messages
```python
MUSIC_FILES = ["track1.mp3", "track2.wav", "track3.mp3"]
MESSAGE_MODE = "RANDOM"
```

### Example C: Aggressive breaks
```python
BREAK_INTERVAL_SHORT = 45 * 60
BREAK_INTERVAL_LONG = 2 * 60 * 60
SKIP_THRESHOLD = 15 * 60
```

---

## **DEPENDENCIES**

- Python 3.8+
- pygame (for music playback)
- screeninfo (for multi-monitor support)
- Tkinter (built-in with Python)

Install with: `pip install pygame screeninfo`

---

## **VERSION**

**v2.0** - Production Ready ✅
- All 4 improvements implemented
- Multi-monitor tested
- User feedback incorporated

---

## **FILES PROVIDED**

1. **disengage-v2.py** - Main executable script
2. **README-v2.md** - Complete documentation
3. **QUICKREF.md** - This file

---

**Start here**: Copy files → Add music → Run script → Test with 2-min cycle → Deploy
