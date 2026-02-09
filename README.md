# AI Local Concierge (随身 AI 地陪) 🗺️ V2.0

A next-generation travel companion app that uses Vision AI and Geolocation to tell you the hidden stories of the places you visit.

**Core Features:**
- **Walk & Talk:** Real-time audio guide based on your GPS location.
- **Snap & Ask:** Take a photo of anything, get a local's story (not a wiki summary).

## 📂 Project Structure
This project is a monorepo containing:
- **`backend/`**: FastAPI (Python) server handling AI logic, TTS, and Location services.
- **`mobile-app/`**: React Native (Expo) mobile client (iOS/Android).

---

## 🚀 Backend Setup (The Brain)

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   - Create a `.env` file in `backend/`:
     ```env
     OPENAI_API_KEY=sk-your-key-here
     ```

4. **Run Server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   - API Docs: `http://localhost:8000/docs`

---

## 📱 Mobile App Setup (The Body)

*Prerequisites: Node.js, npm/yarn, Expo Go app on your phone.*

1. **Navigate to mobile app:**
   ```bash
   cd mobile-app
   ```

2. **Initialize Project (If empty):**
   ```bash
   npx create-expo-app .
   ```

3. **Install Core Libraries:**
   ```bash
   npx expo install expo-location expo-av expo-camera react-native-maps
   ```

4. **Run Development Server:**
   ```bash
   npx expo start
   ```
   - Scan the QR code with your phone (Expo Go app) or press `i` for iOS Simulator / `a` for Android Emulator.

---

## 🔗 Connecting App to Backend
In your React Native code, point your API calls to your computer's local IP address (not `localhost` if testing on a real phone).
Example: `http://192.168.1.5:8000`

---
*Created by [Jyong](https://github.com/JohnJyong) with AI assistance.*
