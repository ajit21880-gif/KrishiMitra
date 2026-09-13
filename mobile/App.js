import React, { useEffect } from 'react';
import { StyleSheet, SafeAreaView, StatusBar, Platform, PermissionsAndroid } from 'react-native';
import { WebView } from 'react-native-webview';

export default function App() {
  useEffect(() => {
    const requestMicrophonePermission = async () => {
      if (Platform.OS === 'android') {
        try {
          const granted = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
            {
              title: "Microphone Permission Required",
              message: "KrishiMitra needs access to your microphone so you can ask voice queries in Hindi and Kannada.",
              buttonPositive: "Grant Permission"
            }
          );
          if (granted === PermissionsAndroid.RESULTS.GRANTED) {
            console.log("Microphone permission granted successfully!");
          } else {
            console.log("Microphone permission denied.");
          }
        } catch (err) {
          console.warn(err);
        }
      }
    };
    requestMicrophonePermission();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      <WebView 
        source={{ uri: 'https://krishi-mitra-crestsubarn.vercel.app/' }}
        style={styles.webview}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        startInLoadingState={true}
        scalesPageToFit={true}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  webview: {
    flex: 1,
  },
});
