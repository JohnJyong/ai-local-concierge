# Backend - The "AI Brain" API
from fastapi import FastAPI, UploadFile, File, Form, WebSocket
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import os
import base64
from io import BytesIO
from PIL import Image
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Local Concierge API")

# --- 🧠 PROMPT ENGINEERING (The "Soul") ---
SYSTEM_PROMPT = """
You are a seasoned, local travel expert (a "Local Concierge"). 
You are NOT a boring encyclopedia. You are a street-smart friend who knows the hidden gems, the history, and the tourist traps.

When the user uploads a photo (of a landmark, food, street, or object):
1. **Identify it** accurately.
2. **Tell a Story (The "Hook"):** Don't just say "This is the Eiffel Tower." Say "Did you know the Eiffel Tower was originally hated by Parisians and called a 'useless monster'?"
3. **Local Insight/Secret:** Share a specific tip. E.g., "Don't eat at the cafe right under it; walk two blocks east to Rue de Monttessuy for better views and cheaper coffee."
4. **Verdict:** Is it a "Must-Do" or a "Tourist Trap"?

Tone: Witty, knowledgeable, helpful, slightly opinionated (like a real local).
Language: Simplified Chinese (unless the user asks otherwise).
"""

LOCATION_PROMPT = """
You are a 'Walking Guide' AI. The user is at the coordinates provided.
Based on this location, identify the MOST interesting landmark, building, or historical site within walking distance (100m).
Provide a short, engaging audio script (in Chinese) about what they are looking at or should look at.
Focus on: "Look to your left/right...", "Did you know that...", "This spot is famous for...".
Don't just list facts. Be a storyteller.
"""

# --- 🔑 CONFIG ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"

# --- 🖼️ IMAGE PROCESSING ---
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- 🛰️ ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Local Concierge Brain is Online 🧠"}

class LocationRequest(BaseModel):
    latitude: float
    longitude: float

@app.post("/analyze-location")
async def analyze_location(loc: LocationRequest):
    """
    Receives GPS coordinates, hallucinates (or uses Places API) to find nearby POI,
    and returns a guide script + audio URL.
    """
    if not OPENAI_API_KEY:
        return JSONResponse(content={"error": "API Key missing"}, status_code=500)

    # 1. Ask LLM what's here (Simulation for MVP)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": LOCATION_PROMPT},
            {"role": "user", "content": f"I am currently at Latitude: {loc.latitude}, Longitude: {loc.longitude}. What is around me? Guide me."}
        ],
        "max_tokens": 300
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        data = response.json()
        guide_text = data["choices"][0]["message"]["content"]
        
        # In a real app, we would generate audio here and return a URL to stream it
        # audio_url = await generate_audio(guide_text)
        
        return {
            "location": {"lat": loc.latitude, "lon": loc.longitude},
            "guide_text": guide_text,
            "audio_url": "/tts/stream"  # Placeholder
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze-photo")
async def analyze_photo(file: UploadFile = File(...)):
    """
    Receives an image file, analyzes it with Vision API, returns the story.
    """
    if not OPENAI_API_KEY:
        return JSONResponse(content={"error": "API Key missing"}, status_code=500)

    contents = await file.read()
    base64_image = encode_image(contents)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": "What is this? Give me the local scoop."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        "max_tokens": 500
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        data = response.json()
        story = data["choices"][0]["message"]["content"]
        return {"story": story}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# --- 🔊 TTS ENDPOINT (Streaming) ---
@app.post("/tts")
async def text_to_speech(text: str = Form(...)):
    """
    Generates TTS audio and returns binary stream.
    """
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "tts-1",
        "input": text,
        "voice": "alloy"
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return Response(content=response.content, media_type="audio/mpeg")
    else:
        return JSONResponse(content={"error": "TTS failed"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
