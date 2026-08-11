# FRIDAY

Full-stack holographic voice-AI orb — FastAPI + Groq + Three.js/HTML/CSS/JS frontend.

## What's in it (the "wow" stuff)
- **Boot sequence** — terminal-style startup lines + progress bar before the core reveals itself
- **3D golden energy orb** (Three.js) — faceted core, 10 crossing wireframe rings, 700 ember particles, layered bloom glow
- **Holographic HUD** — corner brackets, scanline sweep, CRT scanlines, film-grain noise, vignette, rotating dial rings, live clock
- **Holographic grid floor** with perspective + scroll animation
- **Live audio waveform** — 40 reactive bars driven by your actual mic input (Web Audio API), which also feeds the orb's glow intensity in real time
- **Typewriter response text** + text-to-speech playback
- **Conversation memory** — backend remembers the last few exchanges per session
- **Hinglish or English** voice input toggle

## Structure
```
golden_core/
├── start.sh                 # one-command launcher (mac/linux)
├── backend/
│   ├── main.py               # FastAPI + Groq + session memory
│   └── requirements.txt
└── frontend/
    └── index.html            # everything visual — served by FastAPI
```

## Run it

**Option A — one command (mac/linux):**
```bash
export GROQ_API_KEY="your-key-here"
chmod +x start.sh
./start.sh
```

**Option B — manual (any OS):**
```bash
cd backend
pip install -r requirements.txt
export GROQ_API_KEY="your-key-here"      # Windows: set GROQ_API_KEY=your-key-here
uvicorn main:app --reload --port 8000
```

Then open `http://localhost:8000` in Chrome (recommended for mic + voice support).

## Replit

This repo includes a `.replit` file that runs `bash start.sh`.

After importing the GitHub repo into Replit, add `GROQ_API_KEY` in Replit Secrets, then run the project.

## Free, easy AI setup

This project uses Groq's developer API by default. Create an API key at
[Groq Console](https://console.groq.com/keys), set `GROQ_API_KEY`, and run the
launcher above. The browser never receives your key: it only calls the local
FastAPI backend. Groq has an OpenAI-compatible API and provides developer-tier
rate limits; check its console for the current free-tier allowance.

## How it flows
1. Boot animation plays, core spins up.
2. Tap the mic → orb goes **LISTENING**, waveform bars react to your voice.
3. Speech-to-text (browser) sends your question to the Python backend.
4. Backend calls Groq, keeps last 8 turns of memory per session, returns the answer.
5. Orb goes **SPEAKING**, response types itself out, and the browser reads it aloud.

## Extending it
- Backend is where you'd plug in your own model (your Qwen2.5-Coder / DevCrew setup), RAG, or a wake word ("Hey Groot") detector.
- All visual tuning (ring count, particle density, colors, glow) lives in the `initThree()` function in `frontend/index.html`.
