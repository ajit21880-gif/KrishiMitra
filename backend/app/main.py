import os
import sys
import uuid
import re
import json
import jwt
import threading
import time
from datetime import datetime, timedelta
import urllib.parse
import sqlite3
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Helper to auto-load .env file if present
def _load_dotenv():
    env_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.join(os.path.abspath(os.path.dirname(__file__)), ".env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "backend", ".env")
    ]
    for p in env_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("\"'")
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception as e:
                print(f"[Env Loader] Note reading {p}: {e}")
            break

_load_dotenv()

# Add backend/ to Python path to import services correctly
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import get_db_connection, init_db
from app.services.ai_service import AIService
from app.services.bhashini_service import BhashiniService
from app.services.translation_service import TranslationService
from app.services.mandi_service import MandiService
from app.services.whatsapp_service import WhatsAppService
from app.services.enam_service import ENAMService
from app.services.upag_service import UPAgService

# Initialize SQLite tables on startup
init_db()

# Auto-seed database if empty on startup (essential for cloud platforms like Render)
try:
    _conn_check = get_db_connection()
    _c_check = _conn_check.cursor()
    _c_check.execute("SELECT COUNT(*) FROM commodities")
    _comm_cnt = _c_check.fetchone()[0]
    if _comm_cnt < 10:
        print("[Startup] Commodities count is low, running seed_database...")
        from seed_data import seed_database
        seed_database()
    
    # Auto-repair and enrich any missing commodity translations across all 13 languages
    TranslationService.repair_and_enrich_commodities(_conn_check)
    _conn_check.close()
except Exception as _e:
    print(f"[Startup] Error checking/seeding database: {_e}")

def start_background_price_sync():
    def sync_worker():
        time.sleep(10)
        while True:
            api_key = os.environ.get("DATAGOV_API_KEY", "579b464db66ec23bdd000001a40e8a53305b4bcb40409d2efb7d48dc")
            print("[All-India Syncer] Starting chunked background price sync across all Indian mandis...")
            
            rid = "9ef84268-d588-465a-a308-a864a43d0070"
            url = f"https://api.data.gov.in/resource/{rid}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
            
            chunk_size = 100
            total_synced = 0
            max_pages = 20  # 20 pages * 100 = 2,000 live All-India records per sync run!
            
            try:
                conn = get_db_connection()
                cursor = conn.cursor()

                for page in range(max_pages):
                    offset = page * chunk_size
                    params = {
                        "api-key": api_key,
                        "format": "json",
                        "limit": chunk_size,
                        "offset": offset
                    }
                    
                    try:
                        resp = requests.get(url, params=params, headers=headers, timeout=12)
                        if resp.status_code != 200:
                            print(f"[All-India Syncer] Page {page+1} returned HTTP {resp.status_code}, skipping page.")
                            time.sleep(1)
                            continue
                            
                        data = resp.json()
                        records = data.get("records", [])
                        if not records:
                            print(f"[All-India Syncer] Page {page+1} returned 0 records. End of data reached.")
                            break
                            
                        page_synced = 0
                        for r in records:
                            state_gov = str(r.get("state", "")).strip()
                            district_gov = str(r.get("district", state_gov)).strip()
                            market_gov = str(r.get("market", "")).strip()
                            comm_gov = str(r.get("commodity", "")).strip()
                            date_str = str(r.get("arrival_date", datetime.now().date().isoformat())).strip()
                            
                            if "/" in date_str:
                                try:
                                    parts = date_str.split("/")
                                    if len(parts) == 3:
                                        date_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
                                except Exception:
                                    pass

                            try:
                                min_p = float(r.get("min_price", 0))
                                modal_p = float(r.get("modal_price", 0))
                                max_p = float(r.get("max_price", 0))
                            except Exception:
                                continue

                            if not state_gov or not market_gov or not comm_gov or modal_p <= 0:
                                continue

                            # 1. Match or Auto-Create Mandi for ANY Indian state
                            cursor.execute(
                                "SELECT id FROM mandis WHERE state LIKE ? AND (mandi_name LIKE ? OR mandi_name LIKE ?)",
                                (f"%{state_gov}%", f"%{market_gov}%", f"%{market_gov.replace('APMC','').strip()}%")
                            )
                            mandi_row = cursor.fetchone()
                            
                            if not mandi_row:
                                mandi_id = str(uuid.uuid4())
                                cursor.execute(
                                    "INSERT INTO mandis (id, state, district, mandi_name, apmc_code, latitude, longitude) VALUES (?, ?, ?, ?, ?, 0.0, 0.0)",
                                    (mandi_id, state_gov, district_gov or state_gov, market_gov, f"GOV-{uuid.uuid4().hex[:6]}")
                                )
                            else:
                                mandi_id = mandi_row["id"]

                            # 2. Match or Auto-Create Commodity
                            cursor.execute("SELECT id FROM commodities WHERE commodity_name LIKE ?", (f"%{comm_gov}%",))
                            comm_row = cursor.fetchone()
                            
                            if not comm_row:
                                comm_id = str(uuid.uuid4())
                                trans_dict = TranslationService.get_or_create_commodity_translations(comm_gov, enable_network=True)
                                json_local = json.dumps(trans_dict, ensure_ascii=False)
                                cursor.execute(
                                    "INSERT INTO commodities (id, commodity_name, local_name, category) VALUES (?, ?, ?, 'General')",
                                    (comm_id, comm_gov, json_local)
                                )
                            else:
                                comm_id = comm_row["id"]

                            # 3. Upsert Daily Price
                            cursor.execute(
                                "SELECT id FROM daily_prices WHERE mandi_id = ? AND commodity_id = ? AND date = ?",
                                (mandi_id, comm_id, date_str)
                            )
                            existing = cursor.fetchone()
                            
                            if existing:
                                cursor.execute(
                                    "UPDATE daily_prices SET min_price = ?, modal_price = ?, max_price = ?, source = 'AGMARKNET (Synced Live)' WHERE id = ?",
                                    (min_p, modal_p, max_p, existing["id"])
                                )
                            else:
                                cursor.execute(
                                    "INSERT INTO daily_prices (id, mandi_id, commodity_id, date, min_price, modal_price, max_price, source) VALUES (?, ?, ?, ?, ?, ?, ?, 'AGMARKNET (Synced Live)')",
                                    (str(uuid.uuid4()), mandi_id, comm_id, date_str, min_p, modal_p, max_p)
                                )
                            page_synced += 1

                        conn.commit()
                        total_synced += page_synced
                        time.sleep(0.3)

                    except Exception as err:
                        print(f"[All-India Syncer] Error on page {page+1}: {err}")
                        time.sleep(1)

                conn.close()
                print(f"[All-India Syncer] Sync run completed! Total live records updated across India: {total_synced}.")
                
            except Exception as e:
                print(f"[All-India Syncer] Global syncer exception: {e}")
                
            # Run scheduled syncs 3 times daily (every 8 hours = 28,800 seconds)
            time.sleep(28800)

    t = threading.Thread(target=sync_worker, daemon=True)
    t.start()

start_background_price_sync()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

SECRET_KEY = "krishimitra_super_secret_key"
ALGORITHM = "HS256"

# Mock storage for sent OTPs: phone -> OTP
_otp_store = {}

