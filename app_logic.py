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
