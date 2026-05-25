"""
╔══════════════════════════╗
                Kizora
╚══════════════════════════╝

     @Groq—API—File
  
  Read @licence File  And @README.md
  
  Dev: https://t.me/xD3VS
  Updates: https://t.me/BotXCore
  Support: https://t.me/BotXCore
  Donate: https://t.me/BotXCore
"""

import time
import threading
import requests
import config

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

_GF_SYSTEM_PROMPT = (
    "You are Kizora, an advanced and expert AI assistant. Your developer is @xD3VS.\n"
    "You are helpful, professional, and knowledgeable. You are NOT a girlfriend.\n"
    "The current user's name is {first_name}, their username is @{username}, and their Telegram ID is {uid}.\n"
    "If the user asks who they are, what is their ID, or what is their username, answer them correctly using the provided info.\n"
    "If the user asks about you, tell them you are Kizora, an advanced AI developed by @xD3VS.\n"
    "Reply STRICTLY in HTML format only (use <b>bold</b>, <i>italic</i>, <code>code</code>, <pre>pre</pre> tags).\n"
    "Do NOT use markdown (no **, no ##, no ```, no ---). Use only Telegram-supported HTML tags.\n"
    "Keep replies intelligent, clear, and expert-like."
)


def ask_groq(query: str, uid: int, first_name: str = "User", username: str = "None", model: str = None) -> str:
    model = model or config.GROQ_MODEL
    system_prompt = _GF_SYSTEM_PROMPT.format(
        first_name=first_name or "User",
        uid=uid or "Unknown",
        username=username or "None"
    )
    for key in config.GROQ_API_KEYS:
        try:
            r = requests.post(
                GROQ_API_URL,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": query},
                    ],
                },
                timeout=20,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except Exception:
            continue
    return "Error: All Groq API keys failed."


@app.get("/")
def teamdev(g: str = None, uid: int = None, first_name: str = "User", username: str = "None"):
    if not g:
        return JSONResponse({"error": "Missing query (?g=)"}, status_code=400)
    return {
        "status": "success",
        "query": g,
        "model": config.GROQ_MODEL,
        "response": ask_groq(g, uid=uid, first_name=first_name or "User", username=username or "None"),
    }


@app.get("/model")
def model_info():
    return {"fast": config.GROQ_MODEL, "note": "Groq only. ChatGPT (?c=) is under maintenance."}


@app.get("/ping")
def ping():
    return {"status": "alive", "service": "AI_PROJECT - By @BotXCore", "time": int(time.time())}


# Self-ping to keep Railway service alive
def _self_ping():
    base = config.API_BASE
    if not base:
        return
    while True:
        try:
            requests.get(f"{base}/ping", timeout=10)
        except Exception:
            pass
        time.sleep(50)

threading.Thread(target=_self_ping, daemon=True).start()