# Simple translations for WhatsApp Responses
RESPONSES = {
    "en": {
        "greeting": "Hello! I am KrishiMitra AI, your agricultural assistant.\nHow can I help you today? You can ask about grain rates (e.g., 'Apple rate in Ahmedabad' or 'Maize rate in Shimoga'), search for fertilizer/seed dealers, or ask about verified buyers.",
        "location_missing": "To get rates, please tell me your state, district, or APMC mandi name.",
        "commodity_missing": "Which commodity are you interested in? (e.g., Apple, Wheat, Maize, Cotton, Onion, Tomato, Soyabean, Chana)",
        "not_found": "Sorry, I could not find any price records for {commodity} in {mandi}. Would you like to check prices for other crops (e.g., {available_crops})?",
        "price_template": "🌾 *{commodity} Rate at {mandi}* ({date})\n\n• Modal Price: *₹{modal}* / quintal\n• Min Price: *₹{min}*\n• Max Price: *₹{max}*\n• Source: {source}\n\n📊 To view 7-day price trends and compare nearby mandis, [Click Here]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *Verified Buyers for {commodity}* in {district}:\n\n{buyer_list}\n\nTo view more verified buyers, [Click Here]({app_url}/?tab=marketplace)",
        "dealer_template": "🚜 *Input Dealers (Fertilizer/Seeds) near {location}*:\n\n{dealer_list}\n\nTo view inventory and dealers, [Click Here]({app_url}/?tab=marketplace)",
        "weather_template": "🌤️ *Weather Forecast for {location}*:\nToday: Sunny, Max 32°C, Min 22°C.\nTomorrow: Light rain expected in the afternoon. Good for sowing.",
        "scheme_template": "📋 *Government Scheme: PM-Kisan Samman Nidhi*\nUnder this scheme, all landholding farmers' families receive ₹6,000 per year in three equal installments.\nVerify your PM-Kisan status at:\nhttps://pmkisan.gov.in/"
    },
    "hi": {
        "greeting": "नमस्ते! मैं कृषिमित्र एआई हूँ, आपका कृषि सहायक।\nआज मैं आपकी क्या मदद कर सकता हूँ? आप अनाज और फलों के भाव (जैसे 'अहमदाबाद में सेब का भाव' या 'इंदौर में गेहूं'), उर्वरक/बीज विक्रेताओं की खोज, या खरीदारों के बारे में पूछ सकते हैं।",
        "location_missing": "भाव जानने के लिए, कृपया मुझे अपना राज्य, जिला या एपीएमसी मंडी का नाम बताएं।",
        "commodity_missing": "आप किस फसल का भाव जानना चाहते हैं? (जैसे सेब, गेहूं, मक्का, कपास, प्याज, टमाटर, सोयाबीन, चना)",
        "not_found": "क्षमा करें, मुझे {mandi} में {commodity} के लिए कोई भाव नहीं मिला। क्या आप अन्य फसलों (जैसे {available_crops}) के भाव जानना चाहते हैं?",
        "price_template": "🌾 *{mandi} में {commodity} का भाव* ({date})\n\n• मॉडल भाव: *₹{modal}* / क्विंटल\n• न्यूनतम भाव: *₹{min}*\n• अधिकतम भाव: *₹{max}*\n• स्रोत: {source}\n\n📊 7 दिनों के भाव के रुझान और मंडियों की तुलना देखने के लिए, [यहाँ क्लिक करें]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} में {commodity} के सत्यापित खरीदार*:\n\n{buyer_list}\n\nअधिक खरीदारों को देखने के लिए, [यहाँ क्लिक करें]({app_url}/?tab=marketplace)",
        "dealer_template": "🚜 *{location} के पास उर्वरक और बीज विक्रेता*:\n\n{dealer_list}\n\nस्टॉक और विक्रेताओं को देखने के लिए, [यहाँ क्लिक करें]({app_url}/?tab=marketplace)",
        "weather_template": "🌤️ *{location} के लिए मौसम का पूर्वानुमान*:\nआज: धूप खिली रहेगी, अधिकतम 32°C, न्यूनतम 22°C.\nकल: दोपहर में हल्की बारिश की संभावना। बुवाई के लिए अच्छा समय है।",
        "scheme_template": "📋 *सरकारी योजना: पीएम-किसान सम्मान निधि*\nइस योजना के तहत भूमिधारक किसान परिवारों को ₹6,000 प्रति वर्ष की वित्तीय सहायता तीन समान किस्तों में मिलती है।\nअपना स्टेटस यहाँ जांचें: https://pmkisan.gov.in/"
    },
    "gu": {
        "greeting": "નમસ્તે! હું કૃષિમિત્ર AI છું, તમારો કૃષિ સહાયક.\nઆજે હું તમને કેવી રીતે મદદ કરી શકું? તમે બજાર ભાવ (જેમ કે 'અમદાવાદમાં સફરજનનો ભાવ' અથવા 'રાજકોટમાં કપાસ'), ખાતર/બિયારણ વિક્રેતાઓ, અથવા ખરીદદારો વિશે પૂછી શકો છો.",
        "location_missing": "ભાવ જાણવા માટે, કૃપા કરીને તમારું રાજ્ય, જિલ્લો અથવા APMC માર્કેટ યાર્ડનું નામ જણાવો.",
        "commodity_missing": "તમે કયા પાક/ફળનો ભાવ જાણવા માંગો છો? (દા.ત. સફરજન, ઘઉં, કપાસ, મગફળી, જીરું, ડુંગળી, બટાકા)",
        "not_found": "ક્ષમા કરશો, મને {mandi} માર્કેટમાં {commodity} માટે કોઈ ભાવ મળ્યો નથી. શું તમે અન્ય પાકો (જેમ કે {available_crops}) ના ભાવ જાણવા માંગો છો?",
        "price_template": "🌾 *{mandi} માં {commodity} નો બજાર ભાવ* ({date})\n\n• મોડલ ભાવ: *₹{modal}* / ક્વિન્ટલ\n• લઘુત્તમ ભાવ: *₹{min}*\n• મહત્તમ ભાવ: *₹{max}*\n• સ્ત્રોત: {source}\n\n📊 7 દિવસના ભાવના વલણો અને સરખામણી જોવા માટે, [અહીં ક્લિક કરો]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} માં {commodity} ના ચકાસાયેલ ખરીદદારો*:\n\n{buyer_list}\n\nવધુ વેપારીઓ માટે માર્કેટપ્લેસ જુઓ:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} નજીક ખાતર અને બિયારણના વિક્રેતાઓ*:\n\n{dealer_list}\n\nસ્ટોક જોવા માટે મુલાકાત લો:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} માટે હવામાન આગાહી*:\nઆજે: તડકો રહેશે, મહત્તમ 32°C, લઘુત્તમ 22°C.\nઆવતીકાલે: બપોરે હળવા વરસાદની શક્યતા. વાવણી માટે સારો સમય છે.",
        "scheme_template": "📋 *સરકારી યોજના: પીએમ-કિસાન સન્માન નિધિ*\nઆ યોજના હેઠળ તમામ જમીનધારક ખેડૂત પરિવારોને વાર્ષિક ₹6,000 ની નાણાકીય સહાય ત્રણ સમાન હપ્તામાં મળે છે.\nતમારું સ્ટેટસ અહીં તપાસો: https://pmkisan.gov.in/"
    },
    "mr": {
        "greeting": "नमस्कार! मी कृषीमित्र AI आहे, आपला शेती सहाय्यक.\nआज मी आपली काय मदत करू शकतो? आपण धान्याचे व फळांचे दर (उदा. 'पुण्यात सफरचंद दर' किंवा 'नाशिकमध्ये कांदा भाव'), खत/बियाणे विक्रेते किंवा खरेदीदारांबद्दल विचारू शकता.",
        "location_missing": "बाजारभाव जाणून घेण्यासाठी, कृपया आपला जिल्हा किंवा APMC बाजार समितीचे नाव सांगा.",
        "commodity_missing": "आपल्याला कोणत्या पिकाचे दर हवे आहेत? (उदा. सफरचंद, कांदा, कापूस, सोयाबीन, गहू, टोमॅटो, हरभरा)",
        "not_found": "क्षमस्व, मला {mandi} बाजार समितीत {commodity} चे दर उपलब्ध झाले नाहीत. आपण इतर पिकांचे (उदा. {available_crops}) दर तपासू इच्छिता?",
        "price_template": "🌾 *{mandi} बाजार समितीत {commodity} चे दर* ({date})\n\n• मॉडेल दर: *₹{modal}* / क्विंटल\n• किमान दर: *₹{min}*\n• कमाल दर: *₹{max}*\n• स्रोत: {source}\n\n📊 ७ दिवसांचे भाव आणि तुलना पाहण्यासाठी, [येथे क्लिक करा]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} मधील {commodity} चे सत्यापित खरेदीदार*:\n\n{buyer_list}\n\nअधिक खरेदीदार पाहण्यासाठी भेट द्या:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} जवळील खत आणि बियाणे विक्रेते*:\n\n{dealer_list}\n\nउपलब्ध साठा पाहण्यासाठी भेट द्या:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} साठी हवामान अंदाज*:\nआज: निरभ्र आकाश, कमाल 32°C, किमान 22°C.\nउद्या: दुपारनंतर हलक्या पावसाची शक्यता. पेरणीसाठी योग्य वेळ.",
        "scheme_template": "📋 *सरकारी योजना: पीएम-किसान सन्मान निधी*\nया योजनेअंतर्गत पात्र शेतकरी कुटुंबांना वर्षाला ₹6,000 ची आर्थिक मदत तीन समान हप्त्यांमध्ये दिली जाते.\nआपले स्टेटस तपासा: https://pmkisan.gov.in/"
    },
    "kn": {
        "greeting": "ನಮಸ್ಕಾರ! ನಾನು ಕೃಷಿಮಿತ್ರ AI, ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ.\nಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು? ನೀವು ಧಾನ್ಯದ ಹಾಗೂ ಹಣ್ಣುಗಳ ದರಗಳು (ಉದಾಹರಣೆಗೆ 'ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಮೆಕ್ಕೆಜೋಳ' ಅಥವಾ 'ಸೇಬು ದರ'), ರಸಗೊಬ್ಬರ/ಬೀಜ ವಿತರಕರ ಹುಡುಕಾಟ ಅಥವಾ ಖರೀದಿದಾರರ ಬಗ್ಗೆ ಕೇಳಬಹುದು.",
        "location_missing": "ದರಗಳನ್ನು ತಿಳಿಯಲು, ದಯವಿಟ್ಟು ನಿಮ್ಮ ಜಿಲ್ಲೆ ಅಥವಾ ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆಯ ಹೆಸರನ್ನು ತಿಳಿಸಿ.",
        "commodity_missing": "ನೀವು ಯಾವ ಬೆಳೆಯ ದರವನ್ನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ? (ಉದಾಹರಣೆಗೆ ಸೇಬು, ಮೆಕ್ಕೆಜೋಳ, ಗೋಧಿ, ತೊಗರಿ ಬೇಳೆ, ಸೋಯಾಬೀನ್, ಈರುಳ್ಳಿ, ಹತ್ತಿ)",
        "not_found": "ಕ್ಷಮಿಸಿ, {mandi} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {commodity} ಬೆಲೆ ವಿವರಗಳು ಲಭ್ಯವಿಲ್ಲ. ನೀವು ಇತರ ಬೆಳೆಗಳ (ಉದಾಹರಣೆಗೆ {available_crops}) ದರಗಳನ್ನು ಪರಿಶೀಲಿಸಲು ಬಯಸುವಿರಾ?",
        "price_template": "🌾 *{mandi} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {commodity} ದರ* ({date})\n\n• ಮಾದರಿ ಬೆಲೆ: *₹{modal}* / ಕ್ವಿಂಟಾಲ್\n• ಕನಿಷ್ಠ ಬೆಲೆ: *₹{min}*\n• ಗರಿಷ್ಠ ಬೆಲೆ: *₹{max}*\n• ಮೂಲ: {source}\n\n📊 ಕಳೆದ 7 ದಿನಗಳ ಬೆಲೆಯ ಏರಿಳಿತಗಳು ಮತ್ತು ಹೋಲಿಕೆಯನ್ನು ನೋಡಲು, [ಇಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} ಜಿಲ್ಲೆಯಲ್ಲಿ {commodity} ಖರೀದಿದಾರರು*:\n\n{buyer_list}\n\nಹೆಚ್ಚಿನ ಖರೀದಿದಾರರ ವಿವರಗಳಿಗಾಗಿ ಭೇಟಿ ನೀಡಿ:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} ಹತ್ತಿರದ ಗೊಬ್ಬರ ಮತ್ತು ಬೀಜದ ಅಂಗಡಿಗಳು*:\n\n{dealer_list}\n\nದಾಸ್ತಾನು ವಿವರಗಳಿಗಾಗಿ ಭೇಟಿ ನೀಡಿ:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ*:\nಇಂದು: ಬಿಸಿಲಿನ ವಾತಾವರಣ, ಗರಿಷ್ಠ 32°C, ಕನಿಷ್ಠ 22°C.\nನಾಳೆ: ಮಧ್ಯಾಹ್ನ ಸಣ್ಣ ಪ್ರಮಾಣದ ಮಳೆ ನಿರೀಕ್ಷಿಸಲಾಗಿದೆ. ಬಿತ್ತನೆಗೆ ಉತ್ತಮ ಸಮಯ.",
        "scheme_template": "📋 *ಸರ್ಕಾರಿ ಯೋಜನೆ: ಪಿಎಂ-ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ*\nಈ ಯೋಜನೆಯಡಿ ಎಲ್ಲಾ ಭೂಹಿಡುವಳಿ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ವರ್ಷಕ್ಕೆ ₹6,000 ಆರ್ಥಿಕ ಸಹಾಯವನ್ನು ಮೂರು ಸಮಾನ ಕಂತುಗಳಲ್ಲಿ ನೀಡಲಾಗುತ್ತದೆ.\nನಿಮ್ಮ ಅರ್ಹತೆಯನ್ನು ಇಲ್ಲಿ ಪರಿಶೀಲಿಸಿ: https://pmkisan.gov.in/"
    },
    "ta": {
        "greeting": "வணக்கம்! நான் கிருஷிமித்ரா AI, உங்கள் வேளாண்மை உதவியாளர்.\nஇன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்? நீங்கள் சந்தை விலைகள் (எ.கா. 'சென்னையில் தக்காளி விலை'), உரம்/விதை விற்பனையாளர்கள் அல்லது வாங்குபவர்களைப் பற்றி கேட்கலாம்.",
        "location_missing": "விலைகளை அறிய, தயவுசெய்து உங்கள் மாவட்டம் அல்லது ஒழுங்குமுறை விற்பனைக்கூடத்தின் பெயரை தெரிவிக்கவும்.",
        "commodity_missing": "எந்தப் பயிரின் விலையை அறிய விரும்புகிறீர்கள்? (எ.கா. ஆப்பிள், நெல், பருத்தி, தக்காளி, வெங்காயம், நிலக்கடலை)",
        "not_found": "மன்னிக்கவும், {mandi} சந்தையில் {commodity} க்கான விலை விவரங்கள் கிடைக்கவில்லை. நீங்கள் மற்ற பயிர்களின் (எ.கா. {available_crops}) விலைகளை அறிய விரும்புகிறீர்களா?",
        "price_template": "🌾 *{mandi} சந்தையில் {commodity} விலை* ({date})\n\n• மாதிரி விலை: *₹{modal}* / குவிண்டால்\n• குறைந்தபட்ச விலை: *₹{min}*\n• அதிகபட்ச விலை: *₹{max}*\n• ஆதாரம்: {source}\n\n📊 7 நாள் விலை மாற்றங்கள் மற்றும் ஒப்பீட்டைப் பார்க்க, [இங்கே கிளிக் செய்யவும்]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} மாவட்டத்தில் {commodity} வாங்குபவர்கள்*:\n\n{buyer_list}\n\nமேலும் வாங்குபவர்களைக் காண சந்தைக்குச் செல்லவும்:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} அருகிலுள்ள உரம் மற்றும் விதை விற்பனையாளர்கள்*:\n\n{dealer_list}\n\nஇருப்பு நிலவரத்தை காண:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} வானிலை முன்னறிவிப்பு*:\nஇன்று: வெயில் நிலவும், அதிகபட்சம் 32°C, குறைந்தபட்சம் 22°C.\nநாளை: பிற்பகலில் லேசான மழைக்கு வாய்ப்பு. விதைப்புக்கு ஏற்ற சூழல்.",
        "scheme_template": "📋 *அரசு திட்டம்: பிஎம்-கிசான் சம்மான் நிதி*\nஇத்திட்டத்தின் கீழ் தகுதியான விவசாய குடும்பங்களுக்கு ஆண்டுக்கு ₹6,000 நிதி உதவி மூன்று தவணைகளாக வழங்கப்படுகிறது.\nவிவரங்களை சரிபார்க்க: https://pmkisan.gov.in/"
    },
    "te": {
        "greeting": "నమస్కారం! నేను కృషిమిత్ర AI, మీ వ్యవసాయ సహాయకుడిని.\nనేను మీకు ఎలా సహాయపడగలను? మీరు మార్కెట్ ధరలు (ఉదా. 'హైదరాబాద్ లో పత్తి ధర'), ఎరువులు/విత్తన డీలర్లు లేదా ధృవీకరించబడిన కొనుగోలుదారుల గురించి అడగవచ్చు.",
        "location_missing": "ధరలను తెలుసుకోవడానికి, దయచేసి మీ జిల్లా లేదా APMC మార్కెట్ పేరును తెలపండి.",
        "commodity_missing": "మీరు ఏ పంట ధర తెలుసుకోవాలనుకుంటున్నారు? (ఉదా. ఆపిల్, పత్తి, వరి, మొక్కజొన్న, మిరప, ఉల్లిపాయ, వేరుశనగ)",
        "not_found": "క్షమించండి, {mandi} మార్కెట్‌లో {commodity} కి సంబంధించిన ధర రికార్డులు లభ్యం కాలేదు. మీరు ఇతర పంటల (ఉదా. {available_crops}) ధరలను చూడాలనుకుంటున్నారా?",
        "price_template": "🌾 *{mandi} మార్కెట్‌లో {commodity} ధర* ({date})\n\n• మోడల్ ధర: *₹{modal}* / క్వింటాల్\n• కనిష్ట ధర: *₹{min}*\n• గరిష్ట ధర: *₹{max}*\n• మూలం: {source}\n\n📊 గత 7 రోజుల ధరల ధోరణి మరియు పోలిక చూడటానికి, [ఇక్కడ క్లిక్ చేయండి]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} లో {commodity} కొనుగోలుదారులు*:\n\n{buyer_list}\n\nమరింత సమాచారం కోసం మార్కెట్‌ప్లేస్‌ను సందర్శించండి:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} సమీపంలోని ఎరువులు మరియు విత్తన డీలర్లు*:\n\n{dealer_list}\n\nస్టాక్ వివరాల కోసం సందర్శించండి:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} వాతావరణ సమాచారం*:\nఈరోజు: ఎండగా ఉంటుంది, గరిష్ట 32°C, కనిష్ట 22°C.\nరేపు: మధ్యాహ్నం తేలికపాటి వర్షం కురిసే అవకాశం ఉంది. విత్తనాలు వేయడానికి అనుకూల సమయం.",
        "scheme_template": "📋 *ప్రభుత్వ పథకం: పీఎం-కిసాన్ సమ్మాన్ నిధి*\nఈ పథకం కింద రైతు కుటుంబాలకు ఏటా ₹6,000 ఆర్థిక సాయం మూడు వాయిదాలలో అందించబడుతుంది.\nస్టేటస్ చెక్ చేయండి: https://pmkisan.gov.in/"
    },
    "ml": {
        "greeting": "നമസ്കാരം! ഞാൻ കൃഷിമിത്ര AI, നിങ്ങളുടെ കാർഷിക സഹായി.\nഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കണം? നിങ്ങൾക്ക് ധാന്യ-വിള വിലകൾ, വളം/വിത്ത് ഡീലർമാർ അല്ലെങ്കിൽ വ്യാപാരികളെ കുറിച്ച് ചോദിക്കാം.",
        "location_missing": "വിലകൾ അറിയാൻ, ദയവായി നിങ്ങളുടെ ജില്ല അല്ലെങ്കിൽ APMC മാർക്കറ്റിന്റെ പേര് വ്യക്തമാക്കുക.",
        "commodity_missing": "ഏത് വിളയുടെ വിലയാണ് അറിയേണ്ടത്? (ഉദാഹരണത്തിന് ആപ്പിൾ, നെല്ല്, കുരുമുളക്, ഏലം, തക്കാളി, ഉള്ളി)",
        "not_found": "ക്ഷമിക്കണം, {mandi} മാർക്കറ്റിൽ {commodity} യുടെ വില വിവരങ്ങൾ ലഭ്യമല്ല. മറ്റ് വിളകളുടെ (ഉദാഹരണത്തിന് {available_crops}) വില പരിശോധിക്കാൻ താൽപ്പര്യമുണ്ടോ?",
        "price_template": "🌾 *{mandi} മാർക്കറ്റിൽ {commodity} വില* ({date})\n\n• മോഡൽ വില: *₹{modal}* / ക്വിന്റൽ\n• കുറഞ്ഞ വില: *₹{min}*\n• കൂടിയ വില: *₹{max}*\n• ഉറവിടം: {source}\n\n📊 7 ദിവസത്തെ വില വിവരങ്ങളും താരതമ്യവും കാണാൻ, [ഇവിടെ ക്ലിക്ക് ചെയ്യുക]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} ജില്ലയിലെ {commodity} വ്യാപാരികൾ*:\n\n{buyer_list}\n\nകൂടുതൽ വിവരങ്ങൾക്ക് മാർക്കറ്റ് പ്ലേസ് സന്ദർശിക്കുക:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} അടുത്തുള്ള വളം-വിത്ത് ഡീലർമാർ*:\n\n{dealer_list}\n\nസ്റ്റോക്ക് അറിയാൻ സന്ദർശിക്കുക:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} കാലാവസ്ഥാ പ്രവചനം*:\nഇന്ന്: വെയിൽ നിറഞ്ഞ കാലാവസ്ഥ, കൂടിയ താപനില 32°C, കുറഞ്ഞത് 22°C.\nനാളെ: ഉച്ചയ്ക്ക് ശേഷം നേരിയ മഴ സാധ്യത.",
        "scheme_template": "📋 *സർക്കാർ പദ്ധതി: പിഎം-കിസാൻ സമ്മാൻ നിധി*\nഈ പദ്ധതി വഴി അർഹരായ കർഷക കുടുംബങ്ങൾക്ക് വർഷം തോറും ₹6,000 ധനസഹായം ലഭിക്കുന്നു.\nസ്റ്റാറ്റസ് പരിശോധിക്കുക: https://pmkisan.gov.in/"
    },
    "pa": {
        "greeting": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਕ੍ਰਿਸ਼ੀਮਿੱਤਰ AI ਹਾਂ, ਤੁਹਾਡਾ ਖੇਤੀ ਸਹਾਇਕ।\nਮੈਂ ਤੁਹਾਡੀ ਕੀ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ? ਤੁਸੀਂ ਮੰਡੀ ਦੇ ਭਾਅ (ਜਿਵੇਂ 'ਖੰਨਾ ਮੰਡੀ ਵਿੱਚ ਕਣਕ ਦਾ ਭਾਅ'), ਖਾਦ/ਬੀਜ ਡੀਲਰਾਂ ਜਾਂ ਖਰੀਦਦਾਰਾਂ ਬਾਰੇ ਪੁੱਛ ਸਕਦੇ ਹੋ।",
        "location_missing": "ਭਾਅ ਜਾਣਨ ਲਈ ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਜ਼ਿਲ੍ਹਾ ਜਾਂ APMC ਮੰਡੀ ਦਾ ਨਾਂ ਦੱਸੋ।",
        "commodity_missing": "ਤੁਸੀਂ ਕਿਸ ਫਸਲ ਦਾ ਭਾਅ ਜਾਣਨਾ ਚਾਹੁੰਦੇ ਹੋ? (ਜਿਵੇਂ ਕਣਕ, ਝੋਨਾ, ਮੱਕੀ, ਆਲੂ, ਨਰਮਾ, ਬਾਜਰਾ)",
        "not_found": "ਮਾਫ਼ ਕਰਨਾ, ਮੈਨੂੰ {mandi} ਵਿੱਚ {commodity} ਦਾ ਕੋਈ ਭਾਅ ਨਹੀਂ ਮਿਲਿਆ। ਕੀ ਤੁਸੀਂ ਹੋਰ ਫਸਲਾਂ (ਜਿਵੇਂ {available_crops}) ਦੇ ਭਾਅ ਜਾਣਨਾ ਚਾਹੁੰਦੇ ਹੋ?",
        "price_template": "🌾 *{mandi} ਵਿੱਚ {commodity} ਦਾ ਭਾਅ* ({date})\n\n• ਮਾਡਲ ਭਾਅ: *₹{modal}* / ਕੁਇੰਟਲ\n• ਘੱਟੋ-ਘੱਟ ਭਾਅ: *₹{min}*\n• ਵੱਧ ਤੋਂ ਵੱਧ ਭਾਅ: *₹{max}*\n• ਸਰੋਤ: {source}\n\n📊 7 ਦਿਨਾਂ ਦੇ ਭਾਅ ਅਤੇ ਤੁਲਨਾ ਵੇਖਣ ਲਈ, [ਇੱਥੇ ਕਲਿੱਕ ਕਰੋ]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} ਵਿੱਚ {commodity} ਦੇ ਖਰੀਦਦਾਰ*:\n\n{buyer_list}\n\nਹੋਰ ਖਰੀਦਦਾਰਾਂ ਲਈ ਮਾਰਕਿਟਪਲੇਸ ਵੇਖੋ:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} ਨੇੜੇ ਖਾਦ ਅਤੇ ਬੀਜ ਵਿਕਰੇਤਾ*:\n\n{dealer_list}\n\nਸਟਾਕ ਵੇਖਣ ਲਈ ਜਾਓ:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} ਲਈ ਮੌਸਮ ਜਾਣਕਾਰੀ*:\nਅੱਜ: ਧੁੱਪ ਰਹੇਗੀ, ਤਾਪਮਾਨ 32°C ਤੋਂ 22°C.\nਕੱਲ੍ਹ: ਦੁਪਹਿਰ ਬਾਅਦ ਹਲਕੀ ਬਾਰਿਸ਼ ਦੀ ਸੰਭਾਵਨਾ।",
        "scheme_template": "📋 *ਸਰਕਾਰੀ ਸਕੀਮ: ਪੀਐਮ-ਕਿਸਾਨ ਸਨਮਾਨ ਨਿਧੀ*\nਇਸ ਯੋਜਨਾ ਤਹਿਤ ਕਿਸਾਨ ਪਰਿਵਾਰਾਂ ਨੂੰ ਹਰ ਸਾਲ ₹6,000 ਦੀ ਵਿੱਤੀ ਸਹਾਇਤਾ ਮਿਲਦੀ ਹੈ।\nਸਟੇਟਸ ਜਾਂਚੋ: https://pmkisan.gov.in/"
    },
    "bn": {
        "greeting": "নমস্কার! আমি কৃষিমিত্র এআই, আপনার কৃষি সহকারী।\nআজ আপনাকে কীভাবে সাহায্য করতে পারি? আপনি ফসলের বাজার দর (যেমন 'আপেল বা ধানের দর'), সার ও বীজ ডিলার বা বিশ্বস্ত ক্রেতাদের সন্ধান করতে পারেন।",
        "location_missing": "দর জানতে দয়া করে আপনার রাজ্য, জেলা বা এপিএমসি মান্ডির নাম জানান।",
        "commodity_missing": "আপনি কোন ফসলের দর জানতে চান? (যেমন আপেল, ধান, গম, আলু, পেঁয়াজ, পাট, ভুট্টা)",
        "not_found": "দুঃখিত, {mandi} মান্ডিতে {commodity} এর কোনো দর পাওয়া যায়নি। আপনি কি অন্য কোনো ফসলের (যেমন {available_crops}) দর জানতে চান?",
        "price_template": "🌾 *{mandi} মান্ডিতে {commodity} এর দর* ({date})\n\n• মডেল দর: *₹{modal}* / কুইন্টাল\n• সর্বনিম্ন দর: *₹{min}*\n• সর্বোচ্চ দর: *₹{max}*\n• উৎস: {source}\n\n📊 ৭ দিনের দর ও তুলনা দেখতে, [এখানে ক্লিক করুন]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} জেলায় {commodity} এর ক্রেতাগণ*:\n\n{buyer_list}\n\nআরও ক্রেতা খুঁজতে দেখুন:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} এর কাছে সার ও বীজ বিক্রেতা*:\n\n{dealer_list}\n\nস্টক জানতে দেখুন:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} এর আবহাওয়া পূর্বাভাস*:\nআজ: রৌদ্রোজ্জ্বল, সর্বোচ্চ ৩২°C, সর্বনিম্ন ২২°C.\nকাল: বিকেলে হালকা বৃষ্টির সম্ভাবনা রয়েছে।",
        "scheme_template": "📋 *সরকারি প্রকল্প: পিএম-কিসান সম্মান নিধি*\nএই প্রকল্পের আওতায় কৃষক পরিবারগুলিকে বছরে ₹৬,০০০ আর্থিক সহায়তা দেওয়া হয়।\nস্ট্যাটাস যাচাই করুন: https://pmkisan.gov.in/"
    },
    "or": {
        "greeting": "ନମସ୍କାର! ମୁଁ କୃଷିମିତ୍ର AI, ଆପଣଙ୍କ କୃଷି ସହାୟକ।\nଆଜି ମୁଁ ଆପଣଙ୍କୁ କିପରି ସାହାଯ୍ୟ କରିପାରିବି? ଆପଣ ମଣ୍ଡି ଦର (ଯଥା: 'ଭୁବନେଶ୍ୱରରେ ଧାନର ଦର'), ସାର/ବିହନ ଡିଲର କିମ୍ବା ବ୍ୟବସାୟୀଙ୍କ ବିଷୟରେ ପଚାରି ପାରିବେ।",
        "location_missing": "ଦର ଜାଣିବା ପାଇଁ ଦୟାକରି ଆପଣଙ୍କ ଜିଲ୍ଲା କିମ୍ବା ମଣ୍ଡିର ନାମ ଜଣାନ୍ତୁ।",
        "commodity_missing": "ଆପଣ କେଉଁ ଫସଲର ଦର ଜାଣିବାକୁ ଚାହାଁନ୍ତି? (ଯଥା: ସେଓ, ଧାନ, ଗହମ, ଆଳୁ, ପିଆଜ, ମକା)",
        "not_found": "ଦୁଃଖିତ, {mandi} ମଣ୍ଡିରେ {commodity} ପାଇଁ କୌଣସି ଦର ରେକର୍ଡ ମିଳିଲା ନାହିଁ। ଆପଣ ଅନ୍ୟ କୌଣସି ଫସଲ (ଯଥା: {available_crops}) ର ଦର ଜାଣିବାକୁ ଚାହାଁନ୍ତି କି?",
        "price_template": "🌾 *{mandi} ମଣ୍ଡିରେ {commodity} ର ଦର* ({date})\n\n• ମଡେଲ ଦର: *₹{modal}* / କ୍ୱିଣ୍ଟାଲ\n• ସର୍ବନିମ୍ନ ଦର: *₹{min}*\n• ସର୍ବାଧିକ ଦର: *₹{max}*\n• ଉତ୍ସ: {source}\n\n📊 ବିଗତ ୭ ଦିନର ଦର ଏବଂ ତୁଳନା ଦେଖିବା ପାଇଁ, [ଏଠାରେ କ୍ଲିକ୍ କରନ୍ତୁ]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} ରେ {commodity} ର କ୍ରେତାଗଣ*:\n\n{buyer_list}\n\nଅଧିକ କ୍ରେତାଙ୍କ ବିବରଣୀ ପାଇଁ ବଜାର ଦେଖନ୍ତୁ:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} ନିକଟରେ ଥିବା ସାର ଏବଂ ବିହନ ଦୋକାନ*:\n\n{dealer_list}\n\nଷ୍ଟକ୍ ଦେଖିବା ପାଇଁ:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} ପାଣିପାଗ ପୂର୍ବାନୁମାନ*:\nଆଜି: ଖରାଟିଆ ରହିବ, ସର୍ବାଧିକ ୩୨°C, ସର୍ବନିମ୍ନ ୨୨°C।\nକାଲି: ଅପରାହ୍ନରେ ସାମାନ୍ୟ ବର୍ଷା ସମ୍ଭାବନା।",
        "scheme_template": "📋 *ସରକାରୀ ଯୋଜନା: ପିଏମ-କିଷାନ ସମ୍ମାନ ନିଧି*\nଏହି ଯୋଜନା ଅଧୀନରେ ଚାଷୀ ପରିବାରଙ୍କୁ ବାର୍ଷିକ ₹୬,୦୦୦ ଆର୍ଥିକ ସହାୟତା ତିନୋଟି କିସ୍ତିରେ ପ୍ରଦାନ କରାଯାଏ।\nଯାଞ୍ଚ କରନ୍ତୁ: https://pmkisan.gov.in/"
    },
    "as": {
        "greeting": "নমস্কাৰ! মই কৃষিমিত্ৰ AI, আপোনাৰ কৃষি সহায়ক।\nআজি মই আপোনাক কেনেকৈ সহায় কৰিব পাৰোঁ? আপুনি বজাৰৰ দৰ (যেনে 'গুৱাহাটীত আলুৰ দাম'), সাৰ/বীজৰ ডিলাৰ বা ক্ৰেতাসকলৰ বিষয়ে সুধিব পাৰে।",
        "location_missing": "দৰ জানিবলৈ অনুগ্ৰহ কৰি আপোনাৰ জিলা বা এপিএমচি মণ্ডিৰ নাম কওক।",
        "commodity_missing": "আপুনি কোনটো শস্যৰ দৰ জানিব বিচাৰে? (যেনে আপেল, ধান, ঘেঁহু, আলু, পিয়াঁজ, চাহ, মাকৈ)",
        "not_found": "ক্ষমা কৰিব, {mandi} মণ্ডিত {commodity} ৰ কোনো দৰ পোৱা নগ'ল। আপুনি আন শস্যৰ (যেনে {available_crops}) দৰ জানিব বিচাৰে নেকি?",
        "price_template": "🌾 *{mandi} মণ্ডিত {commodity} ৰ দৰ* ({date})\n\n• মডেল দৰ: *₹{modal}* / কুইণ্টল\n• সৰ্বনিম্ন দৰ: *₹{min}*\n• সৰ্বোচ্চ দৰ: *₹{max}*\n• উৎস: {source}\n\n📊 বিগত ৭ দিনৰ দৰ আৰু তুলনা চাবলৈ, [ইয়াত ক্লিক কৰক]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} জিলাত {commodity} ৰ ক্ৰেতাসকল*:\n\n{buyer_list}\n\nঅধিক জানিবলৈ বজাৰ পৃষ্ঠালৈ যাওক:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} ৰ ওচৰৰ সাৰ আৰু বীজ বিক্ৰেতা*:\n\n{dealer_list}\n\nষ্টক জানিবলৈ চাওক:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} ৰ বতৰৰ আগজাননী*:\nআজি: ৰৌদ্ৰোজ্জ্বল, সৰ্বোচ্চ ৩২°C, সৰ্বনিম্ন ২২°C।\nকাইলৈ: আবেলি পাতলীয়া বৰষুণৰ সম্ভাৱনা আছে।",
        "scheme_template": "📋 *চৰকাৰী আঁচনি: পিএম-কিষাণ সন্মান নিধি*\nএই আঁচনিৰ অধীনত কৃষক পৰিয়ালসমূহক বছৰি ₹৬,০০০ আৰ্থিক সাহায্য তিনিটা কিস্তিত প্ৰদান কৰা হয়।\nস্থিতি পৰীক্ষা কৰক: https://pmkisan.gov.in/"
    },
    "ks": {
        "greeting": "سلام! بٕہ چُھس کرٛشۍمِتَر AI، تُہُند کھیتی باڑی مددگار۔\nآز کِتھ پٲٹھۍ ہٮ۪کاو تُہنٛز مَدَتھ کٔرِتھ؟ تُہۍ ہٮ۪کِو منڈی قٟمَتھ (مِثال: 'سوپور مَنٛز ژوٗنٛٹھ ہُنٛد قٟمَتھ')، کھاد یا بیٚول وِکنے والٮ۪ن مُتعلِق پرِژھِتھ۔",
        "location_missing": "قٟمَتھ زاننہٕ باپتھ مہر Hercules مہربٲنی کٔرِتھ پنُن ضِلہٕ یا منڈی ناو وٲنِو۔",
        "commodity_missing": "تُہۍ کَمِہ فَصلُک قٟمَتھ زانُن چِھو یَژھان؟ (مِثال: ژوٗنٛٹھ، دانۍ، گَنَم، آلوٚو، گنڈٕ، کونٛگ، ڈوٗن)",
        "not_found": "معاف کٔرِو، {mandi} مَنٛز {commodity} ہُنٛد کانٛہہ قٟمَتھ مِلیو نہٕ۔",
        "price_template": "🌾 *{mandi} مَنٛز {commodity} ہُنٛد قٟمَتھ* ({date})\n\n• عام قٟمَتھ: *₹{modal}* / کوئنٹل\n• کم ترین قٟمَتھ: *₹{min}*\n• زیٛادٕ قٟمَتھ: *₹{max}*\n• ذٔریعہٕ: {source}\n\n📊 ۷ دۄہَن ہُنٛد قٟمَتھ تہٕ تقابل وُچھنہٕ باپتھ، [یَتھ کِلِک کٔرِو]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} مَنٛز {commodity} ہِندن خریدارن ہِنٛز فِہرِست*:\n\n{buyer_list}\n\nباقی خریدار وُچھنہٕ باپتھ مارکیٹ وزِٹ کٔرِو:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} نزدیٖک کھاد تہٕ بیٚول وِکنے وٲلۍ*:\n\n{dealer_list}\n\nسٹاک وُچھنہٕ باپتھ:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} خٲطرٕ موسمٕچ پینشن گوئی*:\nآز: تاپ آسان، زیٛادٕ کھوتہٕ زیٛادٕ ۲۴°C، کم کھوتہٕ کم ۱۲°C।\nپگاہ: شامس ہلکہٕ رُد گژھنُک اِمکان।",
        "scheme_template": "📋 *سرکٲرۍ سکیٖم: پی ایم-کسان سمان ندھی*\nاَتھ سکیٖمہِ تَحَت چُھ زمیٖندارن ہَر ؤری ₹۶,০০০ مَدَتھ ترٛٮ۪ن قِسطَن مَنٛز مِلان۔\nجانچ کٔرِو: https://pmkisan.gov.in/"
    }
}

