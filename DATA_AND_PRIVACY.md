# Data and privacy

## What stays local

The default JARVIS architecture keeps these items on the device:

- conversation/session JSONL files
- model path/configuration
- optional Piper voice model
- generated temporary WAV output

The local Qwen model runs through llama.cpp on the device.

## What is not included in Git

`.gitignore` excludes:

- model weights (`*.gguf`)
- voice models (`*.onnx`)
- session logs (`*.jsonl`)
- WAV files
- local environment files

This prevents accidentally publishing large or personal files.

## Deleting data

The supported cleanup command is:

```bash
bash scripts/delete_local_data.sh
```

It targets the JARVIS data directory only. It does not delete the model or unrelated Android/Termux files.
