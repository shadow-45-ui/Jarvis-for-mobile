#!/usr/bin/env python3
"""Local JARVIS assistant for Android/Termux.

Designed for Qwen GGUF models through llama.cpp's `llama-cli` executable.
Conversation/session data stays in a local JSONL file unless the user chooses
another storage location.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = Path(os.path.expanduser("~/.jarvis.env"))
DATA_DIR = Path(os.path.expanduser(os.getenv("JARVIS_DATA_DIR", "~/.jarvis")))
SESSIONS_DIR = DATA_DIR / "sessions"
CURRENT_SESSION = DATA_DIR / "current_session.jsonl"

SYSTEM_PROMPT = os.getenv(
    "JARVIS_SYSTEM_PROMPT",
    "You are JARVIS, a concise, helpful local AI assistant. "
    "Answer clearly. Do not claim to have performed actions you did not perform.",
)


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        os.environ.setdefault(key, os.path.expanduser(value))


load_env_file()

MODEL = Path(os.path.expanduser(os.getenv(
    "JARVIS_MODEL",
    "~/storage/shared/Jarvis/models/Qwen3-4B-Q5_K_M.gguf",
)))
LLAMA_CLI = os.getenv("LLAMA_CLI", "llama-cli")
N_CTX = os.getenv("N_CTX", "4096")
N_THREADS = os.getenv("N_THREADS", "4")
MAX_TOKENS = os.getenv("MAX_TOKENS", "512")
TEMPERATURE = os.getenv("TEMPERATURE", "0.7")
TTS_BACKEND = os.getenv("TTS_BACKEND", "termux").lower()
PIPER_BIN = os.path.expanduser(os.getenv("PIPER_BIN", "piper"))
PIPER_MODEL = os.path.expanduser(os.getenv("PIPER_MODEL", ""))
MEDIA_PLAYER = os.getenv("MEDIA_PLAYER", "termux-media-player")


def ensure_dirs() -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def append_message(role: str, content: str) -> None:
    ensure_dirs()
    with CURRENT_SESSION.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"time": now(), "role": role, "content": content}, ensure_ascii=False) + "\n")


def read_messages() -> list[dict]:
    if not CURRENT_SESSION.exists():
        return []
    messages = []
    for line in CURRENT_SESSION.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            if item.get("role") in {"user", "assistant", "system"}:
                messages.append(item)
        except json.JSONDecodeError:
            continue
    return messages


def build_prompt(user_text: str) -> str:
    messages = read_messages()
    # Keep the prompt bounded so old sessions do not grow without limit.
    recent = messages[-20:]
    parts = [f"System: {SYSTEM_PROMPT}"]
    for item in recent:
        label = item["role"].capitalize()
        parts.append(f"{label}: {item['content']}")
    parts.append(f"User: {user_text}")
    parts.append("Assistant:")
    return "\n\n".join(parts)


def run_model(prompt: str) -> str:
    if not MODEL.exists():
        raise FileNotFoundError(f"Model not found: {MODEL}")

    cmd = [
        LLAMA_CLI,
        "-m", str(MODEL),
        "-c", N_CTX,
        "-t", N_THREADS,
        "-n", MAX_TOKENS,
        "--temp", TEMPERATURE,
        "-p", prompt,
    ]

    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        details = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(details or f"llama-cli exited with code {proc.returncode}")

    output = (proc.stdout or "").strip()
    # llama-cli may emit logging lines; keep the response usable without
    # assuming a particular llama.cpp build's exact logging format.
    return output


def speak(text: str) -> None:
    if TTS_BACKEND in {"off", "none", "false"}:
        return

    if TTS_BACKEND == "termux":
        try:
            subprocess.run(["termux-tts-speak", text], check=False)
        except FileNotFoundError:
            print("[Voice unavailable: termux-tts-speak not found]")
        return

    if TTS_BACKEND == "piper":
        if not PIPER_MODEL:
            print("[Piper is selected but PIPER_MODEL is not configured]")
            return
        wav = DATA_DIR / "jarvis_reply.wav"
        try:
            piper = subprocess.Popen(
                [PIPER_BIN, "--model", PIPER_MODEL, "--output_file", str(wav)],
                stdin=subprocess.PIPE,
                text=True,
            )
            piper.communicate(text)
            if piper.returncode != 0:
                print("[Piper failed]")
                return
            subprocess.run([MEDIA_PLAYER, "play", str(wav)], check=False)
        except FileNotFoundError as exc:
            print(f"[Voice component missing: {exc}]")
        return

    print(f"[Unknown TTS_BACKEND={TTS_BACKEND!r}; voice skipped]")


def save_session() -> None:
    ensure_dirs()
    if not CURRENT_SESSION.exists() or CURRENT_SESSION.stat().st_size == 0:
        print("No current session to save.")
        return
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    target = SESSIONS_DIR / f"session_{stamp}.jsonl"
    target.write_text(CURRENT_SESSION.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Saved: {target}")


def new_session() -> None:
    if CURRENT_SESSION.exists():
        save_session()
    CURRENT_SESSION.unlink(missing_ok=True)
    print("Started a new JARVIS session.")


def show_history() -> None:
    ensure_dirs()
    files = sorted(SESSIONS_DIR.glob("session_*.jsonl"))
    if not files:
        print("No saved sessions.")
        return
    for f in files:
        print(f"- {f.name} ({f.stat().st_size} bytes)")


def show_status() -> None:
    print(f"Model: {MODEL}")
    print(f"Model exists: {MODEL.exists()}")
    print(f"llama-cli: {LLAMA_CLI}")
    print(f"TTS backend: {TTS_BACKEND}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Current session: {CURRENT_SESSION}")


def clear_data() -> None:
    answer = input("Delete saved JARVIS sessions from this app? Type DELETE to confirm: ").strip()
    if answer != "DELETE":
        print("Cancelled.")
        return
    for f in SESSIONS_DIR.glob("session_*.jsonl"):
        f.unlink(missing_ok=True)
    CURRENT_SESSION.unlink(missing_ok=True)
    print("JARVIS session data deleted. Model files were not touched.")


def handle_command(text: str) -> bool:
    cmd = text.strip().lower()
    if cmd in {"/exit", "/quit", "/q"}:
        save_session()
        print("Goodbye.")
        return True
    if cmd == "/help":
        print("/new  /save  /history  /status  /voice on  /voice off  /clear  /exit")
        return False
    if cmd == "/new":
        new_session(); return False
    if cmd == "/save":
        save_session(); return False
    if cmd == "/history":
        show_history(); return False
    if cmd == "/status":
        show_status(); return False
    if cmd == "/clear":
        clear_data(); return False
    if cmd == "/voice on":
        os.environ["TTS_BACKEND"] = "termux"
        global TTS_BACKEND
        TTS_BACKEND = "termux"
        print("Voice enabled: Termux TTS")
        return False
    if cmd == "/voice off":
        TTS_BACKEND = "off"
        print("Voice disabled.")
        return False
    return False


def main() -> int:
    ensure_dirs()
    print("JARVIS — local mode")
    print("Type /help for commands. Ctrl+C also exits safely.")
    show_status()

    while True:
        try:
            user_text = input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting JARVIS.")
            save_session()
            return 0

        if not user_text:
            continue
        if user_text.startswith("/"):
            if handle_command(user_text):
                return 0
            continue

        append_message("user", user_text)
        try:
            response = run_model(build_prompt(user_text))
        except Exception as exc:
            print(f"\n[JARVIS error] {exc}")
            continue

        if not response:
            print("\n[JARVIS] No response returned by llama.cpp.")
            continue

        append_message("assistant", response)
        print(f"\nJARVIS > {response}")
        speak(response)


if __name__ == "__main__":
    raise SystemExit(main())
