const chat    = document.getElementById("chat");
const input   = document.getElementById("input");
const form    = document.getElementById("composer");
const micBtn  = document.getElementById("micBtn");
const dot     = document.getElementById("dot");
const status  = document.getElementById("statusText");

const setStatus = (cls, text) => {
  dot.className = "dot " + cls;
  status.textContent = text;
};

const addMsg = (role, text) => {
  const wrap = document.createElement("div");
  wrap.className = "msg " + role;
  wrap.innerHTML =
    `<div class="avatar">${role === "user" ? "U" : "F"}</div>
     <div class="bubble"></div>`;
  wrap.querySelector(".bubble").textContent = text;
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
  return wrap.querySelector(".bubble");
};

// --- text submit --- //
form.addEventListener("submit", async e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  await ask(text);
});

async function ask(text) {
  addMsg("user", text);
  setStatus("thinking", "Thinking…");
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ message: text }),
    });
    const data = await r.json();
    addMsg("friday", data.reply || "(no response)");
    speak(data.reply || "");
    setStatus("idle", "Idle");
  } catch (err) {
    addMsg("friday", "Error: " + err.message);
    setStatus("idle", "Idle");
  }
}

// --- browser TTS --- //
function speak(text) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.rate = 1.05; u.pitch = 1.0;
  const v = speechSynthesis.getVoices().find(v =>
    /female|samantha|zira|google us/i.test(v.name));
  if (v) u.voice = v;
  u.onstart  = () => setStatus("speaking", "Speaking…");
  u.onend    = () => setStatus("idle",     "Idle");
  speechSynthesis.speak(u);
}

// --- browser STT (Web Speech API) --- //
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null, recording = false;

if (SR) {
  recognition = new SR();
  recognition.continuous     = false;
  recognition.interimResults = false;
  recognition.lang           = "en-US";

  recognition.onresult = e => {
    const text = e.results[0][0].transcript.trim();
    input.value = text;
    ask(text);
  };
  recognition.onerror  = e => { setStatus("idle", "Mic error: " + e.error); recording = false; micBtn.classList.remove("recording"); };
  recognition.onend    = () => { recording = false; micBtn.classList.remove("recording"); setStatus("idle", "Idle"); };
  recognition.onstart  = () => { setStatus("listening", "Listening…"); };
} else {
  micBtn.title = "Web Speech API not supported — use Chrome/Edge over HTTPS or localhost";
}

micBtn.addEventListener("click", () => {
  if (!recognition) return alert("Voice input not supported in this browser. Use Chrome or Edge.");
  if (recording) { recognition.stop(); return; }
  recording = true;
  micBtn.classList.add("recording");
  recognition.start();
});

// load voices on some browsers
if ("speechSynthesis" in window) speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();
