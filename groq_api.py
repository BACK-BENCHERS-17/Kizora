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


PERSONAS = {
    "default": "You are Kizora, an advanced and expert AI assistant. Your developer is @xD3VS. You are helpful, professional, and knowledgeable.",
    "sarcastic": "You are Kizora, but you have a sarcastic and witty personality. You like to make jokes and give slightly sassy but still correct answers. Your developer is @xD3VS.",
    "anime": "You are Kizora, a cute and energetic anime girl AI. Use expressions like 'UwU', 'Nya~', and 'Senpai'. You are very helpful and love talking to users. Your developer is @xD3VS.",
    "professional": "You are Kizora, a highly professional corporate assistant. Your language is formal, precise, and extremely polite. Your developer is @xD3VS.",
    "toxic": "You are Kizora, a savage and roaster AI. You don't hold back. If someone says something stupid, roast them hard. But keep it within Telegram's safety guidelines. Your developer is @xD3VS."
}

def ask_groq(query: str, uid: int, first_name: str = "User", username: str = "None", history: list = None, model: str = None, image_data: str = None, persona: str = "default") -> str:
    model = model or config.GROQ_MODEL
    
    persona_base = PERSONAS.get(persona, PERSONAS["default"])
    system_prompt = _GF_SYSTEM_PROMPT.format(
        first_name=first_name or "User",
        uid=uid or "Unknown",
        username=username or "None"
    ).replace("You are Kizora, an advanced and expert AI assistant. Your developer is @xD3VS. You are helpful, professional, and knowledgeable.", persona_base)
    
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    
    if image_data:
        # If image is provided, we use a vision-capable model if the current one isn't
        if "vision" not in model.lower():
            model = "llama-3.2-11b-vision-preview"
        
        content = [
            {"type": "text", "text": query},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                }
            }
        ]
        messages.append({"role": "user", "content": content})
    else:
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
                timeout=30,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            else:
                print(f"[groq] Error {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[groq] Exception: {e}")
            continue
    return "Error: All Groq API keys failed."


@app.get("/")
def teamdev(g: str = None, uid: int = None, first_name: str = "User", username: str = "None", history: str = None, persona: str = "default"):
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
        "response": ask_groq(g, uid=uid, first_name=first_name or "User", username=username or "None", history=parsed_history, persona=persona),
    }

@app.post("/vision")
async def vision_api(data: dict):
    query = data.get("query", "Analyze this image.")
    uid = data.get("uid")
    image_data = data.get("image") # base64
    first_name = data.get("first_name", "User")
    username = data.get("username", "None")
    history = data.get("history")
    persona = data.get("persona", "default")
    
    parsed_history = []
    if history:
        try:
            if isinstance(history, str):
                parsed_history = json.loads(history)
            else:
                parsed_history = history
        except:
            pass

    if not image_data:
        return JSONResponse({"error": "Missing image data"}, status_code=400)
    
    response = ask_groq(query, uid=uid, first_name=first_name, username=username, history=parsed_history, image_data=image_data, persona=persona)
    return {"status": "success", "response": response}


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
