import streamlit as st
import os
import requests
import base64
from PIL import Image
from io import BytesIO

# --- 🎯 CONFIGURATION ---
PAGE_TITLE = "Local Concierge (随身地陪)"
PAGE_ICON = "🎒"
MODEL = "gpt-4o"  # or "gpt-4-vision-preview"

# --- 🔑 API KEY ---
# In a real app, use environment variables. For demo, we check os.environ.
if "OPENAI_API_KEY" not in os.environ:
    st.error("⚠️ Please set OPENAI_API_KEY environment variable!")
    st.stop()

api_key = os.environ["OPENAI_API_KEY"]

# --- 🧠 PROMPT ENGINEERING (The "Soul") ---
# Key Differentiator: Not just "What is this?", but "Tell me the gossip/history/secrets."
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

# --- 🖼️ IMAGE PROCESSING ---
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_image(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": MODEL,
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

# --- 📱 UI LAYOUT ---
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.markdown("### 📸 拍一张，听听本地人的故事")
st.info("💡 这是一个 **Visual AI Concierge** 的原型。上传照片（景点/美食/街道），AI 会像老朋友一样告诉你背后的故事和避坑指南。")

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the image
    image = Image.open(uploaded_file)
    st.image(image, caption='Your View', use_column_width=True)

    if st.button("🔍 召唤地陪 (Ask Concierge)"):
        with st.spinner("🤔 正在回忆这地方的八卦... (Consulting local knowledge...)"):
            try:
                # 1. Encode Image
                base64_image = encode_image(image)
                
                # 2. Call Vision API
                result = analyze_image(base64_image)
                
                # 3. Display Result
                if "choices" in result:
                    content = result["choices"][0]["message"]["content"]
                    st.success("✨ 找到啦！")
                    st.markdown(content)
                else:
                    st.error(f"Error from API: {result}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.markdown("---")
st.caption("Powered by Vision LLM & Streamlit | Prototype v0.1")
