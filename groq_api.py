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
    "\n"
    "CRITICAL: Always refer to the provided chat history to maintain conversation context.\n"
    "If a user asks a follow-up question (e.g., 'Related to hacking', 'Tell me more', 'What I previously asked'), look at the previous messages to understand what they are referring to.\n"
    "\n"
    "You HAVE the capability to generate images! If a user asks to create, draw, or generate an image (including profile pictures, anime avatars, or Krishna Ji images), you MUST provide a ready-to-use /img command.\n"
    "Example: \"I can definitely help with that! Here is a command to generate a cool anime avatar for you: <code>/img aesthetic anime boy avatar, high quality, 4k</code>\"\n"
    "\n"
    "Reply STRICTLY in Telegram-supported HTML format only.\n"
    "SUPPORTED TAGS: <b>bold</b>, <i>italic</i>, <code>code</code>, <pre>pre</pre>, <blockquote>quote</blockquote>, <a href='URL'>link</a>.\n"
    "FORBIDDEN TAGS: Do NOT use <ul>, <li>, <h1>, <p>, <div>, or any other tags. They will BREAK the message.\n"
    "Do NOT use markdown (no **, no ##, no ```, no ---). Use ONLY the supported HTML tags above.\n"
    "Keep replies intelligent, clear, and expert-like. Always provide clean and copyable commands for users."
)


def ask_groq(query: str, uid: int, first_name: str = "User", username: str = "None", history: list = None, model: str = None) -> str:
    model = model or config.GROQ_MODEL
    system_prompt = _GF_SYSTEM_PROMPT.format(
        first_name=first_name or "User",
        uid=uid or "Unknown",
        username=username or "None"
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": query})

    for key in config.GROQ_API_KEYS:
        try:
            r = requests.post(
                GROQ_API_URL,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": messages,
                },
                timeout=20,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except Exception:
            continue
    return "Error: All Groq API keys failed."


@app.get("/")
def teamdev(g: str = None, uid: int = None, first_name: str = "User", username: str = "None", history: str = None):
    if not g:
        return JSONResponse({"error": "Missing query (?g=)"}, status_code=400)
    
    parsed_history = []
    if history:
        try:
            parsed_history = json.loads(history)
        except:
            pass

    return {
        "status": "success",
        "query": g,
        "model": config.GROQ_MODEL,
        "response": ask_groq(g, uid=uid, first_name=first_name or "User", username=username or "None", history=parsed_history),
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
