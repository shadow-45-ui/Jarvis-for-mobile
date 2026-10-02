#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

DATA_DIR="${JARVIS_DATA_DIR:-$HOME/.jarvis}"

printf 'This will delete JARVIS session data under: %s\n' "$DATA_DIR"
printf 'It will NOT delete your GGUF model or unrelated Termux data.\n'
printf 'Type DELETE to continue: '
read -r answer

if [ "$answer" != "DELETE" ]; then
  echo 'Cancelled.'
  exit 0
fi

rm -rf -- "$DATA_DIR"
echo 'JARVIS local session data deleted.'
