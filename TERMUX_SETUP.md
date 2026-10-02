# Termux setup guide

## 1. Prepare storage

Run:

```bash
termux-setup-storage
mkdir -p ~/storage/shared/Jarvis/models
```

The model location used by this repository is:

```text
~/storage/shared/Jarvis/models/Qwen3-4B-Q5_K_M.gguf
```

## 2. Install base packages

```bash
pkg update
pkg install python git ffmpeg
```

## 3. Verify Python

```bash
python --version
```

## 4. Verify Android voice output

```bash
termux-tts-speak "Hello, I am Jarvis."
```

If this command speaks successfully, the Termux TTS backend is ready.

## 5. Install/configure llama.cpp

Use the llama.cpp build you already have working on the device. Verify:

```bash
llama-cli --help
```

If your executable has another name/path, put it in `~/.jarvis.env`:

```text
LLAMA_CLI=/full/path/to/llama-cli
```

## 6. Put the GGUF model in place

Do not put the multi-GB model in GitHub. Put it on the phone instead:

```text
Internal storage/Jarvis/models/Qwen3-4B-Q5_K_M.gguf
```

Then check from Termux:

```bash
ls -lh ~/storage/shared/Jarvis/models/
```

## 7. Clone JARVIS

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd jarvis
```

## 8. Configure

```bash
cp config/jarvis.env.example ~/.jarvis.env
nano ~/.jarvis.env
```

At minimum verify `JARVIS_MODEL` and `LLAMA_CLI`.

## 9. Start

```bash
python jarvis.py
```

## 10. Useful commands

```text
/help
/status
/voice on
/voice off
/save
/history
/new
/clear
/exit
```

## 11. Delete only JARVIS session data

```bash
bash scripts/delete_local_data.sh
```

This does not remove the model.

## 12. About battery, heat, and storage

Local inference is computationally heavy compared with ordinary phone apps. Long sessions can increase CPU use, temperature, and battery drain. Keep the context/token settings reasonable and let the phone cool if it becomes hot.

The GGUF model consumes storage, but using JARVIS repeatedly does not inherently wear out the phone's storage in a special way. Session logs do create writes, which is why the repository keeps them bounded to JSONL session files and provides a cleanup command.
