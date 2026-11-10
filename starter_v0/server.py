"""HTTP backend for the web chat UI (CP5).

Wraps the same model/tool loop as chat.py and writes one transcript JSON per
browser session into transcripts/, so live UI chats count as evidence too.

Run (from starter_v0/):
    python server.py --provider gemini --version v3
Then open http://localhost:8000 (after `npm run build` in web/), or run
`npm run dev` in web/ for hot reload on http://localhost:5173.
"""
from __future__ import annotations

import argparse
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

WEB_DIST = ROOT / "web" / "dist"


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(min_length=1, max_length=8000)


class Session:
    def __init__(self, session_id: str, path: Path, transcript: dict[str, Any]) -> None:
        self.id = session_id
        self.path = path
        self.transcript = transcript
        self.history: list[dict[str, str]] = []
        self.lock = threading.Lock()


def create_app(args: argparse.Namespace) -> FastAPI:
    system_prompt = args.system_prompt.read_text(encoding="utf-8")
    openai_tools = to_openai_tools(load_tool_declarations(args.tools))
    provider = make_provider(args.provider)
    model = args.model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(args.version, args.system_prompt, args.tools)
    sessions: dict[str, Session] = {}
    sessions_lock = threading.Lock()

    def new_session() -> Session:
        session_id = uuid.uuid4().hex[:12]
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([safe_slug(args.version), safe_slug(args.provider), "web", timestamp])
        transcript: dict[str, Any] = {
            "transcript_id": transcript_id,
            **artifact_version_dict(artifact_version),
            "provider": args.provider,
            "model": model,
            "source": "web_ui",
            "system_prompt": str(args.system_prompt),
            "tools": str(args.tools),
            "history_window": args.history_window,
            "max_tool_rounds": args.max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
        session = Session(session_id, args.transcripts_dir / f"{transcript_id}.transcript.json", transcript)
        with sessions_lock:
            sessions[session_id] = session
        return session

    app = FastAPI(title="Research Agent UI")

    @app.get("/api/info")
    def info() -> dict[str, Any]:
        return {
            "provider": args.provider,
            "model": model,
            "artifact_version": artifact_version.artifact_version,
        }

    @app.post("/api/chat")
    def chat(req: ChatRequest) -> dict[str, Any]:
        text = req.message.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Empty message")
        session = sessions.get(req.session_id or "") or new_session()

        with session.lock:
            turn: dict[str, Any] = {
                "turn_index": len(session.transcript["turns"]) + 1,
                "started_at": now_iso(),
                "user": text,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }
            messages = [
                {"role": "system", "content": system_prompt},
                *trim_history(session.history, args.history_window),
                {"role": "user", "content": text},
            ]
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=args.model,
                    max_tool_rounds=args.max_tool_rounds,
                )
                turn.update(result)
                session.history.append({"role": "user", "content": text})
                session.history.append({"role": "assistant", "content": result["assistant_text"]})
            except Exception as exc:  # surface provider errors to the UI, keep them in the transcript
                turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})

            turn["ended_at"] = now_iso()
            session.transcript["turns"].append(turn)
            write_transcript(session.path, session.transcript)

        return {
            "session_id": session.id,
            "status": turn["status"],
            "assistant_text": turn.get("assistant_text") or "",
            "error": turn.get("error"),
            "tool_calls": [
                {
                    "name": event.get("tool"),
                    "args": event.get("args", {}),
                    "error": isinstance(event.get("result"), dict) and "error" in event["result"],
                }
                for event in turn.get("tool_events", [])
            ],
        }

    if WEB_DIST.exists():
        app.mount("/assets", StaticFiles(directory=WEB_DIST / "assets"), name="assets")

        @app.get("/{path:path}")
        def spa(path: str) -> FileResponse:
            file = WEB_DIST / path
            if path and file.is_file() and WEB_DIST in file.resolve().parents:
                return FileResponse(file)
            return FileResponse(WEB_DIST / "index.html")

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Web UI backend for the Research Agent.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini", "ollama"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True, help="Artifact version label, e.g. v3.")
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(create_app(args), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
