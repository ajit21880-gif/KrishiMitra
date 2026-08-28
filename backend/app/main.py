import os
import sys
import uuid
import jwt
from datetime import datetime, timedelta
import urllib.parse
import sqlite3
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Add backend/ to Python path to import services correctly
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import get_db_connection, init_db
from app.services.ai_service import AIService
from app.services.mandi_service import MandiService
from app.services.whatsapp_service import WhatsAppService

# Initialize SQLite tables on startup
init_db()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

SECRET_KEY = "krishimitra_super_secret_key"
ALGORITHM = "HS256"

# Mock storage for sent OTPs: phone -> OTP
_otp_store = {}

# Simple translations for WhatsApp Responses
RESPONSES = {
    "en": {
        "greeting": "Hello! I am KrishiMitra AI, your agricultural assistant.\nHow can I help you today? You can ask about grain rates (e.g., 'Maize rate in Shimoga'), search for fertilizer/seed dealers, or ask about verified buyers.",
        "location_missing": "To get rates, please tell me your state, district, or APMC mandi name.",
        "commodity_missing": "Which commodity are you interested in? (e.g., Maize, Wheat, Toor Dal, Soyabean, Onion, Tomato, Cotton, Gram)",
        "not_found": "Sorry, I could not find any price records for {commodity} in {mandi}.",
        "price_template": "🌾 *{commodity} Rate at {mandi}* ({date})\n\n• Modal Price: *₹{modal}* / quintal\n• Min Price: *₹{min}*\n• Max Price: *₹{max}*\n• Source: {source}\n\n📊 View 7-day price trends and compare nearby mandis at:\n{app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded}",
        "buyer_template": "🤝 *Verified Buyers for {commodity}* in {district}:\n\n{buyer_list}\n\nNavigate to marketplace for more verified buyers:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *Input Dealers (Fertilizer/Seeds) near {location}*:\n\n{dealer_list}\n\nView inventory and navigate at:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *Weather Forecast for {location}*:\nToday: Sunny, Max 32°C, Min 22°C.\nTomorrow: Light rain expected in the afternoon. High chance of rain. Good for sowing maize.",
        "scheme_template": "📋 *Government Scheme: PM-Kisan Samman Nidhi*\nUnder this scheme, all landholding farmers' families receive an financial benefit of ₹6,000 per year in three equal installments.\nVerify your PM-Kisan status at:\nhttps://pmkisan.gov.in/"
    },
    "hi": {
        "greeting": "नमस्ते! मैं कृषिमित्र एआई हूँ, आपका कृषि सहायक।\nआज मैं आपकी क्या मदद कर सकता हूँ? आप अनाज के भाव (जैसे 'इंदौर में गेहूं का भाव'), उर्वरक/बीज विक्रेताओं की खोज, या खरीदारों के बारे में पूछ सकते हैं।",
        "location_missing": "भाव जानने के लिए, कृपया मुझे अपना राज्य, जिला या एपीएमसी मंडी का नाम बताएं।",
        "commodity_missing": "आप किस फसल का भाव जानना चाहते हैं? (जैसे मक्का, गेहूं, तुअर दाल, सोयाबीन, प्याज, टमाटर, कपास, चना)",
        "not_found": "क्षमा करें, मुझे {mandi} में {commodity} के लिए कोई भाव नहीं मिला।",
        "price_template": "🌾 *{mandi} में {commodity} का भाव* ({date})\n\n• मॉडल भाव: *₹{modal}* / क्विंटल\n• न्यूनतम भाव: *₹{min}*\n• अधिकतम भाव: *₹{max}*\n• स्रोत: {source}\n\n📊 7 दिनों के भाव के रुझान देखें और तुलना करें:\n{app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded}",
        "buyer_template": "🤝 *{district} में {commodity} के सत्यापित खरीदार*:\n\n{buyer_list}\n\nअधिक खरीदारों को देखने के लिए जाएँ:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} के पास उर्वरक और बीज विक्रेता*:\n\n{dealer_list}\n\nस्टॉक देखने के लिए जाएँ:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} के लिए मौसम का पूर्वानुमान*:\nआज: धूप खिली रहेगी, अधिकतम 32°C, न्यूनतम 22°C.\nकल: दोपहर में हल्की बारिश की संभावना। बुवाई के लिए अच्छा समय है।",
        "scheme_template": "📋 *सरकारी योजना: पीएम-किसान सम्मान निधि*\nइस योजना के तहत भूमिधारक किसान परिवारों को ₹6,000 प्रति वर्ष की वित्तीय सहायता तीन समान किस्तों में मिलती है।\nअपना स्टेटस यहाँ जांचें: https://pmkisan.gov.in/"
    },
    "kn": {
        "greeting": "ನಮಸ್ಕಾರ! ನಾನು ಕೃಷಿಮಿತ್ರ AI, ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ.\nಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು? ನೀವು ಧಾನ್ಯದ ದರಗಳು (ಉದಾಹರಣೆಗೆ 'ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಮೆಕ್ಕೆಜೋಳದ ರೇಟ್'), ರಸಗೊಬ್ಬರ/ಬೀಜ ವಿತರಕರ ಹುಡುಕಾಟ ಅಥವಾ ಖರೀದಿದಾರರ ಬಗ್ಗೆ ಕೇಳಬಹುದು.",
        "location_missing": "ದರಗಳನ್ನು ತಿಳಿಯಲು, ದಯವಿಟ್ಟು ನಿಮ್ಮ ಜಿಲ್ಲೆ ಅಥವಾ ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆಯ ಹೆಸರನ್ನು ತಿಳಿಸಿ.",
        "commodity_missing": "ನೀವು ಯಾವ ಬೆಳೆಯ ದರವನ್ನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ? (ಉದಾಹರಣೆಗೆ ಮೆಕ್ಕೆಜೋಳ, ಗೋಧಿ, ತೊಗರಿ ಬೇಳೆ, ಸೋಯಾಬೀನ್, ಈರುಳ್ಳಿ, ಟೊಮೆಟೊ, ಹತ್ತಿ, ಕಡಲೆ)",
        "not_found": "ಕ್ಷಮಿಸಿ, {mandi} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {commodity} ಬೆಲೆ ವಿವರಗಳು ಲಭ್ಯವಿಲ್ಲ.",
        "price_template": "🌾 *{mandi} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {commodity} ದರ* ({date})\n\n• ಮಾದರಿ ಬೆಲೆ: *₹{modal}* / ಕ್ವಿಂಟಾಲ್\n• ಕನಿಷ್ಠ ಬೆಲೆ: *₹{min}*\n• ಗರಿಷ್ಠ ಬೆಲೆ: *₹{max}*\n• ಮೂಲ: {source}\n\n📊 ಕಳೆದ 7 ದಿನಗಳ ಬೆಲೆಯ ಏರಿಳಿತಗಳನ್ನು ನೋಡಲು ಈ ಲಿಂಕ್ ಬಳಸಿ:\n{app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded}",
        "buyer_template": "🤝 *{district} ಜಿಲ್ಲೆಯಲ್ಲಿ {commodity} ಖರೀದಿದಾರರು*:\n\n{buyer_list}\n\nಹೆಚ್ಚಿನ ಖರೀದಿದಾರರ ವಿವರಗಳಿಗಾಗಿ ಭೇಟಿ ನೀಡಿ:\n{app_url}/?tab=marketplace",
        "dealer_template": "🚜 *{location} ಹತ್ತಿರದ ಗೊಬ್ಬರ ಮತ್ತು ಬೀಜದ ಅಂಗಡಿಗಳು*:\n\n{dealer_list}\n\nದಾಸ್ತಾನು ವಿವರಗಳಿಗಾಗಿ ಭೇಟಿ ನೀಡಿ:\n{app_url}/?tab=marketplace",
        "weather_template": "🌤️ *{location} ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ*:\nಇಂದು: ಬಿಸಿಲಿನ ವಾತಾವರಣ, ಗರಿಷ್ಠ 32°C, ಕನಿಷ್ಠ 22°C.\nನಾಳೆ: ಮಧ್ಯಾಹ್ನ ಸಣ್ಣ ಪ್ರಮಾಣದ ಮಳೆ ನಿರೀಕ್ಷಿಸಲಾಗಿದೆ. ಬಿತ್ತನೆಗೆ ಉತ್ತಮ ಸಮಯ.",
        "scheme_template": "📋 *ಸರ್ಕಾರಿ ಯೋಜನೆ: ಪಿಎಂ-ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ*\nಈ ಯೋಜನೆಯಡಿ ಎಲ್ಲಾ ಭೂಹಿಡುವಳಿ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ವರ್ಷಕ್ಕೆ ₹6,000 ಆರ್ಥಿಕ ಸಹಾಯವನ್ನು ಮೂರು ಸಮಾನ ಕಂತುಗಳಲ್ಲಿ ನೀಡಲಾಗುತ್ತದೆ.\nನಿಮ್ಮ ಅರ್ಹತೆಯನ್ನು ಇಲ್ಲಿ ಪರಿಶೀಲಿಸಿ: https://pmkisan.gov.in/"
    }
}