APP_URL = os.environ.get("FRONTEND_APP_URL", "https://krishi-mitra-crestsubarn.vercel.app")

def generate_chatbot_response(query_text: str, db: sqlite3.Connection) -> str:
    cursor = db.cursor()
    
    # 1. Parse text using AI Service
    parsed = AIService.parse_query(query_text, db=db)
    lang = parsed.get("language", "en")
    if lang not in RESPONSES:
        lang = "en"
        
    texts = RESPONSES[lang]
    intent = parsed.get("intent")
    
    # Check activation trigger keywords
    q_clean = query_text.lower().strip()
    is_activation_phrase = any(kw in q_clean for kw in ["krishimitra", "krishi mitra", "कृषिमित्र", "ಕೃಷಿಮಿತ್ರ", "கிருஷிமித்ரா", "કૃષિમિત્ર", "కృషిమిత్ర", "കൃഷിമിത്ര", "ਕ੍ਰਿਸ਼ੀਮਿੱਤਰ", "কৃষিমিত্র", "କୃଷିମିତ୍ର", "কৃষিমিত্ৰ", "کرٛشۍمِتَر"])
    is_simple_greeting = q_clean in ["hello", "hi", "hey", "hi!", "hello!", "hey!", "namaste", "नमस्ते", "ನಮಸ್ಕಾರ", "வணக்கம்"]

    if is_activation_phrase:
        # Check if query contains content beyond activation phrase / greeting
        stripped = q_clean
        for kw in ["krishimitra", "krishi mitra", "कृषिमित्र", "ಕೃಷಿಮಿತ್ರ", "கிருஷிமித்ரா", "hi", "hello", "hey", "namaste", "नमस्ते", "ನಮಸ್ಕಾರ", "வணக்கம்"]:
            stripped = stripped.replace(kw, "").strip()
        stripped = re.sub(r'^[,\s\.!\?]+|[,\s\.!\?]+$', '', stripped).strip()
        
        if not stripped or len(stripped) <= 2:
            return texts["greeting"]
        # If user asked a question along with activation phrase, continue to process intent
        
    if is_simple_greeting:
        return "" # Completely silent for plain Hi/Hello - only react when Hi KrishiMitra is said

    # Process Intent
    if intent == "list_commodities":
        mandi_search = parsed.get("mandi") or parsed.get("district") or parsed.get("state") or "Bengaluru"
        cursor.execute(
            "SELECT DISTINCT c.commodity_name FROM daily_prices dp JOIN mandis m ON dp.mandi_id = m.id JOIN commodities c ON dp.commodity_id = c.id WHERE m.state LIKE ? OR m.district LIKE ? OR m.mandi_name LIKE ? LIMIT 10",
            (f"%{mandi_search}%", f"%{mandi_search}%", f"%{mandi_search}%")
        )
        comm_rows = cursor.fetchall()
        if not comm_rows:
            cursor.execute("SELECT commodity_name FROM commodities LIMIT 8")
            comm_rows = cursor.fetchall()
            
        crop_names = ", ".join([r["commodity_name"] for r in comm_rows])
        if lang == "hi":
            return f"🌾 {mandi_search} में उपलब्ध प्रमुख फसलें हैं: {crop_names}।"
        elif lang == "kn":
            return f"🌾 {mandi_search} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಲಭ್ಯವಿರುವ ಪ್ರಮುಖ ಬೆಳೆಗಳು: {crop_names}."
        elif lang == "ta":
            return f"🌾 {mandi_search} சந்தையில் கிடைக்கும் பயிர்கள்: {crop_names}."
        elif lang == "gu":
            return f"🌾 {mandi_search} બજારમાં ઉપલબ્ધ મુખ્ય પાકો: {crop_names}."
        elif lang == "mr":
            return f"🌾 {mandi_search} बाजारपेठेत उपलब्ध मुख्य पिके: {crop_names}."
        elif lang == "te":
            return f"🌾 {mandi_search} మార్కెట్లో లభించే ప్రధాన పంటలు: {crop_names}."
        elif lang == "or":
            return f"🌾 {mandi_search} ମଣ୍ଡିରେ ଉପଲବ୍ଧ ପ୍ରମୁଖ ଫସଲ: {crop_names}।"
        elif lang == "as":
            return f"🌾 {mandi_search} মণ্ডিত উপলব্ধ প্ৰধান শস্য: {crop_names}।"
        elif lang == "bn":
            return f"🌾 {mandi_search} বাজারে উপলব্ধ প্রধান ফসল: {crop_names}।"
        elif lang == "pa":
            return f"🌾 {mandi_search} ਮੰਡੀ ਵਿੱਚ ਉਪਲਬਧ ਮੁੱਖ ਫਸਲਾਂ: {crop_names}।"
        elif lang == "ks":
            return f"🌾 {mandi_search} منڈی مَنٛز دٔستِیاب فَصلَن ہِنٛز فِہرِست: {crop_names}۔"
        else:
            return f"🌾 Prices for the following commodities are currently available in {mandi_search}: {crop_names}."

    elif intent == "price":
        commodity = parsed.get("commodity")
        district = parsed.get("district") or parsed.get("state")
        
        if not commodity:
            return texts["commodity_missing"]
        if not district:
            return texts["location_missing"]
            
        # Try to find a matching mandi
        cursor.execute("SELECT * FROM mandis WHERE district LIKE ? LIMIT 1", (f"%{district}%",))
        mandi = cursor.fetchone()
        
        if not mandi:
            # Fallback to search state
            cursor.execute("SELECT * FROM mandis WHERE state LIKE ? LIMIT 1", (f"%{district}%",))
            mandi = cursor.fetchone()
                
        mandi_name = mandi["mandi_name"] if mandi else district
        state_name = mandi["state"] if mandi else (parsed.get("state") or district)
        
        price_info = MandiService.get_mandi_price(db, state_name, district, mandi_name, commodity)
        
        if price_info.get("modal_price", 0) == 0:
            m_id = mandi["id"] if mandi else None
            alt_crops_list = []
            if m_id:
                cursor.execute(
                    "SELECT DISTINCT c.commodity_name, c.local_name FROM daily_prices dp JOIN commodities c ON dp.commodity_id = c.id WHERE dp.mandi_id = ? LIMIT 4",
                    (m_id,)
                )
                rows = cursor.fetchall()
                for r in rows:
                    c_n = r["commodity_name"] if hasattr(r, "keys") else r[0]
                    l_json = r["local_name"] if hasattr(r, "keys") else r[1]
                    if l_json and lang != "en":
                        try:
                            loc_dict = json.loads(l_json) if isinstance(l_json, str) else l_json
                            c_n = loc_dict.get(lang, c_n)
                        except Exception:
                            pass
                    alt_crops_list.append(c_n)
            alt_crops_str = ", ".join(alt_crops_list) if alt_crops_list else "Wheat, Paddy, Tomato, Onion"

            # Localize commodity name if possible
            commodity_display = commodity
            if lang != "en":
                sunflower_map = {
                    "hi": "सूरजमुखी", "gu": "સૂર્યમુખી", "or": "ସୂର୍ଯ୍ୟମୁଖୀ", "kn": "ಸೂರ್ಯಕಾಂತಿ",
                    "mr": "सूर्यफूल", "ta": "சூரியகாந்தி", "te": "సూర్యముఖి", "bn": "সূর্যমুখী",
                    "as": "সূৰ্যমুখী", "pa": "ਸੂਰਜਮੁਖੀ", "ml": "സൂര്യകാന്തി", "ks": "سُورج مۆکھی"
                }
                if commodity in sunflower_map and lang in sunflower_map:
                    commodity_display = sunflower_map[lang]
                else:
                    cursor.execute("SELECT local_name FROM commodities WHERE commodity_name LIKE ? LIMIT 1", (f"%{commodity}%",))
                    comm_row = cursor.fetchone()
                    if comm_row and comm_row["local_name"]:
                        try:
                            c_dict = json.loads(comm_row["local_name"]) if isinstance(comm_row["local_name"], str) else comm_row["local_name"]
                            commodity_display = c_dict.get(lang, commodity)
                        except Exception:
                            pass

            return texts["not_found"].format(commodity=commodity_display, mandi=mandi_name, available_crops=alt_crops_str)
            
        mandi_enc = urllib.parse.quote(mandi_name)
        comm_enc = urllib.parse.quote(commodity)
        
        res_msg = texts["price_template"].format(
            commodity=commodity,
            mandi=mandi_name,
            date=price_info.get("date"),
            modal=price_info.get("modal_price"),
            min=price_info.get("min_price"),
            max=price_info.get("max_price"),
            source=price_info.get("source"),
            app_url=APP_URL,
            mandi_encoded=mandi_enc,
            commodity_encoded=comm_enc
        )

        if price_info.get("is_enam"):
            arrivals = price_info.get("arrivals_qty", 0)
            variety = price_info.get("variety", "")
            grade = price_info.get("grade", "")
            if lang == "gu":
                res_msg += f"\n\n⚡ *e-NAM સંકલિત મંડી* (આવક: {arrivals} ક્વિન્ટલ | {variety} - {grade})"
            elif lang == "hi":
                res_msg += f"\n\n⚡ *e-NAM एकीकृत मंडी* (आवक: {arrivals} क्विंटल | {variety} - {grade})"
            elif lang == "kn":
                res_msg += f"\n\n⚡ *ಇ-ನಾಮ್ ನೋಂದಾಯಿತ ಮಾರುಕಟ್ಟೆ* (ಆವಕ: {arrivals} ಕ್ವಿಂಟಾಲ್ | {variety} - {grade})"
            elif lang == "mr":
                res_msg += f"\n\n⚡ *e-NAM इलेक्ट्रॉनिक बाजार* (आवक: {arrivals} क्विंटल | {variety} - {grade})"
            elif lang == "ta":
                res_msg += f"\n\n⚡ *e-NAM ஒருங்கிணைந்த சந்தை* (வரத்து: {arrivals} குவிண்டால் | {variety} - {grade})"
            elif lang == "or":
                res_msg += f"\n\n⚡ *e-NAM ସଂଯୁକ୍ତ ମଣ୍ଡି* (ଆଗମନ: {arrivals} କ୍ୱିଣ୍ଟାଲ | {variety} - {grade})"
            elif lang == "as":
                res_msg += f"\n\n⚡ *e-NAM সংযোগী মণ্ডি* (আমদানি: {arrivals} কুইন্টল | {variety} - {grade})"
            elif lang == "bn":
                res_msg += f"\n\n⚡ *e-NAM সংযুক্ত মান্ডি* (আমদানি: {arrivals} কুইন্টাল | {variety} - {grade})"
            elif lang == "te":
                res_msg += f"\n\n⚡ *e-NAM సమగ్ర మార్కెట్* (రాక: {arrivals} క్వింటాళ్లు | {variety} - {grade})"
            elif lang == "pa":
                res_msg += f"\n\n⚡ *e-NAM ਏਕੀਕ੍ਰਿਤ ਮੰਡੀ* (ਆਮਦ: {arrivals} ਕੁਇੰਟਲ | {variety} - {grade})"
            elif lang == "ml":
                res_msg += f"\n\n⚡ *e-NAM ഏകീകൃത വിപണി* (വരവ്: {arrivals} ക്വിന്റൽ | {variety} - {grade})"
            elif lang == "ks":
                res_msg += f"\n\n⚡ *e-NAM مَنٛڈی* (آمد: {arrivals} قُوِنٹل | {variety} - {grade})"
            else:
                res_msg += f"\n\n⚡ *e-NAM Unified Market* (Arrivals: {arrivals} Qtl | Variety: {variety} - {grade})"
        
        return res_msg

    elif intent == "advisory":
        commodity = parsed.get("commodity")
        state = parsed.get("state") or parsed.get("district") or "All India"
        if not commodity:
            return texts["commodity_missing"]
            
        outlook = UPAgService.get_macro_outlook(db, state, commodity)
        trend_sign = "+" if outlook["production_trend_pct"] >= 0 else ""
        
        if lang == "hi":
            return (
                f"📊 *{state} में {commodity} का बाज़ार पूर्वानुमान (UPAg)*:\n\n"
                f"• आपूर्ति परिदृश्य: *{outlook['supply_outlook']}* ({trend_sign}{outlook['production_trend_pct']}%)\n"
                f"• मंडी थोक भाव: *₹{outlook['wholesale_price_avg']}/किग्रा*\n"
                f"• उपभोक्ता खुदरा भाव: *₹{outlook['retail_price_avg']}/किग्रा* (मार्जिन: {outlook['retail_spread_pct']}%)\n"
                f"• कृषि जलवायु (CWWG): वर्षा विचलन {outlook['rainfall_departure_pct']}%\n\n"
                f"💡 *सलाह*: {outlook['advisory_recommendation']}\n\n"
                f"📊 विस्तृत आउटलुक देखने के लिए, [यहाँ क्लिक करें]({APP_URL}/?tab=mandi&commodity={urllib.parse.quote(commodity)})"
            )
        elif lang == "kn":
            return (
                f"📊 *{state} ನಲ್ಲಿ {commodity} ಮಾರುಕಟ್ಟೆ ಮುನ್ನೋಟ (UPAg)*:\n\n"
                f"• ಪೂರೈಕೆ ಸ್ಥಿತಿ: *{outlook['supply_outlook']}* ({trend_sign}{outlook['production_trend_pct']}%)\n"
                f"• ಎಪಿಎಂಸಿ ಸಗಟು ದರ: *₹{outlook['wholesale_price_avg']}/ಕೆಜಿ*\n"
                f"• ನಗರ ಚಿಲ್ಲರೆ ದರ: *₹{outlook['retail_price_avg']}/ಕೆಜಿ* (ಮಾರ್ಜಿನ್: {outlook['retail_spread_pct']}%)\n\n"
                f"💡 *ಸಲಹೆ*: {outlook['advisory_recommendation']}\n\n"
                f"📊 ವಿವರಗಳನ್ನು ನೋಡಲು, [ಇಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ]({APP_URL}/?tab=mandi&commodity={urllib.parse.quote(commodity)})"
            )
        elif lang == "gu":
            return (
                f"📊 *{state} માં {commodity} નો બજાર અંદાજ (UPAg)*:\n\n"
                f"• પુરવઠા સ્થિતિ: *{outlook['supply_outlook']}* ({trend_sign}{outlook['production_trend_pct']}%)\n"
                f"• મંડી જથ્થાબંધ ભાવ: *₹{outlook['wholesale_price_avg']}/કિલો*\n"
                f"• શહેર છૂટક ભાવ: *₹{outlook['retail_price_avg']}/કિલો* (માર્જિન: {outlook['retail_spread_pct']}%)\n\n"
                f"💡 *સલાહ*: {outlook['advisory_recommendation']}\n\n"
                f"📊 વિગતવાર માહિતી જોવા માટે, [અહીં ક્લિક કરો]({APP_URL}/?tab=mandi&commodity={urllib.parse.quote(commodity)})"
            )
        elif lang == "mr":
            return (
                f"📊 *{state} मध्ये {commodity} बाजार अंदाज (UPAg)*:\n\n"
                f"• पुरवठा अंदाज: *{outlook['supply_outlook']}* ({trend_sign}{outlook['production_trend_pct']}%)\n"
                f"• घाऊक भाव: *₹{outlook['wholesale_price_avg']}/किग्रॅ*\n"
                f"• किरकोळ भाव: *₹{outlook['retail_price_avg']}/किग्रॅ* (मार्जिन: {outlook['retail_spread_pct']}%)\n\n"
                f"💡 *सल्ला*: {outlook['advisory_recommendation']}\n\n"
                f"📊 सविस्तर माहिती पाहण्यासाठी, [येथे क्लिक करा]({APP_URL}/?tab=mandi&commodity={urllib.parse.quote(commodity)})"
            )
        elif lang == "ta":
            return (
                f"📊 *{state} இல் {commodity} சந்தை முன்னறிவிப்பு (UPAg)*:\n\n"
                f"• உற்பத்தி நிலை: *{outlook['supply_outlook']}* ({trend_sign}{outlook['production_trend_pct']}%)\n"
                f"• மொத்த விலை: *₹{outlook['wholesale_price_avg']}/கிலோ*\n"
                f"• சில்லறை விலை: *₹{outlook['retail_price_avg']}/கிலோ* (விளிம்பு: {outlook['retail_spread_pct']}%)\n\n"
                f"💡 *ஆலோசனை*: {outlook['advisory_recommendation']}\n\n"
                f"📊 விவரங்களைப் பார்க்க, [இங்கே கிளிக் செய்யவும்]({APP_URL}/?tab=mandi&commodity={urllib.parse.quote(commodity)})"
            )
        else:
            return (
                f"📊 *Market Outlook & Advisory for {commodity} in {state} (UPAg)*:\n\n"
                f"• Supply Outlook: *{outlook['supply_outlook']}* ({trend_sign}{outlook['production_trend_pct']}% vs prior season)\n"
                f"• Mandi Wholesale Rate: *₹{outlook['wholesale_price_avg']}/kg*\n"
                f"• City Consumer Retail Rate: *₹{outlook['retail_price_avg']}/kg* (Retail Spread: {outlook['retail_spread_pct']}%)\n"
                f"• Climate Index (CWWG): Rainfall departure {outlook['rainfall_departure_pct']}%, Reservoir {outlook['reservoir_storage_pct']}%\n\n"
                f"💡 *Strategic Advisory*: {outlook['advisory_recommendation']}\n\n"
                f"📊 To view complete seasonal trend & e-NAM depth, [Click Here]({APP_URL}/?tab=mandi&commodity={urllib.parse.quote(commodity)})"
            )
        
    elif intent == "buyer":
        commodity = parsed.get("commodity") or "Maize"
        district = parsed.get("district") or "Shivamogga"
        
        cursor.execute(
            "SELECT * FROM buyers WHERE commodity LIKE ? AND district LIKE ? LIMIT 3",
            (f"%{commodity}%", f"%{district}%")
        )
        buyers = cursor.fetchall()
        
        if not buyers:
            cursor.execute("SELECT * FROM buyers WHERE commodity LIKE ? LIMIT 3", (f"%{commodity}%",))
            buyers = cursor.fetchall()
            
        if not buyers:
            return f"Currently, no registered buyers for {commodity} are available on the platform."
            
        buyer_list_str = ""
        for b in buyers:
            star = "⭐" * int(b["rating"])
            wa_link = f"https://wa.me/{b['phone'].replace('+', '')}"
            buyer_list_str += f"🏢 *{b['company']}* (Rating: {b['rating']:.1f} {star})\n📞 {b['phone']} | [Chat on WhatsApp]({wa_link})\n\n"
            
        return texts["buyer_template"].format(
            commodity=commodity,
            district=district,
            buyer_list=buyer_list_str.strip(),
            app_url=APP_URL
        )
        
    elif intent == "dealer":
        location = parsed.get("district") or "Shivamogga"
        cursor.execute("SELECT * FROM dealers WHERE location LIKE ? LIMIT 3", (f"%{location}%",))
        dealers = cursor.fetchall()
        
        if not dealers:
            cursor.execute("SELECT * FROM dealers LIMIT 3")
            dealers = cursor.fetchall()
            
        if not dealers:
            return "No input dealers found in your area."
            
        dealer_list_str = ""
        for d in dealers:
            stock = []
            if d["fertilizer"] == 1: stock.append("Fertilizer")
            if d["seed"] == 1: stock.append("Seeds")
            if d["pesticide"] == 1: stock.append("Pesticides")
            stock_str = ", ".join(stock)
            
            dealer_list_str += f"🏪 *{d['shop_name']}*\n📦 Stock: {stock_str}\n📍 Location: {d['location']}\n\n"
            
        return texts["dealer_template"].format(
            location=location,
            dealer_list=dealer_list_str.strip(),
            app_url=APP_URL
        )
        
    elif intent == "weather":
        location = parsed.get("district") or parsed.get("state") or "Shivamogga"
        return texts["weather_template"].format(location=location)
        
    elif intent == "scheme":
        return texts["scheme_template"]
        
    elif intent == "general":
        return parsed.get("general_answer", texts["greeting"])
        
    return texts["greeting"]

