# app_logic.py
import requests
import base64
from io import BytesIO

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

def encode_image(image_obj):
    """Encodes a PIL Image object to base64 string."""
    buffered = BytesIO()
    image_obj.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_image_api(base64_image, api_key, model="gpt-4o"):
    """Sends the base64 image to OpenAI Vision API and returns the raw JSON response."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is this? Give me the local scoop."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def analyze_location_api(latitude, longitude, api_key, model="gpt-4o"):
    """Uses LLM (or a Places API + LLM) to describe the location."""
    # Note: A real app would use Google Places API here first to get the POI name.
    # For MVP, we ask the LLM to 'hallucinate' based on coordinates (it knows famous lat/longs) 
    # or rely on a reverse geocoding result passed in.
    
    # Let's add reverse geocoding in the prompt for better accuracy if we had it.
    # For now, we trust the LLM's vast knowledge of coordinates for famous places.
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": LOCATION_PROMPT},
            {"role": "user", "content": f"I am currently at Latitude: {latitude}, Longitude: {longitude}. What is around me? Guide me."}
        ],
        "max_tokens": 300
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def text_to_speech(text, api_key):
    """Generates MP3 audio from text using OpenAI TTS."""
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "tts-1",
        "input": text,
        "voice": "alloy" # options: alloy, echo, fable, onyx, nova, shimmer
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.content
    else:
        return None

def speech_to_text(audio_bytes, api_key):
    """Transcribes audio using OpenAI Whisper."""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    files = {
        "file": ("audio.wav", audio_bytes, "audio/wav"),
        "model": (None, "whisper-1")
    }
    
    response = requests.post(url, headers=headers, files=files)
    return response.json()
