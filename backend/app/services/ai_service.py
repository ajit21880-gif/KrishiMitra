import os
import json
import re
import requests
from typing import Dict, Any, Optional

# Basic rule-based fallback keyword dictionaries
LANG_PATTERNS = {
    "kn": re.compile(r"[\u0c80-\u0cff]"), # Kannada Unicode block
    "hi": re.compile(r"[\u0900-\u097f]")  # Devanagari Unicode block (Hindi/Marathi)
}

COMMODITY_KEYWORDS = {
    "Maize": ["maize", "corn", "maze", "ಮಕ್ಕೆಜೋಳ", "ಮೆಕ್ಕೆಜೋಳ", "ಮಕ್ಕ ಜೋಳ", "ಜೋಳ", "मक्का"],
    "Wheat": ["wheat", "wheet", "gehun", "gehu", "गेहूं", "कनक", "ಗೋಧಿ"],
    "Paddy (Rice)": ["paddy", "rice", "धान", "ಚಾವಲ್", "ಭತ್ತ", "ರೈಸ್"],
    "Soyabean": ["soyabean", "soybean", "सोयाबीन", "ಸೋಯาಬೀನ್"],
    "Onion": ["onion", "प्याज", "कांदा", "ಈರುಳ್ಳಿ"],
    "Tomato": ["tomato", "टमाटर", "ಟೊಮೆಟೊ"],
    "Toor Dal": ["toor dal", "toor", "arhar", "arhar dal", "ತೊಗರಿ ಬೇಳೆ", "ತೊಗರಿ", "तुअर", "अरहर"],
    "Cotton": ["cotton", "kapas", "ಹತ್ತಿ", "कपास"],
    "Gram (Chana)": ["gram", "chana", "चना", "ಕಡಲೆ", "ಕಡಲೆ ಬೇಳೆ"]
}

LOCATION_KEYWORDS = {
    "Shivamogga": {"district": "Shivamogga", "state": "Karnataka", "keywords": ["shimoga", "shivamogga", "ಶಿವಮೊಗ್ಗ"]},
    "Davanagere": {"district": "Davanagere", "state": "Karnataka", "keywords": ["davanagere", "ದಾವಣಗೆರೆ"]},
    "Bengaluru": {"district": "Bengaluru", "state": "Karnataka", "keywords": ["bengaluru", "bangalore", "ಬೆಂಗಳೂರು", "yeshwanthpur"]},
    "Indore": {"district": "Indore", "state": "Madhya Pradesh", "keywords": ["indore", "इंदौर"]},
    "Ujjain": {"district": "Ujjain", "state": "Madhya Pradesh", "keywords": ["ujjain", "उज्जैन"]},
    "Nashik": {"district": "Nashik", "state": "Maharashtra", "keywords": ["lasalgaon", "nashik", "नाशिक", "लासलगाव"]},
    "Pune": {"district": "Pune", "state": "Maharashtra", "keywords": ["pune", "पुणे"]}
}

