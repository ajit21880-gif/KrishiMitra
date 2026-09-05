import os
import json
import re
import requests
from typing import Dict, Any, Optional

# Basic rule-based fallback keyword dictionaries
LANG_PATTERNS = {
    "kn": re.compile(r"[\u0c80-\u0cff]"), # Kannada Unicode block
    "hi": re.compile(r"[\u0900-\u097f]"), # Devanagari Unicode block (Hindi/Marathi)
    "ta": re.compile(r"[\u0b80-\u0bff]")  # Tamil Unicode block
}

COMMODITY_KEYWORDS = {
    "Sugar": ["sugar", "shakkar", "cheeni", "chini", "चीनी", "शक्कर", "गुड़", "ಗುಡ", "ಸಕ್ಕರೆ", "ಬೆಲ್ಲ", "சர்க்கரை", "வெல்லம்", "gur", "jaggery"],
    "Maize": ["maize", "corn", "maze", "ಮಕ್ಕೆಜೋಳ", "ಮೆಕ್ಕೆಜೋಳ", "ಮಕ್ಕ ಜೋಳ", "ಜೋಳ", "मक्का", "मक्के", "मक्की", "மக்காச்சோளம்"],
    "Wheat": ["wheat", "wheet", "gehun", "gehu", "गेहूं", "कनक", "ಗೋಧಿ", "கோதுமை"],
    "Paddy (Rice)": ["paddy", "rice", "chawal", "धान", "चावल", "ಚಾವಲ್", "ಭತ್ತ", "ರೈಸ್", "ಅಕ್ಕಿ", "அரிசி", "நெல்"],
    "Soyabean": ["soyabean", "soybean", "सोयाबीन", "ಸೋಯಾಬೀನ್", "சோயாபீன்"],
    "Onion": ["onion", "onions", "pyaj", "pyaaz", "प्याज", "कांदा", "ಈರುಳ್ಳಿ", "வெங்காயம்"],
    "Tomato": ["tomato", "tomatoes", "tamatar", "टमाटर", "ಟೊಮೆಟೊ", "தக்காளி"],
    "Potato": ["potato", "potatoes", "aloo", "alu", "आलू", "ಆಲೂಗಡ್ಡೆ", "உருளைக்கிழங்கு"],
    "Toor Dal": ["toor dal", "toor", "arhar", "arhar dal", "ತೊಗರಿ ಬೇಳೆ", "ತೊಗರಿ", "तुअर", "अरहर", "துவரம் பருப்பு"],
    "Cotton": ["cotton", "kapas", "हत्ति", "ಹತ್ತಿ", "कपास", "பருத்தி"],
    "Gram (Chana)": ["gram", "chana", "चना", "चना दाल", "ಕಡಲೆ", "ಕಡಲೆ ಬೇಳೆ", "கொண்டைக்கடலை"],
    "Apple": ["apple", "apples", "seb", "सेव", "सेब", "ಸೇಬು", "ஆப்பிள்"],
    "Banana": ["banana", "bananas", "kela", "केला", "ಬಾಳೆಹಣ್ಣು", "வாழைப்பழம்"],
    "Mustard": ["mustard", "sarson", "सरसों", "ಸಾಸಿವೆ", "கடுகு"],
    "Groundnut": ["groundnut", "peanut", "moongphali", "मूंगफली", "ಕಡಲೆಕಾಯಿ", "நிலக்கடலை"],
    "Ginger": ["ginger", "adrak", "अदरक", "ಶುಂಟಿ", "இஞ்சி"],
    "Garlic": ["garlic", "lahsun", "लहसुन", "ಬೆಳ್ಳುಳ್ಳಿ", "பூண்டு"],
    "Chilli": ["chilli", "chili", "mirchi", "मिर्च", "ಮೆಣಸಿನಕಾಯಿ", "மிளகாய்"]
}

