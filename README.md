# AI Local Concierge (随身 AI 地陪) 🗺️

A Visual AI travel companion prototype that identifies landmarks/food/streets and tells you the *real* story, like a local friend.

**Core Idea:**
- **Input:** Photo from your camera.
- **AI Processing:** Vision LLM + "Local Knowledge" Prompt.
- **Output:** Identity + History/Gossip + "Tourist Trap vs Hidden Gem" verdict.

## 🚀 Quick Start

1. **Clone Repo**
   ```bash
   git clone https://github.com/JohnJyong/ai-local-concierge.git
   cd ai-local-concierge
   ```

2. **Setup Env**
   ```bash
   pip install -r requirements.txt
   export OPENAI_API_KEY="sk-..."  # Or edit .env
   ```

3. **Run App**
   ```bash
   streamlit run app.py
   ```

## 📸 Demo Logic
- Upload a photo (e.g., Eiffel Tower, street food).
- Click "Ask Concierge".
- Get a witty, localized story instead of a Wikipedia summary.

## 🛠️ Tech Stack
- Python 3.9+
- Streamlit (Rapid UI)
- OpenAI GPT-4o (Vision) / Google Gemini Pro Vision

---
*Created by [Jyong](https://github.com/JohnJyong) with AI assistance.*