@app.route("/", methods=["GET"])
def read_root():
    return jsonify({
        "app": "KrishiMitra AI Backend",
        "status": "online",
        "version": "1.0",
        "framework": "Flask (Python 3.14 compatible)"
    })

# =======================
# Authentication Endpoints
# =======================

@app.route("/api/auth/send_otp", methods=["POST"])
def send_otp():
    data = request.get_json() or {}
    mobile = data.get("mobile", "").strip()
    if not mobile:
        return jsonify({"detail": "Mobile number is required"}), 400
    
    otp = "123456"
    _otp_store[mobile] = otp
    print(f"[OTP SMS SIMULATED] To: {mobile} | Code: {otp}")
    
    return jsonify({"message": "OTP sent successfully (Simulated 123456)"})

@app.route("/api/auth/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json() or {}
    mobile = data.get("mobile", "").strip()
    otp = data.get("otp", "").strip()
    name = data.get("name", "Farmer")
    preferred_language = data.get("preferred_language", "en")
    
    if _otp_store.get(mobile) != otp:
        return jsonify({"detail": "Invalid OTP code"}), 400
        
    if mobile in _otp_store:
        del _otp_store[mobile]
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
    user = cursor.fetchone()
    
    if not user:
        user_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO users (id, name, mobile, preferred_language, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, mobile, preferred_language, created_at)
        )
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
    conn.close()
    
    token_data = {
        "sub": user["id"],
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "mobile": user["mobile"],
            "preferred_language": user["preferred_language"]
        }
    })

