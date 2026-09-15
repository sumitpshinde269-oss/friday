#!/usr/bin/env python3
"""Friday — local web UI + REST API."""
from flask import Flask, render_template, request, jsonify, Response
from core import ask_friday, stream_friday
import logging, traceback

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
app = Flask(__name__, static_folder="core/static", template_folder="core/static/templates")

@app.get("/")
def index(): return render_template("index.html")

@app.get("/health")
def health():
    return jsonify(status="ok", assistant="Friday",
                   ollama_url="http://localhost:11434")

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    text = (data.get("message") or "").strip()
    if not text: return jsonify(error="empty message"), 400
    try:
        return jsonify(reply=ask_friday(text))
    except Exception:
        traceback.print_exc()
        return jsonify(error="internal error"), 500

@app.post("/api/stream")
def stream():
    data = request.get_json(silent=True) or {}
    text = (data.get("message") or "").strip()
    if not text: return jsonify(error="empty message"), 400
    def gen():
        for token in stream_friday(text):
            yield token.replace("\n", " ")
    return Response(gen(), mimetype="text/plain")

if __name__ == "__main__":
    print("🟢  Friday UI → http://localhost:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
