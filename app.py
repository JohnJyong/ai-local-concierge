import streamlit as st
import os
import time
from PIL import Image
from dotenv import load_dotenv
from app_logic import analyze_image_api, analyze_location_api, encode_image, text_to_speech, speech_to_text
from streamlit_js_eval import get_geolocation

# --- 🎯 CONFIGURATION ---
load_dotenv() # Load environment variables from .env file

PAGE_TITLE = os.getenv("PAGE_TITLE", "Local Concierge (随身地陪)")
PAGE_ICON = os.getenv("PAGE_ICON", "🎒")
MODEL = os.getenv("MODEL", "gpt-4o")

# --- 🔑 API KEY ---
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ Please set OPENAI_API_KEY environment variable! (See .env.example)")
    st.stop()

# --- 📱 UI LAYOUT ---
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.markdown("### 🗺️ Walk & Talk (边走边听)")

# --- 🛰️ GEOLOCATION ---
st.sidebar.markdown("### 🛰️ 定位 (GPS)")
location = get_geolocation()

if location and location.get('coords'):
    lat = location['coords']['latitude']
    lon = location['coords']['longitude']
    st.sidebar.success(f"📍 Lat: {lat:.4f}, Lon: {lon:.4f}")
    
    # --- AUTO-GUIDE MODE ---
    if st.sidebar.button("🎧 开始自动导游 (Start Auto-Guide)"):
        with st.spinner("🤖 正在感知周围环境..."):
            # Call Location API (LLM hallucinates based on coords for now)
            result = analyze_location_api(lat, lon, api_key, model=MODEL)
            if "choices" in result:
                guide_text = result["choices"][0]["message"]["content"]
                st.markdown(f"**Guide:** {guide_text}")
                
                # TTS
                with st.spinner("🔊 生成语音解说..."):
                    audio_bytes = text_to_speech(guide_text, api_key)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    else:
                        st.error("TTS Failed.")
            else:
                st.error("Location API Failed.")
else:
    st.sidebar.warning("⚠️ 请允许浏览器获取位置权限以启用导游功能。")


# --- 📸 PHOTO MODE ---
st.markdown("---")
st.markdown("### 📸 拍照识别 (Snap & Ask)")
uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Your View', use_column_width=True)

    if st.button("🔍 召唤地陪 (Ask Concierge)"):
        with st.spinner("🤔 正在回忆这地方的八卦..."):
            try:
                base64_image = encode_image(image)
                result = analyze_image_api(base64_image, api_key, model=MODEL)
                
                if "choices" in result:
                    content = result["choices"][0]["message"]["content"]
                    st.success("✨ 找到啦！")
                    st.markdown(content)
                    
                    # TTS for Photo Explanation
                    if st.checkbox("🔊 朗读解说 (Read Aloud)"):
                         with st.spinner("Generating audio..."):
                            audio_bytes = text_to_speech(content, api_key)
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                elif "error" in result:
                    st.error(f"API Error: {result['error']['message']}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.markdown("---")
st.caption("Powered by OpenAI (Vision + TTS + Whisper) | Prototype v0.3")