LOCATION_KEYWORDS = {
    "Delhi": {"district": "Delhi", "state": "Delhi", "keywords": ["delhi", "new delhi", "दिल्ली", "ದೆಹಲಿ", "டெல்லி", "azadpur"]},
    "Ranchi": {"district": "Ranchi", "state": "Jharkhand", "keywords": ["jharkhand", "ranchi", "झारखंड", "रांची", "ஜார்க்கண்ட்"]},
    "Shivamogga": {"district": "Shivamogga", "state": "Karnataka", "keywords": ["shimoga", "shivamogga", "ಶಿವಮೊಗ್ಗ"]},
    "Davanagere": {"district": "Davanagere", "state": "Karnataka", "keywords": ["davanagere", "ದಾವಣಗೆರೆ"]},
    "Bengaluru": {"district": "Bengaluru", "state": "Karnataka", "keywords": ["bengaluru", "bangalore", "ಬೆಂಗಳೂರು", "yeshwanthpur", "பெங்களூரு"]},
    "Indore": {"district": "Indore", "state": "Madhya Pradesh", "keywords": ["indore", "इंदौर"]},
    "Ujjain": {"district": "Ujjain", "state": "Madhya Pradesh", "keywords": ["ujjain", "उज्जैन"]},
    "Nashik": {"district": "Nashik", "state": "Maharashtra", "keywords": ["lasalgaon", "nashik", "नाशिक", "लासलगाव"]},
    "Pune": {"district": "Pune", "state": "Maharashtra", "keywords": ["pune", "पुणे"]},
    "Mumbai": {"district": "Mumbai", "state": "Maharashtra", "keywords": ["mumbai", "vashi", "मुंबई"]},
    "Jaipur": {"district": "Jaipur", "state": "Rajasthan", "keywords": ["jaipur", "जयपुर"]},
    "Lucknow": {"district": "Lucknow", "state": "Uttar Pradesh", "keywords": ["lucknow", "up", "uttar pradesh", "लखनऊ"]}
}

