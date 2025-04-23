# disable the activate script’s own prompt prefix
export VIRTUAL_ENV_DISABLE_PROMPT=1

# auto‑activate our AI Cover Letter venv once per shell
if [ -z "$VIRTUAL_ENV" ] && [ -f "$HOME/DEV/ai_cover_letter/.venv/bin/activate" ]; then
  source "$HOME/DEV/ai_cover_letter/.venv/bin/activate"
fi
