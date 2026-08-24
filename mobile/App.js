import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import * as Speech from 'expo-speech';

// Simple translations
const TRANSLATIONS = {
  en: {
    title: "KrishiMitra AI",
    tagline: "Multilingual Mandi Assistant",
    mic_btn: "Tap to Speak",
    mandi_price: "Mandi Price",
    marketplace: "Marketplace",
    welcome_greeting: "Hello, I am KrishiMitra AI! Speak or select your mandi to get live grain rates."
  },
  hi: {
    title: "कृषिमित्र एआई",
    tagline: "बहुभाषी मंडी सहायक",
    mic_btn: "बोलने के लिए दबाएं",
    mandi_price: "मंडी भाव",
    marketplace: "बाज़ार (मार्केट)",
    welcome_greeting: "नमस्ते, मैं कृषिमित्र एआई हूँ! मंडी भाव जानने के लिए बोलें या चयन करें।"
  },
  kn: {
    title: "ಕೃಷಿಮಿತ್ರ AI",
    tagline: "ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ಸಲಹೆಗಾರ",
    mic_btn: "ಮಾತನಾಡಲು ಒತ್ತಿ",
    mandi_price: "ಮಾರುಕಟ್ಟೆ ದರ",
    marketplace: "ಖರೀದಿದಾರರು",
    welcome_greeting: "ನಮಸ್ಕಾರ, ನಾನು ಕೃಷಿಮಿತ್ರ AI! ದರಗಳನ್ನು ತಿಳಿಯಲು ಮಾತನಾಡಿ ಅಥವಾ ಆಯ್ಕೆಮಾಡಿ."
  }
};

export default function App() {
  const [lang, setLang] = useState('en');
  const t = TRANSLATIONS[lang];

  const handleSpeak = (text) => {
    Speech.speak(text, {
      language: lang === 'kn' ? 'kn-IN' : lang === 'hi' ? 'hi-IN' : 'en-IN',
      pitch: 1.0,
      rate: 0.9,
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>{t.title}</Text>
        <Text style={styles.headerSubtitle}>{t.tagline}</Text>
      </View>

      <View style={styles.langSelector}>
        <TouchableOpacity style={[styles.langBtn, lang === 'en' && styles.activeLang]} onPress={() => setLang('en')}>
          <Text style={[styles.langText, lang === 'en' && styles.activeLangText]}>English</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.langBtn, lang === 'hi' && styles.activeLang]} onPress={() => setLang('hi')}>
          <Text style={[styles.langText, lang === 'hi' && styles.activeLangText]}>हिन्दी</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.langBtn, lang === 'kn' && styles.activeLang]} onPress={() => setLang('kn')}>
          <Text style={[styles.langText, lang === 'kn' && styles.activeLangText]}>ಕನ್ನಡ</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.assistantCard}>
          <Text style={styles.assistantText}>{t.welcome_greeting}</Text>
          
          <TouchableOpacity 
            style={styles.micButton} 
            onPress={() => handleSpeak(t.welcome_greeting)}
          >
            <Text style={styles.micText}>🎙️</Text>
          </TouchableOpacity>
          <Text style={styles.micLabel}>{t.mic_btn}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>{t.mandi_price}</Text>
          <Text style={styles.dummyInfo}>🌾 Maize (Shivamogga APMC): ₹2,320 / quintal</Text>
          <Text style={styles.dummyInfo}>🌾 Wheat (Indore APMC): ₹2,540 / quintal</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>{t.marketplace}</Text>
          <Text style={styles.dummyInfo}>🤝 Karnataka Agri Exports - Rating: 4.7 ⭐</Text>
          <Text style={styles.dummyInfo}>🏪 Sri Manjunatha Fertilizer Depot - Shivamogga</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  header: {
    backgroundColor: '#16a34a',
    padding: 20,
    alignItems: 'center',
  },
  headerTitle: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    color: '#dcfce7',
    fontSize: 12,
  },
  langSelector: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#15803d',
    paddingVertical: 8,
  },
  langBtn: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  activeLang: {
    backgroundColor: '#fff',
  },
  langText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  activeLangText: {
    color: '#15803d',
  },
  content: {
    padding: 16,
    gap: 16,
  },
  assistantCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  assistantText: {
    fontSize: 14,
    color: '#374151',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 20,
  },
  micButton: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: '#16a34a',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  micText: {
    fontSize: 28,
  },
  micLabel: {
    fontSize: 11,
    color: '#6b7280',
    marginTop: 8,
    fontWeight: 'bold',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 10,
    borderLeftWidth: 3,
    borderLeftColor: '#16a34a',
    paddingLeft: 8,
  },
  dummyInfo: {
    fontSize: 13,
    color: '#4b5563',
    marginVertical: 4,
  }
});
