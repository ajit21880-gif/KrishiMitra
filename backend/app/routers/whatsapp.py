from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException
import sqlite3
from typing import Optional, Dict, Any
import os
import urllib.parse
from app.core.database import get_db
from app.services.ai_service import AIService
from app.services.mandi_service import MandiService
from app.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

# Simple translations for WhatsApp Responses
RESPONSES = {
    "en": {
        "greeting": "Hello! I am KrishiMitra AI, your agricultural assistant.\nHow can I help you today? You can ask about grain rates (e.g., 'Maize rate in Shimoga'), search for fertilizer/seed dealers, or ask about verified buyers.",
        "location_missing": "To get rates, please tell me your state, district, or APMC mandi name.",
        "commodity_missing": "Which commodity are you interested in? (e.g., Maize, Wheat, Soyabean, Onion, Tomato)",
        "not_found": "Sorry, I could not find any price records for {commodity} in {mandi}.",
        "price_template": "🌾 *{commodity} Rate at {mandi}* ({date})\n\n• Modal Price: *₹{modal}* / quintal\n• Min Price: *₹{min}*\n• Max Price: *₹{max}*\n• Source: {source}\n\n📊 To view 7-day price trends and compare nearby mandis, [Click Here]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *Verified Buyers for {commodity}* in {district}:\n\n{buyer_list}\n\nNavigate to marketplace for more verified buyers:\n{app_url}/marketplace",
        "dealer_template": "🚜 *Input Dealers (Fertilizer/Seeds) near {location}*:\n\n{dealer_list}\n\nView inventory and navigate at:\n{app_url}/marketplace",
        "weather_template": "🌤️ *Weather Forecast for {location}*:\nToday: Sunny, Max 32°C, Min 22°C.\nTomorrow: Light rain expected in the afternoon. High chance of rain. Good for sowing maize.",
        "scheme_template": "📋 *Government Scheme: PM-Kisan Samman Nidhi*\nUnder this scheme, all landholding farmers' families receive an financial benefit of ₹6,000 per year in three equal installments.\nVerify your PM-Kisan status at:\nhttps://pmkisan.gov.in/"
    },
    "hi": {
        "greeting": "नमस्ते! मैं कृषिमित्र एआई हूँ, आपका कृषि सहायक।\nआज मैं आपकी क्या मदद कर सकता हूँ? आप अनाज के भाव (जैसे 'इंदौर में गेहूं का भाव'), उर्वरक/बीज विक्रेताओं की खोज, या खरीदारों के बारे में पूछ सकते हैं।",
        "location_missing": "भाव जानने के लिए, कृपया मुझे अपना राज्य, जिला या एपीएमसी मंडी का नाम बताएं।",
        "commodity_missing": "आप किस फसल का भाव जानना चाहते हैं? (जैसे मक्का, गेहूं, सोयाबीन, प्याज, टमाटर)",
        "not_found": "क्षमा करें, मुझे {mandi} में {commodity} के लिए कोई भाव नहीं मिला।",
        "price_template": "🌾 *{mandi} में {commodity} का भाव* ({date})\n\n• मॉडल भाव: *₹{modal}* / क्विंटल\n• न्यूनतम भाव: *₹{min}*\n• अधिकतम भाव: *₹{max}*\n• स्रोत: {source}\n\n📊 7 दिनों के भाव के रुझान और मंडियों की तुलना देखने के लिए, [यहाँ क्लिक करें]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} में {commodity} के सत्यापित खरीदार*:\n\n{buyer_list}\n\nअधिक खरीदारों को देखने के लिए जाएँ:\n{app_url}/marketplace",
        "dealer_template": "🚜 *{location} के पास उर्वरक और बीज विक्रेता*:\n\n{dealer_list}\n\nस्टॉक देखने के लिए जाएँ:\n{app_url}/marketplace",
        "weather_template": "🌤️ *{location} के लिए मौसम का पूर्वानुमान*:\nआज: धूप खिली रहेगी, अधिकतम 32°C, न्यूनतम 22°C.\nकल: दोपहर में हल्की बारिश की संभावना। बुवाई के लिए अच्छा समय है।",
        "scheme_template": "📋 *सरकारी योजना: पीएम-किसान सम्मान निधि*\nइस योजना के तहत भूमिधारक किसान परिवारों को ₹6,000 प्रति वर्ष की वित्तीय सहायता तीन समान किस्तों में मिलती है।\nअपना स्टेटस यहाँ जांचें: https://pmkisan.gov.in/"
    },
    "kn": {
        "greeting": "ನಮಸ್ಕಾರ! ನಾನು ಕೃಷಿಮಿತ್ರ AI, ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ.\nಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು? ನೀವು ಧಾನ್ಯದ ದರಗಳು (ಉದಾಹರಣೆಗೆ 'ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಮೆಕ್ಕೆಜೋಳದ ರೇಟ್'), ರಸಗೊಬ್ಬರ/ಬೀಜ ವಿತರಕರ ಹುಡುಕಾಟ ಅಥವಾ ಖರೀದಿದಾರರ ಬಗ್ಗೆ ಕೇಳಬಹುದು.",
        "location_missing": "ದರಗಳನ್ನು ತಿಳಿಯಲು, ದಯವಿಟ್ಟು ನಿಮ್ಮ ಜಿಲ್ಲೆ ಅಥವಾ ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆಯ ಹೆಸರನ್ನು ತಿಳಿಸಿ.",
        "commodity_missing": "ನೀವು ಯಾವ ಬೆಳೆಯ ದರವನ್ನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ? (ಉದಾಹರಣೆಗೆ ಮೆಕ್ಕೆಜೋಳ, ಗೋಧಿ, ಸೋಯಾಬೀನ್, ಈರುಳ್ಳಿ, ಟೊಮೆಟೊ)",
        "not_found": "ಖುಷಿ ಪಡಿ, ಆದರೆ {mandi} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {commodity} ಬೆಲೆ ವಿವರಗಳು ಲಭ್ಯವಿಲ್ಲ.",
        "price_template": "🌾 *{mandi} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {commodity} ದರ* ({date})\n\n• ಮಾದರಿ ಬೆಲೆ: *₹{modal}* / ಕ್ವಿಂಟಾಲ್\n• ಕನಿಷ್ಠ ಬೆಲೆ: *₹{min}*\n• ಗರಿಷ್ಠ ಬೆಲೆ: *₹{max}*\n• ಮೂಲ: {source}\n\n📊 ಕಳೆದ 7 ದಿನಗಳ ಬೆಲೆಯ ಏರಿಳಿತಗಳು ಮತ್ತು ಹೋಲಿಕೆಯನ್ನು ನೋಡಲು, [ಇಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ]({app_url}/?tab=mandi&mandi={mandi_encoded}&commodity={commodity_encoded})",
        "buyer_template": "🤝 *{district} ಜಿಲ್ಲೆಯಲ್ಲಿ {commodity} ಖರೀದಿದಾರರು*:\n\n{buyer_list}\n\nಹೆಚ್ಚಿನ ಖರೀದಿದಾರರ ವಿವರಗಳಿಗಾಗಿ ಭೇಟಿ ನೀಡಿ:\n{app_url}/marketplace",
        "dealer_template": "🚜 *{location} ಹತ್ತಿರದ ಗೊಬ್ಬರ ಮತ್ತು ಬೀಜದ ಅಂಗಡಿಗಳು*:\n\n{dealer_list}\n\nದಾಸ್ತಾನು ವಿವರಗಳಿಗಾಗಿ ಭೇಟಿ ನೀಡಿ:\n{app_url}/marketplace",
        "weather_template": "🌤️ *{location} ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ*:\nಇಂದು: ಬಿಸಿಲಿನ ವಾತಾವರಣ, ಗರಿಷ್ಠ 32°C, ಕನಿಷ್ಠ 22°C.\nನಾಳೆ: ಮಧ್ಯಾಹ್ನ ಸಣ್ಣ ಪ್ರಮಾಣದ ಮಳೆ ನಿರೀಕ್ಷಿಸಲಾಗಿದೆ. ಬಿತ್ತನೆಗೆ ಉತ್ತಮ ಸಮಯ.",
        "scheme_template": "📋 *ಸರ್ಕಾರಿ ಯೋಜನೆ: ಪಿಎಂ-ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ*\nಈ ಯೋಜನೆಯಡಿ ಎಲ್ಲಾ ಭೂಹಿಡುವಳಿ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ವರ್ಷಕ್ಕೆ ₹6,000 ಆರ್ಥಿಕ ಸಹಾಯವನ್ನು ಮೂರು ಸಮಾನ ಕಂತುಗಳಲ್ಲಿ ನೀಡಲಾಗುತ್ತದೆ.\nನಿಮ್ಮ ಅರ್ಹತೆಯನ್ನು ಇಲ್ಲಿ ಪರಿಶೀಲಿಸಿ: https://pmkisan.gov.in/"
    }
}

