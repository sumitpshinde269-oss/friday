import pyttsx3
_engine = pyttsx3.init(); _engine.setProperty("rate", 175)
for v in _engine.getProperty("voices"):
    if "female" in v.name.lower() or "zira" in v.name.lower() or "samantha" in v.name.lower():
        _engine.setProperty("voice", v.id); break

def speak(text: str):
    print(f"Friday ▶ {text}")
    _engine.say(text); _engine.runAndWait()
