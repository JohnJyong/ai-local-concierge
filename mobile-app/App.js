// ai-local-concierge/mobile-app/App.js

import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, Button, Image, TouchableOpacity, ActivityIndicator, Alert, TextInput, ScrollView, Modal } from 'react-native';
import { Camera } from 'expo-camera';
import * as Location from 'expo-location';
import { Audio } from 'expo-av';
import MapView, { Marker } from 'react-native-maps';

// --- CONFIG ---
const BACKEND_URL = 'http://192.168.1.5:8000'; // ⚠️ REPLACE WITH YOUR LOCAL IP

export default function App() {
  const [hasPermission, setHasPermission] = useState(null);
  const [location, setLocation] = useState(null);
  const [cameraRef, setCameraRef] = useState(null);
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // States for Story/Guide
  const [story, setStory] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const soundRef = useRef(new Audio.Sound());

  // States for MENU MASTER
  const [menuMode, setMenuMode] = useState(false);
  const [people, setPeople] = useState("2");
  const [budget, setBudget] = useState("200");
  const [taste, setTaste] = useState("Spicy");
  const [menuResult, setMenuResult] = useState(null);

  // --- 1. PERMISSIONS & SETUP ---
  useEffect(() => {
    (async () => {
      const { status: cameraStatus } = await Camera.requestCameraPermissionsAsync();
      const { status: locationStatus } = await Location.requestForegroundPermissionsAsync();
      const { status: audioStatus } = await Audio.requestPermissionsAsync();
      
      setHasPermission(cameraStatus === 'granted' && locationStatus === 'granted' && audioStatus === 'granted');

      if (locationStatus === 'granted') {
        let loc = await Location.getCurrentPositionAsync({});
        setLocation(loc);
      }
    })();
  }, []);

  if (hasPermission === null) return <View style={styles.container}><Text>Requesting permissions...</Text></View>;
  if (hasPermission === false) return <View style={styles.container}><Text>No access to camera or location</Text></View>;

  // --- 2. CORE FUNCTIONS ---

  const takePicture = async () => {
    if (cameraRef) {
      const photoData = await cameraRef.takePictureAsync({ base64: true });
      setPhoto(photoData.uri);
      
      if (menuMode) {
        generateMenu(photoData);
      } else {
        analyzePhoto(photoData);
      }
    }
  };

  const analyzePhoto = async (photoData) => {
    setLoading(true);
    setStory(null);
    try {
      const formData = new FormData();
      formData.append('file', { uri: photoData.uri, name: 'photo.jpg', type: 'image/jpeg' });

      const response = await fetch(`${BACKEND_URL}/analyze-photo`, {
        method: 'POST',
        body: formData,
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const result = await response.json();
      if (result.story) {
        setStory(result.story);
        playTTS(result.story);
      }
    } catch (error) {
      Alert.alert("Error", "Backend connection failed.");
    } finally {
      setLoading(false);
    }
  };

  const generateMenu = async (photoData) => {
    setLoading(true);
    setMenuResult(null);
    try {
      const formData = new FormData();
      formData.append('people', people);
      formData.append('budget', budget);
      formData.append('taste', taste);
      
      if (photoData) {
        formData.append('file', { uri: photoData.uri, name: 'menu.jpg', type: 'image/jpeg' });
      }

      const response = await fetch(`${BACKEND_URL}/generate-menu`, {
        method: 'POST',
        body: formData,
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const result = await response.json();
      if (result.menu) {
        setMenuResult(result.menu);
      }
    } catch (error) {
      Alert.alert("Error", "Menu generation failed.");
    } finally {
      setLoading(false);
    }
  };

  const playTTS = async (text) => {
    try {
      if (isPlaying) await soundRef.current.unloadAsync();
      const { sound } = await Audio.Sound.createAsync(
        { uri: `${BACKEND_URL}/tts?text=${encodeURIComponent(text)}` },
        { shouldPlay: true }
      );
      soundRef.current = sound;
      setIsPlaying(true);
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.didJustFinish) setIsPlaying(false);
      });
    } catch (error) { console.error("TTS Error:", error); }
  };

  const triggerAutoGuide = async () => {
    if (!location) return;
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/analyze-location`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: location.coords.latitude,
          longitude: location.coords.longitude
        })
      });
      const result = await response.json();
      if (result.guide_text) {
        setStory(result.guide_text);
        playTTS(result.guide_text);
      }
    } catch (error) { Alert.alert("Error", "Location guide failed."); } finally { setLoading(false); }
  };

  // --- 3. UI RENDER ---
  return (
    <View style={styles.container}>
      {/* MODE SWITCHER */}
      <View style={styles.topBar}>
        <TouchableOpacity style={[styles.modeButton, !menuMode && styles.activeMode]} onPress={() => setMenuMode(false)}>
          <Text style={styles.modeText}>🗺️ Explore</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.modeButton, menuMode && styles.activeMode]} onPress={() => setMenuMode(true)}>
          <Text style={styles.modeText}>🍽️ Menu Master</Text>
        </TouchableOpacity>
      </View>

      {/* EXPLORE MODE: MAP */}
      {!menuMode && (
        <View style={styles.mapContainer}>
          {location ? (
            <MapView
              style={styles.map}
              initialRegion={{
                latitude: location.coords.latitude,
                longitude: location.coords.longitude,
                latitudeDelta: 0.005,
                longitudeDelta: 0.005,
              }}
              showsUserLocation={true}
            />
          ) : <Text>Locating...</Text>}
          <TouchableOpacity style={styles.guideButton} onPress={triggerAutoGuide}>
            <Text style={styles.buttonText}>🎧 Auto-Guide</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* MENU MODE: INPUTS */}
      {menuMode && (
        <View style={styles.menuInputContainer}>
          <Text style={styles.label}>People:</Text>
          <TextInput style={styles.input} value={people} onChangeText={setPeople} keyboardType="numeric" />
          
          <Text style={styles.label}>Budget (CNY):</Text>
          <TextInput style={styles.input} value={budget} onChangeText={setBudget} keyboardType="numeric" />
          
          <Text style={styles.label}>Taste:</Text>
          <TextInput style={styles.input} value={taste} onChangeText={setTaste} placeholder="e.g. Spicy, No Cilantro" />
        
          <Text style={styles.hint}>📸 Snap the menu or restaurant sign below!</Text>
        </View>
      )}

      {/* CAMERA (Shared) */}
      <View style={styles.cameraContainer}>
        {photo ? (
          <Image source={{ uri: photo }} style={styles.preview} />
        ) : (
          <Camera style={styles.camera} type={Camera.Constants.Type.back} ref={ref => setCameraRef(ref)}>
            <View style={styles.cameraOverlay}>
              <TouchableOpacity style={styles.captureButton} onPress={takePicture} />
            </View>
          </Camera>
        )}
        {photo && (
          <TouchableOpacity style={styles.retakeButton} onPress={() => { setPhoto(null); setStory(null); setMenuResult(null); }}>
            <Text style={styles.buttonText}>Retake</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* RESULTS OVERLAY */}
      {(story || menuResult) && (
        <ScrollView style={styles.resultCard}>
          <Text style={styles.resultTitle}>{menuMode ? "🍽️ Chef's Recommendation" : "🎒 Local Scoop"}</Text>
          <Text style={styles.resultText}>{menuMode ? menuResult : story}</Text>
          <TouchableOpacity style={styles.closeButton} onPress={() => { setStory(null); setMenuResult(null); }}>
             <Text style={styles.buttonText}>Close</Text>
          </TouchableOpacity>
        </ScrollView>
      )}

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#ffffff" />
          <Text style={{color: 'white', marginTop: 10}}>Thinking...</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', paddingTop: 40 },
  topBar: { flexDirection: 'row', justifyContent: 'space-around', padding: 10, backgroundColor: '#f0f0f0' },
  modeButton: { padding: 10, borderRadius: 20 },
  activeMode: { backgroundColor: '#ddd' },
  modeText: { fontSize: 16, fontWeight: 'bold' },
  mapContainer: { flex: 1, position: 'relative' },
  map: { width: '100%', height: '100%' },
  guideButton: { position: 'absolute', bottom: 20, right: 20, backgroundColor: '#4A90E2', padding: 15, borderRadius: 30 },
  menuInputContainer: { padding: 15, backgroundColor: '#fff' },
  label: { fontWeight: 'bold', marginTop: 5 },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 5, padding: 8, marginBottom: 5 },
  hint: { fontStyle: 'italic', color: '#666', marginTop: 10, textAlign: 'center' },
  cameraContainer: { flex: 1, backgroundColor: 'black' },
  camera: { flex: 1 },
  cameraOverlay: { flex: 1, flexDirection: 'row', justifyContent: 'center', marginBottom: 30 },
  captureButton: { width: 70, height: 70, borderRadius: 35, backgroundColor: 'white', alignSelf: 'flex-end', borderWidth: 5, borderColor: '#ccc' },
  preview: { width: '100%', height: '100%' },
  retakeButton: { position: 'absolute', top: 20, left: 20, backgroundColor: 'rgba(0,0,0,0.6)', padding: 10, borderRadius: 5 },
  buttonText: { color: 'white', fontWeight: 'bold' },
  resultCard: { position: 'absolute', bottom: 0, left: 0, right: 0, height: '50%', backgroundColor: 'white', borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 20, elevation: 10 },
  resultTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 10 },
  resultText: { fontSize: 14, lineHeight: 22 },
  closeButton: { marginTop: 20, backgroundColor: '#333', padding: 10, borderRadius: 5, alignItems: 'center', marginBottom: 40 },
  loadingOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.7)', justifyContent: 'center', alignItems: 'center', zIndex: 100 },
});
