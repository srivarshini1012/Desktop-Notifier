import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import json
import os
import wave
import struct
import math
from datetime import datetime, timedelta
try:
    import pygame
except Exception as e:
    raise RuntimeError("pygame is required. Install with: pip install pygame") from e

# ------------------------- Settings -------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
DEFAULT_CHIME = os.path.join(APP_DIR, "default_chime.wav")

BG_COLOR = "#f5c6ea"  # soft pink color for full background
TEXT_COLOR = "black"

def generate_default_chime(path=DEFAULT_CHIME):
    if os.path.exists(path):
        return
    framerate = 44100
    duration = 0.25
    freqs = [880.0, 1320.0]
    data = []
    amplitude = 16000
    for f in freqs:
        for i in range(int(framerate * duration)):
            t = i / framerate
            sample = amplitude * math.sin(2 * math.pi * f * t) * (0.5 + 0.5*math.cos(math.pi * (t/duration)))
            data.append(int(sample))
        for i in range(int(framerate * 0.08)):
            data.append(0)
    for f in freqs:
        for i in range(int(framerate * duration)):
            t = i / framerate
            sample = amplitude * math.sin(2 * math.pi * f * t) * (0.5 + 0.5*math.cos(math.pi * (t/duration)))
            data.append(int(sample))
        for i in range(int(framerate * 0.08)):
            data.append(0)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        for s in data:
            wf.writeframes(struct.pack('<h', max(-32767, min(32767, int(s)))))

generate_default_chime()

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f)

settings = load_settings()
initial_sound = settings.get("sound_path", DEFAULT_CHIME)

pygame.mixer.init()
_sound_lock = threading.Lock()

def play_sound_loop(path):
    with _sound_lock:
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Error playing sound:", e)

def stop_sound():
    with _sound_lock:
        try:
            pygame.mixer.music.stop()
        except:
            pass

alarm_time = None
repeat_daily = False
alarm_running = False
snooze_until = None
sound_path = initial_sound
_scheduler_thread = None
_scheduler_stop = threading.Event()

