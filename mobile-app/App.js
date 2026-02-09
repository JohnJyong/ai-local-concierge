// ai-local-concierge/mobile-app/App.js

import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, Button, Image, TouchableOpacity, ActivityIndicator, Alert, Platform } from 'react-native';
import { Camera } from 'expo-camera';
import * as Location from 'expo-location';
import { Audio } from 'expo-av';
import MapView, { Marker } from 'react-native-maps';

// --- CONFIG ---
// ⚠️ REPLACE WITH YOUR LOCAL IP ADDRESS (e.g., 192.168.1.5)
const BACKEND_URL = 'http://192.168.1.5:8000'; 

export default function App() {
  const [hasPermission, setHasPermission] = useState(null);
  const [location, setLocation] = useState(null);
  const [cameraRef, setCameraRef] = useState(null);
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [story, setStory] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const soundRef = useRef(new Audio.Sound());

  // --- 1. PERMISSIONS & SETUP ---
  useEffect(() => {
    (async () => {
      const { status: cameraStatus } = await Camera.requestCameraPermissionsAsync();
      const { status: locationStatus } = await Location.requestForegroundPermissionsAsync();
      const { status: audioStatus } = await Audio.requestPermissionsAsync();
      
      setHasPermission(cameraStatus === 'granted' && locationStatus === 'granted' && audioStatus === 'granted');

      // Get initial location
      if (locationStatus === 'granted') {
        let loc = await Location.getCurrentPositionAsync({});
        setLocation(loc);
      }
    })();
  }, []);

  if (hasPermission === null) {
    return <View style={styles.container}><Text>Requesting permissions...</Text></View>;
  }
  if (hasPermission === false) {
    return <View style={styles.container}><Text>No access to camera or location</Text></View>;
  }

  // --- 2. CORE FUNCTIONS ---

  // 📸 Take Photo & Analyze
  const takePicture = async () => {
    if (cameraRef) {
      const photoData = await cameraRef.takePictureAsync({ base64: true });
      setPhoto(photoData.uri);
      analyzePhoto(photoData);
    }
  };

  const analyzePhoto = async (photoData) => {
    setLoading(true);
    setStory(null);
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: photoData.uri,
        name: 'photo.jpg',
        type: 'image/jpeg',
      });

      const response = await fetch(`${BACKEND_URL}/analyze-photo`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const result = await response.json();
      if (result.story) {
        setStory(result.story);
        // Auto-play TTS
        playTTS(result.story);
      } else {
        Alert.alert("Error", "Could not analyze photo.");
      }
    } catch (error) {
      console.error(error);
      Alert.alert("Error", "Backend connection failed. Check IP.");
    } finally {
      setLoading(false);
    }
  };

  // 🎧 Play Text-to-Speech
  const playTTS = async (text) => {
    try {
      if (isPlaying) {
        await soundRef.current.unloadAsync();
      }

      const { sound } = await Audio.Sound.createAsync(
        { uri: `${BACKEND_URL}/tts?text=${encodeURIComponent(text)}` },
        { shouldPlay: true }
      );
      soundRef.current = sound;
      setIsPlaying(true);
      
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.didJustFinish) {
          setIsPlaying(false);
        }
      });
    } catch (error) {
      console.error("TTS Error:", error);
    }
  };

  // 🛰️ Auto-Guide (Location Based)
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
    } catch (error) {
      Alert.alert("Error", "Location guide failed.");
    } finally {
      setLoading(false);
    }
  };

  // --- 3. UI RENDER ---
  return (
    <View style={styles.container}>
      {/* MAP / CAMERA TOGGLE (Simplified: Top half Map, Bottom half Camera for MVP) */}
      
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
          >
             <Marker coordinate={location.coords} title="You are here" />
          </MapView>
        ) : (
          <Text>Locating...</Text>
        )}
        <TouchableOpacity style={styles.guideButton} onPress={triggerAutoGuide}>
          <Text style={styles.buttonText}>🎧 Auto-Guide Me</Text>
        </TouchableOpacity>
      </View>

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
          <TouchableOpacity style={styles.retakeButton} onPress={() => setPhoto(null)}>
            <Text style={styles.buttonText}>Retake</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* STORY CARD OVERLAY */}
      {story && (
        <View style={styles.storyCard}>
          <Text style={styles.storyTitle}>Local Scoop 🎒</Text>
          <Text style={styles.storyText}>{story}</Text>
          {loading && <ActivityIndicator size="small" color="#0000ff" />}
        </View>
      )}

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#ffffff" />
          <Text style={{color: 'white', marginTop: 10}}>Consulting Local Expert...</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  mapContainer: {
    flex: 1, // Top half
    position: 'relative',
  },
  map: {
    width: '100%',
    height: '100%',
  },
  guideButton: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    backgroundColor: '#4A90E2',
    padding: 15,
    borderRadius: 30,
    elevation: 5,
  },
  cameraContainer: {
    flex: 1, // Bottom half
    backgroundColor: 'black',
    position: 'relative',
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    flex: 1,
    backgroundColor: 'transparent',
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 30,
  },
  captureButton: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'white',
    alignSelf: 'flex-end',
    borderWidth: 5,
    borderColor: '#ccc',
  },
  preview: {
    width: '100%',
    height: '100%',
  },
  retakeButton: {
    position: 'absolute',
    top: 20,
    left: 20,
    backgroundColor: 'rgba(0,0,0,0.6)',
    padding: 10,
    borderRadius: 5,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  storyCard: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: '40%',
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
  },
  storyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#333',
  },
  storyText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 100,
  },
});
