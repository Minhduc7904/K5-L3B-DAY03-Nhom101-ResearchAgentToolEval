# Research Agent — Web UI (CP5)

React + Vite + shadcn/ui chat front end for the agent. The backend is `../server.py`
(FastAPI), which reuses the tool loop from `chat.py` and writes one
`transcripts/*_web_*.transcript.json` per browser session.

## Run (from `starter_v0/`)

```bash
pip install -r requirements.txt
(cd web && npm install && npm run build)          # builds web/dist
python server.py --provider gemini --version v3    # → http://localhost:8000
```

`server.py` serves the built UI and the API on one port, so a single tunnel is enough:

```bash
cloudflared tunnel --url http://localhost:8000
```

## Develop with hot reload

```bash
python server.py --provider gemini --version v3    # API on :8000
cd web && npm run dev                              # UI on :5173, proxies /api → :8000
```

Example prompts on the empty screen live in `EXAMPLES` in `src/App.tsx` — keep them in sync with A3 of the group report.
