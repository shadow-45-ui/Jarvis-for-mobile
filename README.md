# JARVIS — Local Android/Termux AI Assistant

A phone-first, local AI assistant built around **Qwen3-4B + llama.cpp**, with optional voice output, session memory, and Termux integration.

> This repository contains the software/configuration only. The GGUF model itself is **not** stored in Git because it is several GB.

## Architecture

```text
User
  │
  ├── text ───────────────┐
  │                        ▼
  │                   jarvis.py
  │                        │
  │                llama.cpp / Qwen3-4B
  │                        │
  │                  local response
  │                        │
  │        ┌───────────────┴───────────────┐
  │        ▼                               ▼
  │   session memory                 voice output
  │   data/sessions/                 Termux TTS
  │                                    or Piper
  │
  └── future UI/app bridge
```

## What is included

- `jarvis.py` — main assistant loop
- Local Qwen GGUF inference through `llama-cli`
- Persistent JSONL session memory
- `/save`, `/new`, `/history`, `/clear`, `/status`, `/voice`, `/exit` commands
- Android Termux TTS output
- Optional Piper WAV output
- Safe local configuration through environment variables
- Setup scripts for Termux
- Storage/data cleanup script
- No cloud API key required for the local model path

## Requirements

- Android + Termux
- Python 3
- `llama-cli` from llama.cpp
- A compatible Qwen3 GGUF model
- Enough storage/RAM for the chosen quantization
- Optional: Piper for local neural TTS

The project was designed around a Qwen3-4B Q5_K_M GGUF model. A model file is intentionally not included in this repository.

## Quick start

```bash
pkg update
pkg install python git ffmpeg
```

Install/configure llama.cpp according to your existing Termux setup, then place the model at:

```text
~/storage/shared/Jarvis/models/Qwen3-4B-Q5_K_M.gguf
```

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd jarvis
```

Create local configuration:

```bash
cp config/jarvis.env.example ~/.jarvis.env
nano ~/.jarvis.env
```

Then run:

```bash
python jarvis.py
```

## Commands inside JARVIS

| Command | Purpose |
|---|---|
| `/help` | Show commands |
| `/new` | Start a fresh session |
| `/save` | Save current session |
| `/history` | Show saved sessions |
| `/status` | Show local configuration/status |
| `/voice on` | Enable speech |
| `/voice off` | Disable speech |
| `/clear` | Delete saved JARVIS sessions after confirmation |
| `/exit` | Exit JARVIS |

Normal text is sent to the local model. Nothing needs to leave the phone for inference.

## Data and privacy

By default, sessions are stored locally under:

```text
~/.jarvis/sessions/
```

The model is local. The repository does not contain your conversations, model weights, or personal configuration.

If you want to remove JARVIS's locally saved sessions:

```bash
bash scripts/delete_local_data.sh
```

The script only targets this project's JARVIS data directory; it does **not** wipe Android storage or unrelated Termux files.

## Voice

### Android/Termux TTS

The simplest voice path uses Termux's Android TTS interface. Test it with:

```bash
termux-tts-speak "Hello, I am Jarvis."
```

If that works, set:

```text
TTS_BACKEND=termux
```

### Piper

For a fully local neural voice, configure Piper and set:

```text
TTS_BACKEND=piper
PIPER_BIN=/path/to/piper
PIPER_MODEL=/path/to/voice.onnx
```

JARVIS can create a WAV and optionally play it through `termux-media-player`.

## Model configuration

The defaults are intentionally conservative. Edit `~/.jarvis.env` rather than hard-coding device-specific paths into Git.

Important variables:

```text
JARVIS_MODEL=~/storage/shared/Jarvis/models/Qwen3-4B-Q5_K_M.gguf
LLAMA_CLI=llama-cli
N_CTX=4096
N_THREADS=4
MAX_TOKENS=512
TEMPERATURE=0.7
```

Adjust thread/context values to match the phone. More context and more threads can increase memory/heat usage.

## Offline behavior

Once the model, llama.cpp executable, Python code, and chosen local voice components are installed, text generation does not require an internet connection.

Android/Termux TTS may use Android's installed speech engine and its own language/voice resources. Piper is the more self-contained option when its model and binary are stored locally.

## Repository rules

Never commit:

- `.env` files containing secrets
- Personal chat logs
- Private tokens/API keys
- Large GGUF model files
- Private voice/model files unless you have redistribution rights

See `.gitignore` for the defaults.

## Roadmap

- [x] Local Qwen + llama.cpp command loop
- [x] Session memory
- [x] Termux TTS
- [x] Optional Piper backend
- [x] Safe local cleanup
- [ ] Mic input bridge
- [ ] Android UI bridge
- [ ] Tool/plugin system
- [ ] Better long-term memory
- [ ] Wake-word/always-listening mode

## License

MIT. See `LICENSE`.