# App Base URL (fallback to production Vercel URL)
APP_URL = os.environ.get("FRONTEND_APP_URL", "https://krishi-mitra-crestsubarn.vercel.app")

def generate_chatbot_response(query_text: str, db: sqlite3.Connection) -> str:
    cursor = db.cursor()
    
    # 1. Parse text using AI Service
    parsed = AIService.parse_query(query_text)
    lang = parsed.get("language", "en")
    if lang not in RESPONSES:
        lang = "en"
        
    texts = RESPONSES[lang]
    intent = parsed.get("intent")
    
    # Check activation trigger keywords
    q_clean = query_text.lower().strip()
    is_activation_phrase = any(kw in q_clean for kw in ["krishimitra", "krishi mitra", "कृषिमित्र", "ಕೃಷಿಮಿತ್ರ", "கிருஷிமித்ரா"])
    is_simple_greeting = q_clean in ["hello", "hi", "hey", "hi!", "hello!", "hey!", "namaste", "नमस्ते", "ನಮಸ್ಕಾರ", "வணக்கம்"]
    
    if is_activation_phrase:
        return texts["greeting"]
        
    if is_simple_greeting:
        return "" # Completely silent for plain Hi/Hello - only react when Hi KrishiMitra is said

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
            if not mandi:
                # Get any mandi in DB
                cursor.execute("SELECT * FROM mandis LIMIT 1")
                mandi = cursor.fetchone()
                
        mandi_name = mandi["mandi_name"] if mandi else district
        state_name = mandi["state"] if mandi else "Karnataka"
        
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
            # Fallback by commodity
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
        location = parsed.get("district") or "Shivamogga"
        return texts["weather_template"].format(location=location)
        
    elif intent == "scheme":
        return texts["scheme_template"]
        
    return texts["greeting"]

