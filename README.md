
# V2.0 Architecture

This is a complete rewrite of the initial prototype.

## 📂 Structure
- `backend/`: FastAPI Python server (Logic, LLM calls, TTS generation).
- `mobile-app/`: (Placeholder) This will be the React Native (Expo) project.

## 🚀 How to Run Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `uvicorn main:app --reload`
4. Access docs at `http://localhost:8000/docs`

## 📱 Mobile App (Coming Soon)
- Use `npx create-expo-app mobile-app` to initialize inside `mobile-app/`.
- Connect to backend API for AI features.
