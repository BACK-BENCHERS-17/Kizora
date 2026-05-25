#!/usr/bin/env bash
# ───── Kizora ─────
set -e

echo ""
echo "╔═══════════════════╗"
echo "         Kizora"
echo "╚═══════════════════╝"
echo ""

# Kill existing processes to avoid 409 Conflict
pkill -f "python3 bot.py" || true
pkill -f "uvicorn c-gpt:app" || true

# Start API server (groq_api is imported within c-gpt)
python3 -m uvicorn c-gpt:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "[~] Waiting for API..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:8000/home > /dev/null 2>&1; then
        echo "[+] API ready."
        break
    fi
    sleep 2
done

echo "[+] Starting bot..."
# Use exec to replace the shell process with the bot process
exec python3 bot.py