class AIService:
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language: default to en, supports hi, kn based on scripts"""
        for lang, pattern in LANG_PATTERNS.items():
            if pattern.search(text):
                return lang
        return "en"

    @staticmethod
    def parse_query_rule_based(text: str) -> Dict[str, Any]:
        """Simple, robust regex and keyword based fallback intent parser"""
        text_lower = text.lower()
        detected_lang = AIService.detect_language(text)
        
        # 1. Detect Intent
        intent = "price" # Default
        
        dealer_words = ["dap", "urea", "fertilizer", "seed", "pesticide", "खाद", "बीज", "कीटनाशक", "ರಸಗೊಬ್ಬರ", "ಬೀಜ", "ಕೀಟನಾಶಕ"]
        buyer_words = ["sell", "buyer", "purchase", "wholesaler", "trader", "बेचना", "खरीददार", "व्यापारी", "ಮಾರಾಟ", "ಖರೀದಿದಾರ", "ವ್ಯಾಪಾರಿ"]
        weather_words = ["weather", "rain", "monsoon", "temperature", "मौसम", "बारिश", "ಮಳೆ", "ಹವಾಮಾನ"]
        msp_words = ["msp", "support price", "एमएसपी", "समर्थन मूल्य", "ಬೆಂಬಲ ಬೆಲೆ"]
        scheme_words = ["scheme", "kisan", "yojana", "योजना", "ಯೋಜನೆ"]

        if any(w in text_lower for w in dealer_words):
            intent = "dealer"
        elif any(w in text_lower for w in buyer_words):
            intent = "buyer"
        elif any(w in text_lower for w in weather_words):
            intent = "weather"
        elif any(w in text_lower for w in msp_words):
            intent = "msp"
        elif any(w in text_lower for w in scheme_words):
            intent = "scheme"

        # 2. Extract Commodity
        extracted_commodity = None
        for comm, kw_list in COMMODITY_KEYWORDS.items():
            for kw in kw_list:
                # Matches the keyword with start/end of string, spaces, or punctuation around it
                pattern = rf"(?:\s|^){re.escape(kw)}(?:\s|$|[.,?!])"
                if re.search(pattern, text_lower):
                    extracted_commodity = comm
                    break
            if extracted_commodity:
                break
                
        # 3. Extract Location
        extracted_district = None
        extracted_state = None
        for loc, info in LOCATION_KEYWORDS.items():
            for kw in info["keywords"]:
                pattern = rf"(?:\s|^){re.escape(kw)}(?:\s|$|[.,?!])"
                if re.search(pattern, text_lower):
                    extracted_district = info["district"]
                    extracted_state = info["state"]
                    break
            if extracted_district:
                break
                
        return {
            "intent": intent,
            "commodity": extracted_commodity,
            "state": extracted_state,
            "district": extracted_district,
            "language": detected_lang,
            "raw_query": text
        }

    @staticmethod
    def parse_query_with_llm(text: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Call Gemini API for robust NLP parsing of agricultural queries"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            
            prompt = f"""
            You are a smart AI agricultural assistant. A farmer has asked you a query in English, Hindi, or Kannada.
            
            First, check if the query is asking about one of these core app features: "price" (mandi rates), "msp" (minimum support price), "buyer" (find verified buyers to sell), "dealer" (find input fertilizer/seed dealers), "weather" (weather forecasts), "scheme" (govt schemes).
            If it is a core feature, extract the details.
            - Supported commodities: "Maize", "Wheat", "Paddy (Rice)", "Soyabean", "Onion", "Tomato". Map synonyms accordingly.
            - States & Districts should be standardized (e.g. State: "Karnataka", District: "Shivamogga"; State: "Maharashtra", District: "Pune").
            
            If the query is a general farming question, agronomy advice, greeting, or anything outside those core features, set the intent to "general".
            When intent is "general", you must also provide a helpful, expert response in the exact same language the user used (en, hi, or kn) in the "general_answer" field.

            Output format MUST be strictly JSON (no markdown formatting, no explanation):
            {{
                "intent": "price" | "msp" | "buyer" | "dealer" | "weather" | "scheme" | "general",
                "commodity": "Maize" | "Wheat" | "Paddy (Rice)" | "Soyabean" | "Onion" | "Tomato" | null,
                "state": "State Name" | null,
                "district": "District Name" | null,
                "language": "en" | "hi" | "kn",
                "general_answer": "Expert response to the user's general query in their language" | null,
                "raw_query": "original input text"
            }}
            
            Input Text: "{text}"
            """
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=8)
            if response.status_code == 200:
                res_data = response.json()
                content_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(content_text.strip())
            else:
                print(f"Gemini API returned error code {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None

    @classmethod
    def parse_query(cls, text: str) -> Dict[str, Any]:
        """Entrypoint for parsing query text. Falls back to rules if API key is not present."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            parsed = cls.parse_query_with_llm(text, api_key)
            if parsed:
                return parsed
        return cls.parse_query_rule_based(text)

    @staticmethod
    def speech_to_text(audio_bytes: bytes) -> str:
        """Simulate Speech-to-Text (e.g. Whisper API) for audio voice messages"""
        # In a real setup, we would upload audio_bytes to Whisper API.
        # Here we mock a successful transcription based on dummy files or returns
        return "ಇವತ್ತು ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಜೋಳದ ರೇಟ್ ಎಷ್ಟು"  # Mock default for testing
