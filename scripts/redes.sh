#!/bin/sh
# Corre la publicación de redes de Ausel con Claude Code sin pantalla. Lo llama cron en la TV box.
cd "$(dirname "$0")/.." || exit 1
git pull -q
export MUSICA_DIR=/root/musica  # temas de Kevin MacLeod descargados por scripts/musica_descargar.py
date
claude -p "$(cat automatizacion/redes-prompt.md)" \
  --permission-mode dontAsk \
  --allowedTools "Bash(git *)" "Bash(gh *)" "Bash(python *)" "Bash(python3 *)" "Bash(curl *)" "Bash(ls *)" "Read" "Write" "Edit" "Glob" "Grep" "mcp__claude_ai_Composio"
