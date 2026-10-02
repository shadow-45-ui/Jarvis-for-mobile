#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

pkg update
pkg install -y python git ffmpeg

mkdir -p "$HOME/storage/shared/Jarvis/models"
mkdir -p "$HOME/.jarvis/sessions"

if [ ! -f "$HOME/.jarvis.env" ]; then
  cat > "$HOME/.jarvis.env" <<'ENV'
JARVIS_MODEL=~/storage/shared/Jarvis/models/Qwen3-4B-Q5_K_M.gguf
LLAMA_CLI=llama-cli
N_CTX=4096
N_THREADS=4
MAX_TOKENS=512
TEMPERATURE=0.7
TTS_BACKEND=termux
PIPER_BIN=piper
PIPER_MODEL=
MEDIA_PLAYER=termux-media-player
ENV
fi

echo
 echo 'Base Termux setup complete.'
echo 'Next: install/configure llama.cpp, place your GGUF model in ~/storage/shared/Jarvis/models/, test TTS, then run: python jarvis.py'