# =======================
# Mandi Price Endpoints
# =======================

@app.route("/api/admin/upload-rates", methods=["POST"])
def admin_upload_rates():
    """
    Admin endpoint to upload local mandi rates in bulk (JSON, CSV text, or file upload).
    Requires valid Admin Secret Security PIN.
    """
    import csv
    import io

    # Admin Secret PIN Verification Check
    admin_pin = request.headers.get("X-Admin-PIN") or request.form.get("admin_pin")
    if request.is_json and isinstance(request.get_json(), dict):
        admin_pin = admin_pin or request.get_json().get("admin_pin")
        
    EXPECTED_PIN = os.environ.get("ADMIN_PIN", "2026")
    if not admin_pin or str(admin_pin).strip() != str(EXPECTED_PIN).strip():
        return jsonify({
            "success": False,
            "detail": "🔒 Unauthorized: Invalid Admin Security PIN. Access denied."
        }), 401
    
    records = []
    
    # 1. Check if JSON payload
    if request.is_json:
        data = request.get_json() or {}
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = data.get("records", [data])
            
    # 2. Check if CSV file or text in request
    elif "file" in request.files:
        uploaded_file = request.files["file"]
        content = uploaded_file.read().decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(content))
        records = [row for row in reader]
    elif request.form.get("csv_text"):
        csv_text = request.form.get("csv_text")
        reader = csv.DictReader(io.StringIO(csv_text))
        records = [row for row in reader]
    elif request.data:
        try:
            content = request.data.decode("utf-8", errors="ignore")
            reader = csv.DictReader(io.StringIO(content))
            records = [row for row in reader]
        except Exception:
            pass

    if not records:
        return jsonify({
            "success": False,
            "detail": "No valid CSV or JSON records found. Provide CSV file upload, JSON array, or csv_text parameter."
        }), 400

    conn = get_db_connection()
    res = MandiService.bulk_upload_rates(conn, records)
    conn.close()

    return jsonify(res)