# =======================
# Webhook Endpoints
# =======================

@router.get("/webhook")
def meta_verify(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    verify_token = os.environ.get("META_VERIFY_TOKEN", "krishimitra_secret_token")
    
    if mode and token:
        if mode == "subscribe" and token == verify_token:
            print("Webhook verified successfully by Meta!")
            return Response(content=challenge, media_type="text/plain")
        return HTTPException(status_code=403, detail="Verification token mismatch")
    return Response(content="Webhook endpoint active", media_type="text/plain")

@router.post("/webhook")
async def meta_webhook(request: Request, db: sqlite3.Connection = Depends(get_db)):
    try:
        body = await request.json()
        print("Meta webhook body received:", body)
        
        entry = body.get("entry", [])
        if not entry:
            return {"status": "empty"}
            
        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "empty"}
            
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
                response_text = generate_chatbot_response(incoming_text, db)
                WhatsAppService.send_via_meta(from_num, response_text)
                
        return {"status": "processed"}
    except Exception as e:
        print(f"Meta webhook error: {e}")
        return {"status": "error", "detail": str(e)}

@router.post("/twilio")
async def twilio_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    NumMedia: int = Form(0),
    db: sqlite3.Connection = Depends(get_db)
):
    try:
        print(f"Twilio webhook received from {From}: {Body}")
        
        incoming_text = Body
        if NumMedia > 0:
            incoming_text = "ಇವತ್ತು ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಜೋಳದ ರೇಟ್ ಎಷ್ಟು"
            
        response_text = generate_chatbot_response(incoming_text, db)
        WhatsAppService.send_via_twilio(From, response_text)
        
        twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
        <Response></Response>"""
        return Response(content=twiml_response, media_type="application/xml")
    except Exception as e:
        print(f"Twilio webhook error: {e}")
        return Response(content="<Response/>", media_type="application/xml")