APP_URL = os.environ.get("FRONTEND_APP_URL", "http://localhost:3001")

def generate_chatbot_response(query_text: str, db: sqlite3.Connection) -> str:
    cursor = db.cursor()
    
    # 1. Parse text using AI Service
    parsed = AIService.parse_query(query_text)
    lang = parsed.get("language", "en")
    if lang not in RESPONSES:
        lang = "en"
        
    texts = RESPONSES[lang]
    intent = parsed.get("intent")
    
    # Quick greeting catch
    if query_text.lower().strip() in ["hello", "hi", "hey", "नमस्ते", "ನಮಸ್ಕಾರ"]:
        return texts["greeting"]

    # Process Intent
    if intent == "price":
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
            return texts["not_found"].format(commodity=commodity, mandi=mandi_name)
            
        mandi_enc = urllib.parse.quote(mandi_name)
        comm_enc = urllib.parse.quote(commodity)
        
        return texts["price_template"].format(
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

@app.route("/api/mandi/states", methods=["GET"])
def get_states():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT state FROM mandis")
    rows = cursor.fetchall()
    states = [row["state"] for row in rows]
    conn.close()
    return jsonify(states)

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
        return jsonify({"detail": str(e)}), 500
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
                incoming_text = "ಇವತ್ತು ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಜೋಳದ ರೇಟ್ ಎಷ್ಟು"
                
            if incoming_text:
                conn = get_db_connection()
                response_text = generate_chatbot_response(incoming_text, conn)
                conn.close()
                WhatsAppService.send_via_meta(from_num, response_text)
                
        return jsonify({"status": "processed"})
    except Exception as e:
        print(f"Meta webhook error: {e}")
        return jsonify({"status": "error", "detail": str(e)}), 500

@app.route("/api/whatsapp/twilio", methods=["POST"])
def twilio_webhook():
    try:
        from_num = request.form.get("From", "")
        body = request.form.get("Body", "")
        num_media = int(request.form.get("NumMedia", 0))
        
        print(f"Twilio webhook received from {from_num}: {body}")
        
        incoming_text = body
        if num_media > 0:
            incoming_text = "ಇವತ್ತು ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಜೋಳದ ರೇಟ್ ಎಷ್ಟು"
            
        conn = get_db_connection()
        response_text = generate_chatbot_response(incoming_text, conn)
        conn.close()
        
        WhatsAppService.send_via_twilio(from_num, response_text)
        
        twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <Response></Response>"""
        return Response(twiml_response, mimetype="application/xml")
    except Exception as e:
        print(f"Twilio webhook error: {e}")
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
        parsed = AIService.parse_query(text)
        
        speech_url = f"/api/voice/tts?text={urllib.parse.quote(response_text[:30])}"
        
        return jsonify({
            "text": response_text,
            "speech_url": speech_url,
            "intent": parsed.get("intent"),
            "commodity": parsed.get("commodity"),
            "district": parsed.get("district"),
            "detected_language": parsed.get("language")
        })
    except Exception as e:
        return jsonify({"detail": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/query/voice", methods=["POST"])
def process_voice_query():
    if "file" not in request.files:
        return jsonify({"detail": "No file uploaded"}), 400
        
    file = request.files["file"]
    audio_bytes = file.read()
    
    transcribed_text = AIService.speech_to_text(audio_bytes)
    print(f"Transcribed voice: {transcribed_text}")
    
    conn = get_db_connection()
    try:
        response_text = generate_chatbot_response(transcribed_text, conn)
        parsed = AIService.parse_query(transcribed_text)
        speech_url = f"/api/voice/tts?text={urllib.parse.quote(response_text[:30])}"
        
        return jsonify({
            "transcribed_text": transcribed_text,
            "text": response_text,
            "speech_url": speech_url,
            "intent": parsed.get("intent"),
            "commodity": parsed.get("commodity"),
            "district": parsed.get("district"),
            "detected_language": parsed.get("language")
        })
    except Exception as e:
        return jsonify({"detail": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/debug", methods=["GET"])
def debug_env():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    datagov_key = os.environ.get("DATAGOV_API_KEY")
    
    status = {
        "gemini_key_present": bool(gemini_key),
        "datagov_key_present": bool(datagov_key),
        "gemini_key_prefix": gemini_key[:4] if gemini_key else None,
        "gemini_api_test": "Not Tested"
    }
    
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            status["gemini_api_test"] = f"Status: {response.status_code}"
            if response.status_code != 200:
                status["gemini_error"] = response.text[:200]
        except Exception as e:
            status["gemini_api_test"] = f"Error: {str(e)}"
            
    return jsonify(status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