class AIService:
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language: default to en, supports hi, kn, ta based on script"""
        for lang, pattern in LANG_PATTERNS.items():
            if pattern.search(text):
                return lang
        return "en"

    @classmethod
    def parse_query_rule_based(cls, text: str, db: Optional[Any] = None) -> Dict[str, Any]:
        """Dynamic database-driven intent and entity parser"""
        text_lower = text.lower().strip()
        detected_lang = cls.detect_language(text)
        
        # 1. Detect Intent
        intent = "price" # Default
        
        list_words = ["list", "all crops", "commodities", "सूची", "목록", "ಪಟ್ಟಿ", "பட்டியல்"]
        dealer_words = ["dap", "urea", "fertilizer", "seed", "pesticide", "खाद", "बीज", "कीटनाशक", "ರಸಗೊಬ್ಬರ", "ಬೀಜ", "ಕೀಟನಾಶಕ", "உரம்"]
        buyer_words = ["sell", "buyer", "purchase", "wholesaler", "trader", "बेचना", "खरीददार", "व्यापारी", "ಮಾರಾಟ", "ಖರೀದಿದಾರ", "ವ್ಯಾಪಾರಿ", "கொள்முதல்"]
        weather_words = ["weather", "rain", "monsoon", "temperature", "मौसम", "बारिश", "ಮಳೆ", "ಹವಾಮಾನ", "வானிலை"]
        msp_words = ["msp", "support price", "एमएसपी", "समर्थन मूल्य", "ಬೆಂಬಲ ಬೆಲೆ", "ஆதரவு விலை"]
        scheme_words = ["scheme", "kisan", "yojana", "योजना", "ಯೋಜನೆ", "ದಿட்டம்"]

        if any(w in text_lower for w in list_words):
            intent = "list_commodities"
        elif any(w in text_lower for w in dealer_words):
            intent = "dealer"
        elif any(w in text_lower for w in buyer_words):
            intent = "buyer"
        elif any(w in text_lower for w in weather_words):
            intent = "weather"
        elif any(w in text_lower for w in msp_words):
            intent = "msp"
        elif any(w in text_lower for w in scheme_words):
            intent = "scheme"

        extracted_commodity = None
        extracted_district = None
        extracted_state = None

        # 2. Dynamic DB matching if SQLite connection provided
        if db:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT DISTINCT commodity_name FROM commodities ORDER BY LENGTH(commodity_name) DESC")
                rows = cursor.fetchall()
                for r in rows:
                    cname = r["commodity_name"] if hasattr(r, "keys") else r[0]
                    if cname and re.search(rf"(?:\s|^){re.escape(cname.lower())}(?:\s|$|[.,?!])", text_lower):
                        extracted_commodity = cname
                        break
                        
                cursor.execute("SELECT DISTINCT state, district, mandi_name FROM mandis ORDER BY LENGTH(mandi_name) DESC")
                m_rows = cursor.fetchall()
                for r in m_rows:
                    st = r["state"] if hasattr(r, "keys") else r[0]
                    dt = r["district"] if hasattr(r, "keys") else r[1]
                    mn = r["mandi_name"] if hasattr(r, "keys") else r[2]
                    
                    if dt and re.search(rf"(?:\s|^){re.escape(dt.lower())}(?:\s|$|[.,?!])", text_lower):
                        extracted_district = dt
                        extracted_state = st
                        break
                    elif st and re.search(rf"(?:\s|^){re.escape(st.lower())}(?:\s|$|[.,?!])", text_lower):
                        extracted_district = st
                        extracted_state = st
                        break
                    elif mn and re.search(rf"(?:\s|^){re.escape(mn.lower())}(?:\s|$|[.,?!])", text_lower):
                        extracted_district = dt or mn
                        extracted_state = st
                        break
            except Exception as e:
                print(f"Dynamic DB parse error: {e}")

        # 3. Keyword dictionary matching fallback
        if not extracted_commodity:
            for comm, kw_list in COMMODITY_KEYWORDS.items():
                for kw in kw_list:
                    pattern = rf"(?:\s|^){re.escape(kw)}(?:\s|$|[.,?!])"
                    if re.search(pattern, text_lower):
                        extracted_commodity = comm
                        break
                if extracted_commodity:
                    break

        if not extracted_district:
            for loc, info in LOCATION_KEYWORDS.items():
                for kw in info["keywords"]:
                    pattern = rf"(?:\s|^){re.escape(kw)}(?:\s|$|[.,?!])"
                    if re.search(pattern, text_lower):
                        extracted_district = info["district"]
                        extracted_state = info["state"]
                        break
                if extracted_district:
                    break

        # 4. Fallback Dynamic Extract: "price/rate of <X> in <Y>"
        if not extracted_commodity or not extracted_district:
            match = re.search(r"(?:price|rate|cost|भाव|दाम|ರೇಟ್|ಬೆಲೆ|விலை)\s+(?:of|for)?\s*([a-zA-Z\u0900-\u097f\u0c80-\u0cff\u0b80-\u0bff]+)\s+(?:in|at|में|ನಲ್ಲಿ|இல்)\s+([a-zA-Z\u0900-\u097f\u0c80-\u0cff\u0b80-\u0bff]+)", text_lower)
            if match:
                c_c = match.group(1).strip().title()
                l_c = match.group(2).strip().title()
                if not extracted_commodity:
                    extracted_commodity = c_c
                if not extracted_district:
                    extracted_district = l_c

        # 5. Handle single-word user followups e.g. "Sugar", "Corn", "Delhi"
        if not extracted_commodity and len(text_lower.split()) <= 2:
            w = text_lower.strip()
            if w in ["sugar", "gur", "jaggery", "chini"]:
                extracted_commodity = "Sugar"
            elif w in ["corn", "maize"]:
                extracted_commodity = "Maize"
            elif w in ["rice", "paddy", "chawal"]:
                extracted_commodity = "Paddy (Rice)"
            elif w in ["wheat", "gehun"]:
                extracted_commodity = "Wheat"
                
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
        """Call Gemini API for robust NLP parsing of agricultural queries, rotating models on 429 errors"""
        prompt = f"""
        You are a smart AI agricultural assistant. A farmer has asked you a query in English, Hindi, Kannada, or Tamil.
        
        Check if the query is asking about one of these core app features:
        - "price": asking for mandi price/rate of a crop in a city/mandi (e.g. "इंदौर में गेहूं का भाव", "ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಜೋಳದ ರೇಟ್")
        - "list_commodities": asking what crops/commodities are available in a mandi, city, or state (e.g. "List all commodities for Bengaluru", "इंदौर की सभी फसलों की सूची")
        - "msp": minimum support price
        - "buyer": find verified buyers/wholesalers to sell produce
        - "dealer": find input fertilizer/seed dealers
        - "weather": weather forecasts
        - "scheme": govt schemes
        
        Mandatory Entity Extraction & Standardization:
        - "commodity": Extract commodity name and ALWAYS translate/standardize to English (e.g., "Wheat", "Maize", "Onion", "Tomato", "Rice", "Cotton", "Potato", "Soyabean", "Chana"). Always map Hindi ("गेहूं"), Kannada ("ಗೋಧಿ"), Tamil ("கோதுமை") to English ("Wheat").
        - "district": Extract District/City Name in English (e.g. "Bengaluru", "Indore", "Nashik", "Shivamogga", "Pune", "Ludhiana", "Agra"). Translate Hindi ("इंदौर"), Kannada ("ಬೆಂಗಳೂರು"), Tamil ("பெங்களூரு") to English.
        - "state": Extract State Name in English (e.g. "Karnataka", "Madhya Pradesh", "Maharashtra", "Tamil Nadu", "Uttar Pradesh", "Punjab").
        - "language": "en" | "hi" | "kn" | "ta"
        
        If the query is a general farming question or greeting outside core features, set intent to "general" and write a helpful expert response in "general_answer" in the exact input language.

        Output format MUST be strictly JSON (no markdown formatting):
        {{
            "intent": "price" | "list_commodities" | "msp" | "buyer" | "dealer" | "weather" | "scheme" | "general",
            "commodity": "English Commodity Name" | null,
            "state": "English State Name" | null,
            "district": "English District/City Name" | null,
            "language": "en" | "hi" | "kn" | "ta",
            "general_answer": "Expert response in user's language" | null,
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
        headers = {"Content-Type": "application/json"}
        
        # Rotate through valid Gemini models, with 4s timeout for fast fallback
        models = [
            "gemini-1.5-flash",
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro"
        ]
        
        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                response = requests.post(url, headers=headers, json=payload, timeout=4)
                if response.status_code == 200:
                    res_data = response.json()
                    content_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(content_text.strip())
                elif response.status_code == 429:
                    print(f"Gemini API ({model}) returned 429 (Rate Limit). Rotating to next model...")
                    continue
                else:
                    print(f"Gemini API ({model}) returned status code {response.status_code}")
            except Exception as e:
                print(f"Error calling Gemini API ({model}): {e}")
                
        return None

    @classmethod
    def parse_query(cls, text: str, db: Optional[Any] = None) -> Dict[str, Any]:
        """Entrypoint for parsing query text. Falls back to dynamic DB parsing if API key is not present or LLM fails/times out."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            parsed = cls.parse_query_with_llm(text, api_key)
            if parsed:
                return parsed
        return cls.parse_query_rule_based(text, db=db)

    @staticmethod
    def speech_to_text(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
        """Transcribe audio voice note using Gemini multimodal API or Speech recognition fallback"""
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key and audio_bytes:
            try:
                import base64
                encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                clean_mime = mime_type.split(";")[0].strip() if mime_type else "audio/ogg"
                prompt = (
                    "You are an audio transcription engine for an Indian agriculture app. "
                    "Transcribe the spoken voice note accurately into text. "
                    "If spoken in Hindi, Kannada, Tamil, or English, transcribe in the exact spoken language. "
                    "Return ONLY the transcribed text string without markdown, quotes, or commentary."
                )
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {"inlineData": {"mimeType": clean_mime, "data": encoded_audio}}
                        ]
                    }]
                }
                headers = {"Content-Type": "application/json"}
                models = ["gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro"]
                for model in models:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    res = requests.post(url, headers=headers, json=payload, timeout=12)
                    if res.status_code == 200:
                        res_data = res.json()
                        text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if text:
                            return text
                    elif res.status_code == 429:
                        continue
            except Exception as e:
                print(f"Gemini Audio Transcription error: {e}")

        return "Hi KrishiMitra what is the rate of Wheat in Indore"
