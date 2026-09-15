import requests, json
from . import actions

OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "llama3"   # or llama3.1, mistral, phi3, gemma2, etc.
SYSTEM = (
    "You are Friday, a concise local AI voice assistant. "
    "Reply in 1-3 short spoken sentences. No markdown, lists, code fences, or emojis."
)

def ask_ollama(prompt: str) -> str:
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt,
                  "system": SYSTEM, "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "I can't reach Ollama. Run:  ollama serve   and   ollama pull llama3"
    except Exception as e:
        return f"Ollama error: {e}"

def ask_friday(text: str) -> str:
    local = actions.handle(text)
    return local if local else ask_ollama(text)

def stream_friday(text: str):
    """Server-Sent-Events style generator."""
    local = actions.handle(text)
    if local:
        yield local
        return
    try:
        with requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": text,
                  "system": SYSTEM, "stream": True},
            stream=True, timeout=300,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line: continue
                chunk = json.loads(line).get("response", "")
                if chunk: yield chunk
    except requests.exceptions.ConnectionError:
        yield "I can't reach Ollama on port 11434."
    except Exception as e:
        yield f"Ollama error: {e}"
