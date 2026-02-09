import streamlit as st
import os
from PIL import Image
from dotenv import load_dotenv

# Import logic from the helper file
from app_logic import encode_image, analyze_image_api

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
                result = analyze_image_api(base64_image, api_key, model=MODEL)
                
                # 3. Display Result
                if "choices" in result:
                    content = result["choices"][0]["message"]["content"]
                    st.success("✨ 找到啦！")
                    st.markdown(content)
                elif "error" in result:
                    st.error(f"API Error: {result['error']['message']}")
                else:
                    st.error(f"Unexpected response: {result}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.markdown("---")
st.caption("Powered by Vision LLM & Streamlit | Prototype v0.2")