@app.route("/api/mandi/states", methods=["GET"])
def get_states():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT state FROM mandis")
    rows = cursor.fetchall()
    states = [row["state"] for row in rows]
    conn.close()
    return jsonify(states)

@app.route("/api/translations/locations", methods=["GET"])
def get_location_translations():
    return jsonify({
        "states": TranslationService.STATE_TRANSLATIONS,
        "districts": TranslationService.DISTRICT_TRANSLATIONS
    })

@app.route("/api/mandi/details", methods=["GET"])
def get_mandi_details():
    mandi_name = request.args.get("mandi_name")
    if not mandi_name:
        return jsonify({"detail": "mandi_name is required"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT state, district, mandi_name FROM mandis WHERE mandi_name LIKE ? LIMIT 1", (f"%{mandi_name}%",))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"detail": "Mandi not found"}), 404

@app.route("/api/mandi/districts", methods=["GET"])
def get_districts():
    state = request.args.get("state")
    if not state:
        return jsonify({"detail": "state query parameter is required"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT district FROM mandis WHERE state = ?", (state,))
    rows = cursor.fetchall()
    districts = [row["district"] for row in rows]
    conn.close()
    return jsonify(districts)

@app.route("/api/mandi/list", methods=["GET"])
def get_mandis():
    state = request.args.get("state")
    district = request.args.get("district")
    if not state or not district:
        return jsonify({"detail": "state and district query parameters are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mandis WHERE state = ? AND district = ?", (state, district))
    rows = cursor.fetchall()
    mandis = [dict(row) for row in rows]
    conn.close()
    return jsonify(mandis)

@app.route("/api/mandi/commodities", methods=["GET"])
def get_commodities():
    mandi_name = request.args.get("mandi_name")
    conn = get_db_connection()
    cursor = conn.cursor()
    if mandi_name:
        cursor.execute("""
            SELECT DISTINCT c.id, c.commodity_name, c.local_name, c.category 
            FROM commodities c 
            JOIN daily_prices dp ON c.id = dp.commodity_id 
            JOIN mandis m ON dp.mandi_id = m.id 
            WHERE m.mandi_name = ?
        """, (mandi_name,))
    else:
        cursor.execute("SELECT * FROM commodities")
    rows = cursor.fetchall()
    commodities = [dict(row) for row in rows]
    conn.close()
    return jsonify(commodities)

@app.route("/api/advisory/market-outlook", methods=["GET"])
def get_market_outlook():
    state = request.args.get("state", "All India")
    commodity = request.args.get("commodity", "")
    lang = request.args.get("lang", "en")
    
    if not commodity:
        return jsonify({"error": "commodity parameter is required"}), 400
        
    conn = get_db_connection()
    try:
        outlook = UPAgService.get_macro_outlook(conn, state, commodity, lang=lang)
        return jsonify(outlook)
    except Exception as e:
        app.logger.exception("Market outlook query error")
        return jsonify({"error": "An internal error has occurred"}), 500
    finally:
        conn.close()

@app.route("/api/mandi/price", methods=["GET"])
def get_mandi_price():
    state = request.args.get("state")
    district = request.args.get("district")
    mandi_name = request.args.get("mandi_name")
    commodity_name = request.args.get("commodity_name")
    
    if not all([state, district, mandi_name, commodity_name]):
        return jsonify({"detail": "Missing parameters. Required: state, district, mandi_name, commodity_name"}), 400
        
    conn = get_db_connection()
    try:
        price_info = MandiService.get_mandi_price(conn, state, district, mandi_name, commodity_name)
        return jsonify(price_info)
    except Exception as e:
        app.logger.exception("Mandi price query error")
        return jsonify({"detail": "An internal error has occurred"}), 500
    finally:
        conn.close()

@app.route("/api/mandi/trend", methods=["GET"])
def get_price_trends():
    mandi_name = request.args.get("mandi_name")
    commodity_name = request.args.get("commodity_name")
    
    if not mandi_name or not commodity_name:
        return jsonify({"detail": "mandi_name and commodity_name are required"}), 400
        
    conn = get_db_connection()
    trend_data = MandiService.get_price_trends(conn, mandi_name, commodity_name)
    conn.close()
    
    if not trend_data:
        return jsonify({"detail": "Trend data not found"}), 404
        
    return jsonify({
        "commodity_name": commodity_name,
        "mandi_name": mandi_name,
        "trend": trend_data
    })

# =======================
# Marketplace Endpoints
# =======================

@app.route("/api/marketplace/buyers", methods=["GET"])
def get_buyers():
    commodity = request.args.get("commodity")
    district = request.args.get("district")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM buyers WHERE 1=1"
    params = []
    
    if commodity:
        query += " AND commodity LIKE ?"
        params.append(f"%{commodity}%")
    if district:
        query += " AND district LIKE ?"
        params.append(f"%{district}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    buyers = [dict(row) for row in rows]
    conn.close()
    return jsonify(buyers)

@app.route("/api/marketplace/dealers", methods=["GET"])
def get_dealers():
    location = request.args.get("location")
    fertilizer = request.args.get("fertilizer")
    seed = request.args.get("seed")
    pesticide = request.args.get("pesticide")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM dealers WHERE 1=1"
    params = []
    
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if fertilizer is not None:
        query += " AND fertilizer = ?"
        params.append(1 if fertilizer.lower() == 'true' else 0)
    if seed is not None:
        query += " AND seed = ?"
        params.append(1 if seed.lower() == 'true' else 0)
    if pesticide is not None:
        query += " AND pesticide = ?"
        params.append(1 if pesticide.lower() == 'true' else 0)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    dealers = [dict(row) for row in rows]
    conn.close()
    return jsonify(dealers)

@app.route("/api/marketplace/inventory/<dealer_id>", methods=["GET"])
def get_dealer_inventory(dealer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dealer_inventory WHERE dealer_id = ?", (dealer_id,))
    rows = cursor.fetchall()
    inventory = [dict(row) for row in rows]
    conn.close()
    return jsonify(inventory)

@app.route("/api/marketplace/reserve", methods=["POST"])
def reserve_inventory():
    data = request.json
    dealer_id = data.get("dealer_id")
    inventory_id = data.get("inventory_id")
    quantity = data.get("quantity")
    farmer_phone = data.get("farmer_phone")
    
    if not all([dealer_id, inventory_id, quantity, farmer_phone]):
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({"error": "Invalid quantity"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check stock
    cursor.execute("SELECT stock_quantity, item_name, unit FROM dealer_inventory WHERE id = ?", (inventory_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        return jsonify({"error": "Item not found"}), 404
        
    stock = item["stock_quantity"]
    if quantity > stock:
        conn.close()
        return jsonify({"error": f"Only {stock} {item['unit']} available"}), 400
        
    # Generate 4-digit PIN
    import random
    pin_code = str(random.randint(1000, 9999))
    reservation_id = str(uuid.uuid4())
    
    # Update stock
    cursor.execute("UPDATE dealer_inventory SET stock_quantity = stock_quantity - ? WHERE id = ?", (quantity, inventory_id))
    
    # Create reservation
    cursor.execute("""
    INSERT INTO reservations (id, dealer_id, inventory_id, farmer_phone, quantity, pin_code, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (reservation_id, dealer_id, inventory_id, farmer_phone, quantity, pin_code, 'PENDING'))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True, 
        "reservation_id": reservation_id, 
        "pin_code": pin_code,
        "message": f"Successfully reserved {quantity} {item['unit']} of {item['item_name']}. Please show PIN {pin_code} to the dealer to collect."
    })

# =======================
# WhatsApp Endpoints
# =======================

@app.route("/api/whatsapp/webhook", methods=["GET"])
def meta_verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    verify_token = os.environ.get("META_VERIFY_TOKEN", "krishimitra_secret_token")
    
    if mode and token:
        if mode == "subscribe" and token == verify_token:
            print("Webhook verified successfully by Meta!")
            return Response(challenge, mimetype="text/plain")
        return Response("Verification token mismatch", status=403, mimetype="text/plain")
    return Response("Webhook endpoint active", mimetype="text/plain")

@app.route("/api/whatsapp/webhook", methods=["POST"])
def meta_webhook():
    try:
        body = request.get_json() or {}
        print("Meta webhook body received:", body)
        
        entry = body.get("entry", [])
        if not entry:
            return jsonify({"status": "empty"})
            
        changes = entry[0].get("changes", [])
        if not changes:
            return jsonify({"status": "empty"})
            
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            msg = messages[0]
            from_num = msg.get("from")
            msg_type = msg.get("type")
            
            incoming_text = ""
            if msg_type == "text":
                incoming_text = msg.get("text", {}).get("body", "")
            elif msg_type == "audio":
                audio_obj = msg.get("audio", {})
                audio_id = audio_obj.get("id")
                audio_mime = audio_obj.get("mime_type", "audio/ogg")
                meta_token = os.environ.get("META_ACCESS_TOKEN", "")
                audio_bytes = None
                if audio_id and meta_token:
                    try:
                        media_meta = requests.get(
                            f"https://graph.facebook.com/v18.0/{audio_id}",
                            headers={"Authorization": f"Bearer {meta_token}"},
                            timeout=10
                        ).json()
                        dl_url = media_meta.get("url")
                        if dl_url:
                            r = requests.get(dl_url, headers={"Authorization": f"Bearer {meta_token}"}, timeout=15)
                            if r.status_code == 200:
                                audio_bytes = r.content
                    except Exception as _e:
                        print(f"Failed to fetch Meta audio: {_e}")

                if audio_bytes:
                    incoming_text = AIService.speech_to_text(audio_bytes, mime_type=audio_mime, language="hi")
                else:
                    incoming_text = "ಇವತ್ತು ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಜೋಳದ ರೇಟ್ ಎಷ್ಟು"
                
            if incoming_text:
                conn = get_db_connection()
                response_text = generate_chatbot_response(incoming_text, conn)
                conn.close()
                WhatsAppService.send_via_meta(from_num, response_text)
                
        return jsonify({"status": "processed"})
    except Exception as e:
        app.logger.exception("Meta webhook error")
        return jsonify({"status": "error", "detail": "An internal error has occurred"}), 500

@app.route("/api/whatsapp/twilio", methods=["POST"])
def twilio_webhook():
    try:
        from_num = request.form.get("From", "")
        body = request.form.get("Body", "")
        num_media = int(request.form.get("NumMedia", 0))
        
        print(f"Twilio webhook received from {from_num}")
        
        incoming_text = body
        if num_media > 0:
            media_url = request.form.get("MediaUrl0")
            media_type = request.form.get("MediaContentType0", "audio/ogg")
            if media_url and "audio" in media_type:
                parsed_url = urllib.parse.urlparse(media_url)
                allowed_hosts = ("api.twilio.com", "media.twiliocdn.com", "lookaside.fbsbx.com")
                host = (parsed_url.hostname or "").lower()
                if parsed_url.scheme == "https" and any(host == d or host.endswith("." + d) for d in allowed_hosts):
                    safe_path = parsed_url.path or ""
                    if safe_path.startswith("/"):
                        safe_media_url = urllib.parse.urlunparse((
                            "https",
                            host,
                            safe_path,
                            "",
                            parsed_url.query or "",
                            ""
                        ))
                        try:
                            r = requests.get(safe_media_url, timeout=15, allow_redirects=False)
                            if r.status_code == 200:
                                incoming_text = AIService.speech_to_text(r.content, mime_type=media_type, language="hi")
                        except Exception as _e:
                            print(f"Failed to download Twilio audio: {_e}")
            if not incoming_text:
                incoming_text = "ಇವತ್ತು ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಜೋಳದ ರೇಟ್ ಎಷ್ಟು"
            
        conn = get_db_connection()
        response_text = generate_chatbot_response(incoming_text, conn)
        conn.close()
        
        WhatsAppService.send_via_twilio(from_num, response_text)
        
        twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <Response></Response>"""
        return Response(twiml_response, mimetype="application/xml")
    except Exception as e:
        app.logger.exception("Twilio webhook error")
        return Response("<Response/>", mimetype="application/xml")

# =======================
# General Query Endpoints
# =======================

@app.route("/api/query", methods=["POST"])
def process_query():
    data = request.get_json() or {}
    text = data.get("text", "")
    
    if not text:
        return jsonify({"detail": "text field is required"}), 400
        
    conn = get_db_connection()
    try:
        response_text = generate_chatbot_response(text, conn)
        parsed = AIService.parse_query(text, db=conn)
        
        speech_url = f"/api/voice/tts?text={urllib.parse.quote(response_text[:30])}"
        audio_b64 = AIService.text_to_speech_base64(response_text, lang=parsed.get("language", "en"))
        
        return jsonify({
            "text": response_text,
            "audio_base64": audio_b64,
            "speech_url": speech_url,
            "intent": parsed.get("intent"),
            "commodity": parsed.get("commodity"),
            "district": parsed.get("district"),
            "detected_language": parsed.get("language")
        })
    except Exception as e:
        app.logger.exception("Process query error")
        return jsonify({"detail": "An internal error has occurred"}), 500
    finally:
        conn.close()

@app.route("/api/query/voice", methods=["POST"])
def process_voice_query():
    audio_bytes = None
    mime_type = "audio/ogg"

    if request.is_json:
        data = request.get_json() or {}
        base64_data = data.get("audio")
        mime_type = data.get("mime_type", "audio/ogg")
        if base64_data:
            import base64
            audio_bytes = base64.b64decode(base64_data)
    elif "file" in request.files:
        file = request.files["file"]
        audio_bytes = file.read()
        mime_type = file.mimetype or "audio/ogg"

    if not audio_bytes:
        return jsonify({"detail": "No audio file or base64 data received"}), 400

    transcribed_text = AIService.speech_to_text(audio_bytes, mime_type=mime_type)
    print("Voice query audio transcribed successfully")

    conn = get_db_connection()
    try:
        response_text = generate_chatbot_response(transcribed_text, conn)
        parsed = AIService.parse_query(transcribed_text, db=conn)
        speech_url = f"/api/voice/tts?text={urllib.parse.quote(response_text[:30])}"
        audio_b64 = AIService.text_to_speech_base64(response_text, lang=parsed.get("language", "en"))

        return jsonify({
            "transcribed_text": transcribed_text,
            "text": response_text,
            "audio_base64": audio_b64,
            "speech_url": speech_url,
            "intent": parsed.get("intent"),
            "commodity": parsed.get("commodity"),
            "district": parsed.get("district"),
            "detected_language": parsed.get("language")
        })
    except Exception as e:
        app.logger.exception("Process voice query error")
        return jsonify({"detail": "An internal error has occurred"}), 500
    finally:
        conn.close()

# =======================
# Voice & Bhashini Endpoints
# =======================

@app.route("/api/voice/tts", methods=["GET"])
def voice_tts_stream():
    text = request.args.get("text", "")
    lang = request.args.get("lang", "en")
    if not text:
        return jsonify({"detail": "text parameter is required"}), 400
    
    b64_audio = AIService.text_to_speech_base64(text, lang=lang)
    if not b64_audio:
        return jsonify({"detail": "Failed to synthesize speech"}), 500
    
    import base64
    audio_bytes = base64.b64decode(b64_audio)
    return Response(audio_bytes, mimetype="audio/wav")

@app.route("/api/voice/transcribe", methods=["POST"])
def voice_transcribe():
    audio_bytes = None
    mime_type = "audio/wav"
    lang = request.form.get("language") or "hi"
    
    if request.is_json:
        data = request.get_json() or {}
        b64_data = data.get("audio")
        mime_type = data.get("mime_type", "audio/wav")
        lang = data.get("language", "hi")
        if b64_data:
            import base64
            if "," in b64_data:
                b64_data = b64_data.split(",", 1)[1]
            audio_bytes = base64.b64decode(b64_data)
    elif "file" in request.files:
        f = request.files["file"]
        audio_bytes = f.read()
        mime_type = f.mimetype or "audio/wav"
        lang = request.form.get("language", "hi")
    
    if not audio_bytes:
        return jsonify({"detail": "No audio content provided"}), 400
        
    transcribed_text = AIService.speech_to_text(audio_bytes, mime_type=mime_type, language=lang)
    return jsonify({
        "text": transcribed_text,
        "language": lang
    })

@app.route("/api/voice/synthesize", methods=["POST"])
def voice_synthesize():
    data = request.get_json() or {}
    text = data.get("text", "")
    lang = data.get("language", "hi")
    gender = data.get("gender", "female")
    
    if not text:
        return jsonify({"detail": "text field is required"}), 400
        
    b64_audio = None
    if BhashiniService.is_available():
        b64_audio = BhashiniService.text_to_speech(text, source_lang=lang, gender=gender)
        
    if not b64_audio:
        b64_audio = AIService.text_to_speech_base64(text, lang=lang)
        
    if not b64_audio:
        return jsonify({"detail": "Failed to synthesize speech"}), 500
        
    return jsonify({
        "audio_base64": b64_audio,
        "mime_type": "audio/wav",
        "language": lang
    })

@app.route("/api/voice/translate", methods=["POST"])
def voice_translate():
    data = request.get_json() or {}
    text = data.get("text", "")
    src = data.get("source_language", "en")
    tgt = data.get("target_language", "hi")
    
    if not text:
        return jsonify({"detail": "text field is required"}), 400
        
    translated = BhashiniService.translate_text(text, source_lang=src, target_lang=tgt)
    return jsonify({
        "original_text": text,
        "translated_text": translated or text,
        "source_language": src,
        "target_language": tgt
    })

@app.route("/api/debug", methods=["GET"])
def debug_env():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    datagov_key = os.environ.get("DATAGOV_API_KEY")
    
    bhashini_available = BhashiniService.is_available()
    
    status = {
        "gemini_key_present": bool(gemini_key),
        "datagov_key_present": bool(datagov_key),
        "bhashini_configured": bhashini_available,
        "gemini_key_prefix": gemini_key[:4] if gemini_key else None,
        "gemini_api_test": "Not Tested"
    }
    
    if gemini_key:
        try:
            urls = [
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={gemini_key}"
            ]
            status["gemini_api_tests"] = {}
            for i, url in enumerate(urls):
                headers = {"Content-Type": "application/json"}
                payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
                response = requests.post(url, headers=headers, json=payload, timeout=5)
                status["gemini_api_tests"][f"url_{i}"] = f"Status: {response.status_code}, Body: {response.text[:200]}"
                
        except Exception as e:
            status["gemini_api_test"] = f"Error: {str(e)}"
            
    return jsonify(status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