def set_next_alarm(hour_int, minute_int, once_or_daily):
    global alarm_time, repeat_daily
    now = datetime.now()
    candidate = now.replace(hour=hour_int, minute=minute_int, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    alarm_time = candidate
    repeat_daily = (once_or_daily == "Daily")
    return alarm_time

def scheduler_loop():
    global alarm_running, snooze_until, alarm_time
    while not _scheduler_stop.is_set():
        now = datetime.now()
        if snooze_until:
            if now >= snooze_until:
                snooze_until = None
                trigger_alarm()
        elif alarm_time and now >= alarm_time:
            trigger_alarm()
            if repeat_daily:
                alarm_time += timedelta(days=1)
            else:
                alarm_time = None
                alarm_running = False
                _scheduler_stop.set()
                break
        time.sleep(0.8)

def trigger_alarm():
    threading.Thread(target=play_sound_loop, args=(sound_path,), daemon=True).start()
    root.event_generate("<<ShowPopup>>", when="tail")

# ------------------------- UI -------------------------
root = tk.Tk()
root.title("Custom Notifier")
root.geometry("500x400")
root.minsize(500, 400)
root.configure(bg=BG_COLOR)

main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(expand=True, fill="both", padx=20, pady=20)

title_var = tk.StringVar(value="Reminder")
msg_var = tk.StringVar(value="It's time for your task.")
hour_var = tk.StringVar(value=str(datetime.now().hour).zfill(2))
min_var = tk.StringVar(value=str(datetime.now().minute).zfill(2))
mode_var = tk.StringVar(value="Once")
sound_label_var = tk.StringVar(value=os.path.basename(initial_sound))

main_frame.columnconfigure(1, weight=1)

# Labels & Entries
tk.Label(main_frame, text="Title", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)\
    .grid(row=0, column=0, sticky="w", pady=5)
tk.Entry(main_frame, textvariable=title_var, font=("Segoe UI", 11))\
    .grid(row=0, column=1, columnspan=3, sticky="ew", pady=5)

tk.Label(main_frame, text="Message", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)\
    .grid(row=1, column=0, sticky="w", pady=5)
tk.Entry(main_frame, textvariable=msg_var, font=("Segoe UI", 11))\
    .grid(row=1, column=1, columnspan=3, sticky="ew", pady=5)

tk.Label(main_frame, text="Time (24h)", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)\
    .grid(row=2, column=0, sticky="w", pady=5)
tk.Entry(main_frame, textvariable=hour_var, width=4, font=("Segoe UI", 11))\
    .grid(row=2, column=1, sticky="w", padx=(0,5))
tk.Label(main_frame, text=":", font=("Segoe UI", 11), bg=BG_COLOR, fg=TEXT_COLOR)\
    .grid(row=2, column=2, sticky="w")
tk.Entry(main_frame, textvariable=min_var, width=4, font=("Segoe UI", 11))\
    .grid(row=2, column=3, sticky="w", padx=(5,0))

ttk.Radiobutton(main_frame, text="Once", variable=mode_var, value="Once")\
    .grid(row=3, column=1, sticky="w", pady=5)
ttk.Radiobutton(main_frame, text="Daily", variable=mode_var, value="Daily")\
    .grid(row=3, column=2, sticky="w", pady=5)

# Sound
tk.Label(main_frame, text="Sound:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)\
    .grid(row=4, column=0, sticky="w", pady=5)
tk.Label(main_frame, textvariable=sound_label_var, font=("Segoe UI", 9), anchor="w", bg=BG_COLOR, fg=TEXT_COLOR)\
    .grid(row=4, column=1, columnspan=2, sticky="ew")
ttk.Button(main_frame, text="Choose Sound", command=lambda: choose_sound_file())\
    .grid(row=4, column=3, pady=5)

# Functions
def choose_sound_file():
    global sound_path
    p = filedialog.askopenfilename(title="Choose sound", filetypes=[("Audio files", "*.wav *.mp3")])
    if p:
        sound_path = p
        sound_label_var.set(os.path.basename(sound_path))
        settings['sound_path'] = sound_path
        save_settings(settings)

def start_clicked():
    global _scheduler_thread
    try:
        h = int(hour_var.get())
        m = int(min_var.get())
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError()
    except ValueError:
        messagebox.showerror("Invalid time", "Enter valid hour (0-23) and minute (0-59).")
        return
    set_next_alarm(h, m, mode_var.get())
    messagebox.showinfo("Notification set", f"Set for {alarm_time.strftime('%Y-%m-%d %H:%M')}")
    if _scheduler_thread is None or not _scheduler_thread.is_alive():
        _scheduler_stop.clear()
        _scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        _scheduler_thread.start()

def pause_clicked():
    _scheduler_stop.set()
    stop_sound()
    messagebox.showinfo("Paused", "Notifications paused.")

def snooze_clicked():
    global snooze_until
    snooze_until = datetime.now() + timedelta(minutes=5)
    stop_sound()
    messagebox.showinfo("Snoozed", "Snoozed for 5 minutes.")

def test_clicked():
    threading.Thread(target=play_sound_loop, args=(sound_path,), daemon=True).start()
    root.event_generate("<<ShowPopup>>", when="tail")

# Buttons
button_frame = tk.Frame(main_frame, bg=BG_COLOR)
button_frame.grid(row=5, column=0, columnspan=4, pady=15)

for i, (text, cmd) in enumerate([
    ("Start", start_clicked),
    ("Pause", pause_clicked),
    ("Snooze 5m", snooze_clicked),
    ("Test Sound", test_clicked)
]):
    ttk.Button(button_frame, text=text, command=cmd, width=12).grid(row=0, column=i, padx=5)

def on_close():
    settings['sound_path'] = sound_path
    save_settings(settings)
    stop_sound()
    _scheduler_stop.set()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Popup
def show_popup_window(event=None):
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)
    PW, PH = 420, 160
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - PW) // 2
    y = (sh - PH) // 2
    popup.geometry(f"{PW}x{PH}+{x}+{y}")
    c = tk.Canvas(popup, width=PW, height=PH, highlightthickness=0, bg=BG_COLOR)
    c.pack(fill="both", expand=True)
    c.create_text(PW//2, 36, text=title_var.get(), font=("Segoe UI", 14, "bold"), fill=TEXT_COLOR)
    c.create_text(PW//2, 80, text=msg_var.get(), font=("Segoe UI", 12), fill=TEXT_COLOR, width=PW-40)
    def stop_and_close():
        stop_sound()
        try:
            popup.destroy()
        except:
            pass
    btn = ttk.Button(popup, text="Stop", command=stop_and_close)
    c.create_window(PW//2, PH-36, window=btn, width=120, height=36)
    c.bind("<Button-1>", lambda e: stop_and_close())

root.bind("<<ShowPopup>>", show_popup_window)

root.mainloop()
