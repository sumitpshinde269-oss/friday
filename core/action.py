"""All non-LLM actions Friday can perform."""
import os, re, platform, webbrowser, subprocess, threading, random
from datetime import datetime
import pyautogui
import requests

SYSTEM = platform.system().lower()

# ---------- time / date ---------- #
def get_time():  return datetime.now().strftime("It's %I:%M %p.")
def get_date():  return datetime.now().strftime("Today is %A, %B %d, %Y.")

# ---------- system audio ---------- #
def volume(direction: str):
    d = direction.lower()
    if SYSTEM == "linux":
        if d == "up":   subprocess.Popen(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"])
        if d == "down": subprocess.Popen(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-10%"])
        if d == "mute": subprocess.Popen(["pactl", "set-sink-mute",  "@DEFAULT_SINK@", "toggle"])
    elif SYSTEM == "windows":
        if d == "up":   pyautogui.press("volumeup")
        if d == "down": pyautogui.press("volumedown")
        if d == "mute": pyautogui.press("volumemute")
    elif SYSTEM == "darwin":
        script = {
            "up":   'set volume output volume (output volume of (get volume settings)) + 10',
            "down": 'set volume output volume (output volume of (get volume settings)) - 10',
            "mute": 'set volume with output muted',
        }[d]
        subprocess.Popen(["osascript", "-e", script])
    return f"Volume {d}."

# ---------- power / screen ---------- #
def screenshot(path="screenshot.png"):
    pyautogui.screenshot(path)
    return f"Screenshot saved → {os.path.abspath(path)}"

def shutdown():
    speak = "I am a web instance — power actions are no-ops."
    if SYSTEM == "linux":   subprocess.Popen(["shutdown", "-h", "+1"])
    elif SYSTEM == "windows": subprocess.Popen(["shutdown", "/s", "/t", "60"])
    elif SYSTEM == "darwin":  subprocess.Popen(["shutdown", "-h", "+1"])
    return "Shutting down in 1 minute."

def restart():
    if SYSTEM == "linux":   subprocess.Popen(["reboot"])
    elif SYSTEM == "windows": subprocess.Popen(["shutdown", "/r", "/t", "0"])
    elif SYSTEM == "darwin":  subprocess.Popen(["shutdown", "-r", "now"])
    return "Restarting."

def lock():
    if SYSTEM == "linux":   subprocess.Popen(["loginctl", "lock-session"])
    elif SYSTEM == "windows": subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
    elif SYSTEM == "darwin":  subprocess.Popen(["pmset", "displaysleepnow"])
    return "Screen locked."

# ---------- apps / web ---------- #
def open_app(name: str):
    n = name.lower().strip()
    table = {
        "chrome":   (["google-chrome"],          ["open", "-a", "Google Chrome"]),
        "firefox":  (["firefox"],                ["open", "-a", "Firefox"]),
        "code":     (["code"],                   ["open", "-a", "Visual Studio Code"]),
        "vscode":   (["code"],                   ["open", "-a", "Visual Studio Code"]),
        "spotify":  (["spotify"],                ["open", "-a", "Spotify"]),
        "discord":  (["discord"],                ["open", "-a", "Discord"]),
        "terminal": (["gnome-terminal", "konsole", "xterm", "wt"],
                     ["open", "-a", "Terminal"]),
        "files":    (["nautilus", "thunar", "explorer"],
                     ["open", "-a", "Finder"]),
        "calc":     (["gnome-calculator", "calc"],
                     ["open", "-a", "Calculator"]),
    }
    for key in table:
        if key in n:
            cmds = table[key][0] if SYSTEM == "linux" else table[key][1]
            for c in cmds:
                try:    subprocess.Popen(c if isinstance(c, list) else [c]); return f"Opening {key}."
                except FileNotFoundError: continue
            return f"{key} not installed."
    try: subprocess.Popen([n]); return f"Opening {n}."
    except Exception as e: return f"Could not open {name}: {e}"

def open_url(target: str):
    if not target.startswith("http"):
        target = "https://" + target
    webbrowser.open(target)
    return f"Opening {target}."

def search_google(q: str):
    webbrowser.open("https://www.google.com/search?q=" + requests.utils.quote(q))
    return f"Searching Google for {q}."

def search_youtube(q: str):
    webbrowser.open("https://www.youtube.com/results?search_query=" + requests.utils.quote(q))
    return f"Searching YouTube for {q}."

# ---------- jokes ---------- #
JOKES = [
    "Why don't scientists trust atoms? They make up everything.",
    "I told my computer I needed a break — it said 'no problem, I'll go to sleep.'",
    "Why was the JavaScript developer sad? Because he didn't Node how to Express himself.",
    "There are 10 kinds of people: those who understand binary, and those who don't.",
    "Why did the developer go broke? He used up all his cache.",
]
def joke(): return random.choice(JOKES)

# ---------- weather ---------- #
def weather(city: str = "auto"):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=10)
        r.raise_for_status()
        d = r.json()
        cur  = d["current_condition"][0]
        area = d.get("nearest_area", [{}])[0]
        loc  = area.get("areaName", [{}])[0].get("value", "your area")
        return (f"In {loc}: {cur['weatherDesc'][0]['value']}, "
                f"{cur['temp_C']}°C, feels like {cur['FeelsLikeC']}°C, "
                f"humidity {cur['humidity']}%.")
    except Exception as e:
        return f"Weather unavailable: {e}"

# ---------- math ---------- #
_MATH_RE = re.compile(r"^[\d\s\.\+\-\*\/\(\)\%]+$")
def calc(expr: str):
    if _MATH_RE.match(expr):
        try: return f"That equals {eval(expr, {'__builtins__': {}}, {})}."
        except Exception: pass
    return None

# ---------- timer ---------- #
def set_timer(seconds: int, label="Timer"):
    def done(): print(f"[timer] {label} done")
    t = threading.Timer(seconds, done); t.daemon = True; t.start()
    return f"Timer set for {seconds} seconds."

# ---------- master router ---------- #
def handle(text: str):
    t = text.lower()
    if re.search(r"\btime\b", t):                     return get_time()
    if "date" in t or "day is it" in t:              return get_date()
    if "volume up"   in t or "louder"   in t:         return volume("up")
    if "volume down" in t or "quieter"  in t:         return volume("down")
    if "mute"        in t:                            return volume("mute")
    if "screenshot"  in t:                            return screenshot()
    if "cancel shutdown" in t:                        return "Shutdown cancelled."
    if "shutdown"    in t or "shut down" in t:        return shutdown()
    if "restart"     in t or "reboot"   in t:         return restart()
    if "lock"        in t and "screen"  in t:         return lock()
    m = re.search(r"open (.+)", t)
    if m:
        tgt = m.group(1).strip()
        if "." in tgt and " " not in tgt: return open_url(tgt)
        return open_app(tgt)
    m = re.search(r"(?:search (?:for )?|google) (.+)", t)
    if m: return search_google(m.group(1))
    if t.startswith("play "): return search_youtube(t[5:])
    if "joke" in t or "laugh" in t: return joke()
    if "weather" in t:
        m = re.search(r"weather(?:\s+(?:in|at|for)\s+([\w\s,]+))?", t)
        return weather(m.group(1).strip() if (m and m.group(1)) else "auto")
    m = re.search(r"(?:set a )?timer (?:for )?(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)?", t)
    if m:
        n = int(m.group(1)); u = (m.group(2) or "seconds").lower()
        if u.startswith("min"): n *= 60
        elif u.startswith("h"):  n *= 3600
        return set_timer(n)
    m = re.search(r"(?:calculate|what(?:'s| is)?|compute)\s+([\d\.\+\-\*\/\(\)\%]+)", t)
    if m:
        r = calc(m.group(1));
        if r: return r
    return None

ACTIONS = {"handle": handle}
