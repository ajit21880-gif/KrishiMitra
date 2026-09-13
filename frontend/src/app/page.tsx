"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Mic, MicOff, Search, PhoneCall, TrendingUp, Store, 
  MapPin, Radio, MessageCircle, ArrowRight, UserCheck, 
  Volume2, CloudSun, BookOpen, Send, CheckCircle, X
} from "lucide-react";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from "recharts";

// Language UI translations
const TRANSLATIONS: Record<string, any> = {
  en: {
    app_title: "KrishiMitra AI",
    tagline: "Your Hyperlocal Mandi & Input Assistant",
    tab_assistant: "Voice Assistant",
    not_found_alert: "No active price records found for this crop in this mandi.",
    not_found_suggestion: "Would you like to check prices for other commodities or nearby mandis?",
    tab_mandi: "Mandi Rates",
    tab_market: "Marketplace",
    tab_whatsapp: "WhatsApp Chat",
    btn_mic_start: "Tap to Speak",
    btn_mic_stop: "Listening... Tap to Stop",
    btn_upload_csv: "Upload Rates (CSV)",
    select_lang: "Select Language",
    select_state: "Select State",
    select_district: "Select District",
    select_mandi: "Select Mandi",
    select_commodity: "Select Grain/Crop",
    min_price: "Min Rate",
    max_price: "Max Rate",
    modal_price: "Modal Rate",
    gov_verified: "Official Govt Source",
    mandi_header: "Mandi Rates Dashboard",
    trend_header: "7-Day Price Trend (₹/Quintal)",
    buyers_header: "Verified Wholesalers & Buyers",
    dealers_header: "Fertilizer, Seed & Pesticide Dealers",
    stock_status: "In Stock:",
    rating: "Rating",
    whats_app_chat: "WhatsApp",
    call: "Call",
    prompt_placeholder: "Ask something e.g. 'Wheat rate in Indore'...",
    send: "Send",
    offline_mode: "Offline Mode (Cached Prices Active)",
    last_updated: "Last Updated",
    no_records: "No price records found. Try another Mandi or crop.",
    msp: "MSP Support Price",
    greeting: "Hello! How can I help you with your agriculture queries today?"
  },
  hi: {
    app_title: "कृषिमित्र एआई",
    tagline: "आपका हाइपरलोकल मंडी और इनपुट सहायक",
    tab_assistant: "आवाज़ सहायक",
    tab_mandi: "मंडी दर",
    tab_market: "बाज़ार (मार्केट)",
    tab_whatsapp: "व्हाट्सएप चैट",
    btn_mic_start: "बोलने के लिए दबाएं",
    btn_mic_stop: "सुन रहा हूँ... रोकने के लिए दबाएं",
    btn_upload_csv: "भाव अपलोड करें (CSV)",
    select_lang: "भाषा चुनें",
    select_state: "राज्य चुनें",
    select_district: "जिला चुनें",
    select_mandi: "मंडी चुनें",
    select_commodity: "फसल/अनाज चुनें",
    min_price: "न्यूनतम भाव",
    max_price: "अधिकतम भाव",
    modal_price: "मॉडल भाव",
    gov_verified: "आधिकारिक सरकारी स्रोत",
    mandi_header: "मंडी भाव डैशबोर्ड",
    trend_header: "7-दिवसीय भाव का रुझान (₹/क्विंटल)",
    buyers_header: "सत्यापित थोक व्यापारी और खरीदार",
    dealers_header: "उर्वरक, बीज और कीटनाशक विक्रेता",
    stock_status: "स्टॉक में:",
    rating: "रेटिंग",
    whats_app_chat: "व्हाट्सएप",
    call: "कॉल",
    prompt_placeholder: "कुछ पूछें जैसे 'इंदौर में गेहूं का भाव'...",
    send: "भेजें",
    offline_mode: "ऑफलाइन मोड (कैश भाव सक्रिय)",
    last_updated: "अंतिम अपडेट",
    no_records: "कोई भाव रिकॉर्ड नहीं मिला। दूसरी मंडी या फसल चुनें।",
    msp: "MSP न्यूनतम समर्थन मूल्य",
    greeting: "नमस्ते! मैं आपकी कृषि संबंधी समस्याओं में कैसे मदद कर सकता हूँ?"
  },
  kn: {
    app_title: "ಕೃಷಿಮಿತ್ರ AI",
    tagline: "ನಿಮ್ಮ ಹತ್ತಿರದ ಮಾರುಕಟ್ಟೆ ಮತ್ತು ಕೃಷಿ ಸಲಹೆಗಾರ",
    tab_assistant: "ಧ್ವನಿ ಸಹಾಯಕ",
    not_found_alert: "ಈ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಈ ಬೆಳೆಗೆ ಯಾವುದೇ ಸಕ್ರಿಯ ಬೆಲೆ ದಾಖಲೆಗಳು ಕಂಡುಬಂದಿಲ್ಲ.",
    not_found_suggestion: "ನೀವು ಇತರ ಬೆಳೆಗಳ ದರಗಳನ್ನು ಪರಿಶೀಲಿಸಲು ಬಯಸುವಿರಾ?",
    tab_mandi: "ಮಾರುಕಟ್ಟೆ ದರ",
    tab_market: "ಖರೀದಿದಾರರು/ಅಂಗಡಿಗಳು",
    tab_whatsapp: "ವಾಟ್ಸಾಪ್ ಚಾಟ್",
    btn_mic_start: "ಮಾತನಾಡಲು ಒತ್ತಿ",
    btn_mic_stop: "ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದೆ... ನಿಲ್ಲಿಸಲು ಒತ್ತಿ",
    btn_upload_csv: "ದರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ (CSV)",
    select_lang: "ಭಾಷೆ ಆರಿಸಿ",
    select_state: "ರಾಜ್ಯ ಆರಿಸಿ",
    select_district: "ಜಿಲ್ಲೆ ಆರಿಸಿ",
    select_mandi: "ಮಾರುಕಟ್ಟೆ ಆರಿಸಿ",
    select_commodity: "ಬೆಳೆ/ಧಾನ್ಯ ಆರಿಸಿ",
    min_price: "ಕನಿಷ್ಠ ದರ",
    max_price: "ಗರಿಷ್ಠ ದರ",
    modal_price: "ಮಾದರಿ ದರ",
    gov_verified: "ಸರ್ಕಾರಿ ಅಧಿಕೃತ ಮಾಹಿತಿ",
    mandi_header: "ಮಾರುಕಟ್ಟೆ ದರ ಪಟ್ಟಿ",
    trend_header: "ಕಳೆದ 7 ದಿನಗಳ ಬೆಲೆಯ ಏರಿಳಿತ (₹/ಕ್ವಿಂಟಾಲ್)",
    buyers_header: "ಸತ್ಯಾಪಿತ ಸಗಟು ಖರೀದಿದಾರರು",
    dealers_header: "ರಸಗೊಬ್ಬರ, ಬೀಜ ಮತ್ತು ಕೀಟನಾಶಕ ಅಂಗಡಿಗಳು",
    stock_status: "ದಾಸ್ತಾನು ಲಭ್ಯತೆ:",
    rating: "ರೇಟಿಂಗ್",
    whats_app_chat: "ವಾಟ್ಸಾಪ್",
    call: "ಕರೆ ಮಾಡಿ",
    prompt_placeholder: "ಉದಾಹರಣೆಗೆ 'ಶಿವಮೊಗ್ಗದಲ್ಲಿ ಜೋಳದ ರೇಟ್' ಎಂದು ಕೇಳಿ...",
    send: "ಕಳುಹಿಸಿ",
    offline_mode: "ಆಫ್‌ಲೈನ್ ಮೋಡ್ (ಹಳೆಯ ಬೆಲೆ ಲಭ್ಯವಿದೆ)",
    last_updated: "ಕೊನೆಯದಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ",
    no_records: "ಯಾವುದೇ ದರ ಪಟ್ಟಿ ಲಭ್ಯವಿಲ್ಲ. ಬೇರೆ ಮಾರುಕಟ್ಟೆ ಅಥವಾ ಬೆಳೆ ಆರಿಸಿ.",
    msp: "ಬೆಂಬಲ ಬೆಲೆ (MSP)",
    greeting: "ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಕೃಷಿ ಸಂಬಂಧಿತ ಪ್ರಶ್ನೆಗಳಿಗೆ ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
  },
  gu: {
    app_title: "કૃષિમિત્ર AI",
    tagline: "તમારો હાયપરલોકલ મંડી અને ખેતી ઇનપુટ સહાયક",
    tab_assistant: "અવાજ સહાયક",
    tab_mandi: "મંડી ભાવ",
    tab_market: "બજાર (માર્કેટ)",
    tab_whatsapp: "વોટ્સએપ ચેટ",
    btn_mic_start: "બોલવા માટે દબાવો",
    btn_mic_stop: "સાંભળી રહ્યો છું... રોકવા માટે દબાવો",
    btn_upload_csv: "ભાવ અપલોડ કરો (CSV)",
    select_lang: "ભાષા પસંદ કરો",
    select_state: "રાજ્ય પસંદ કરો",
    select_district: "જિલ્લો પસંદ કરો",
    select_mandi: "મંડી પસંદ કરો",
    select_commodity: "પાક/અનાજ પસંદ કરો",
    min_price: "ન્યૂનતમ ભાવ",
    max_price: "મહત્તમ ભાવ",
    modal_price: "મોડલ ભાવ",
    gov_verified: "સત્તાવાર સરકારી સ્ત્રોત",
    mandi_header: "મંડી ભાવ ડેશબોર્ડ",
    trend_header: "છેલ્લા 7 દિવસના ભાવનું વલણ (₹/ક્વિન્ટલ)",
    buyers_header: "ચકાસાયેલ જથ્થાબંધ વેપારીઓ અને ખરીદદારો",
    dealers_header: "ખાતર, બિયારણ અને જંતુનાશક વિક્રેતાઓ",
    stock_status: "સ્ટોકમાં:",
    rating: "રેટિંગ",
    whats_app_chat: "વોટ્સએપ",
    call: "કૉલ કરો",
    prompt_placeholder: "પૂછો જેમ કે 'અમદાવાદમાં સફરજનનો ભાવ'...",
    send: "મોકલો",
    offline_mode: "ઓફલાઇન મોડ (સંગ્રહિત ભાવો સક્રિય)",
    last_updated: "છેલ્લું અપડેટ",
    no_records: "કોઈ ભાવ રેકોર્ડ મળ્યા નથી. બીજી મંડી અથવા પાક પસંદ કરો.",
    msp: "MSP ટેકાના ભાવ",
    greeting: "નમસ્તે! હું તમારા ખેતી સંબંધિત પ્રશ્નોમાં કેવી રીતે મદદ કરી શકું?"
  },
  mr: {
    app_title: "कृषिमित्र AI",
    tagline: "तुमचा हायपरलोकल बाजार समिती व कृषी सहाय्यक",
    tab_assistant: "व्हॉइस असिस्टंट",
    tab_mandi: "बाजार भाव",
    tab_market: "मार्केटप्लेस",
    tab_whatsapp: "व्हॉट्सॲप चॅट",
    btn_mic_start: "बोलण्यासाठी दाबा",
    btn_mic_stop: "ऐकत आहे... थांबवण्यासाठी दाबा",
    btn_upload_csv: "दर अपलोड करा (CSV)",
    select_lang: "भाषा निवडा",
    select_state: "राज्य निवडा",
    select_district: "जिल्हा निवडा",
    select_mandi: "बाजार समिती (मंडी) निवडा",
    select_commodity: "पीक/धान्य निवडा",
    min_price: "किमान दर",
    max_price: "कमाल दर",
    modal_price: "सर्वसाधारण दर",
    gov_verified: "अधिकृत शासकीय स्रोत",
    mandi_header: "बाजार भाव डॅशबोर्ड",
    trend_header: "गेल्या ७ दिवसांचे बाजार भाव (₹/क्विंटल)",
    buyers_header: "सत्यापित घाऊक व्यापारी व खरेदीदार",
    dealers_header: "खते, बियाणे आणि कीटकनाशके विक्रेते",
    stock_status: "उपलब्ध साठा:",
    rating: "रेटिंग",
    whats_app_chat: "व्हॉट्सॲप",
    call: "कॉल करा",
    prompt_placeholder: "विचारा जसे 'पुण्यात कांद्याचा भाव काय आहे'...",
    send: "पाठवा",
    offline_mode: "ऑफलाइन मोड (कॅश केलेले भाव सक्रिय)",
    last_updated: "शेवटचे अपडेट",
    no_records: "कोणतेही दर उपलब्ध नाहीत. दुसरी मंडी किंवा पीक निवडा.",
    msp: "हमीभाव (MSP)",
    greeting: "नमस्कार! मी आज आपल्या कृषी विषयक प्रश्नांमध्ये कशी मदत करू शकतो?"
  },
  ta: {
    app_title: "கிருஷிமித்ரா AI",
    tagline: "உங்கள் பண்ணை & சந்தை விலை வழிகாட்டி",
    tab_assistant: "குரல் உதவியாளர்",
    not_found_alert: "இந்த சந்தையில் இந்த பயிருக்கான விலை விவரங்கள் கிடைக்கவில்லை.",
    not_found_suggestion: "மற்ற பயிர்களின் விலைகளை பார்க்க விரும்புகிறீர்களா?",
    tab_mandi: "மண்டி விலை",
    tab_market: "சந்தை",
    tab_whatsapp: "வாட்ஸ்அப் அரட்டை",
    btn_mic_start: "பேச அழுத்தவும்",
    btn_mic_stop: "கேட்கிறது... நிறுத்த அழுத்தவும்",
    btn_upload_csv: "விலை பதிவேற்றம் (CSV)",
    select_lang: "மொழியைத் தேர்ந்தெடுக்கவும்",
    select_state: "மாநிலத்தைத் தேர்ந்தெடுக்கவும்",
    select_district: "மாவட்டத்தைத் தேர்ந்தெடுக்கவும்",
    select_mandi: "மண்டியைத் தேர்ந்தெடுக்கவும்",
    select_commodity: "பயிரைத் தேர்ந்தெடுக்கவும்",
    min_price: "குறைந்தபட்ச விலை",
    max_price: "அதிகபட்ச விலை",
    modal_price: "சராசரி விலை",
    gov_verified: "அரசு அங்கீகாரம் பெற்றது",
    mandi_header: "மண்டி விலை நிலவரம்",
    trend_header: "7 நாள் விலை போக்கு (₹/குவிண்டால்)",
    buyers_header: "சரிபார்க்கப்பட்ட மொத்த வியாபாரிகள்",
    dealers_header: "உரம், விதை மற்றும் பூச்சிக்கொல்லி விற்பனையாளர்கள்",
    stock_status: "கையிருப்பு:",
    rating: "மதிப்பீடு",
    whats_app_chat: "வாட்ஸ்அப்",
    call: "அழைக்க",
    prompt_placeholder: "கேளுங்கள் எ.கா. 'சென்னையில் தக்காளி விலை'...",
    send: "அனுப்பு",
    offline_mode: "ஆஃப்லைன் பயன்முறை",
    last_updated: "கடைசி புதுப்பிப்பு",
    no_records: "விலை விவரங்கள் கிடைக்கவில்லை. வேறு மண்டி அல்லது பயிரைத் தேர்ந்தெடுக்கவும்.",
    msp: "குறைந்தபட்ச ஆதரவு விலை (MSP)",
    greeting: "வணக்கம்! உங்கள் விவசாயம் சார்ந்த கேள்விகளுக்கு நான் எவ்வாறு உதவ முடியும்?"
  },
  te: {
    app_title: "కృషిమిత్ర AI",
    tagline: "మీ స్థానిక మార్కెట్ & వ్యవసాయ సహాయకుడు",
    tab_assistant: "వాయిస్ అసిస్టెంట్",
    not_found_alert: "ఈ మార్కెట్‌లో ఈ పంటకు సంబంధించిన ధర రికార్డులు లభ్యం కాలేదు.",
    not_found_suggestion: "మీరు ఇతర పంటల ధరలను చూడాలనుకుంటున్నారా?",
    tab_mandi: "మార్కెట్ ధరలు",
    tab_market: "మార్కెట్‌ప్లేస్",
    tab_whatsapp: "వాట్సాప్ చాట్",
    btn_mic_start: "మాట్లాడటానికి నొక్కండి",
    btn_mic_stop: "వింటోంది... ఆపడానికి నొక్కండి",
    btn_upload_csv: "ధరలను అప్‌లోడ్ చేయండి (CSV)",
    select_lang: "భాషను ఎంచుకోండి",
    select_state: "రాష్ట్రాన్ని ఎంచుకోండి",
    select_district: "జిల్లాను ఎంచుకోండి",
    select_mandi: "మార్కెట్/మండి ఎంచుకోండి",
    select_commodity: "పంటను ఎంచుకోండి",
    min_price: "కనిష్ట ధర",
    max_price: "గరిష్ట ధర",
    modal_price: "మోడల్ ధర",
    gov_verified: "అధికారిక ప్రభుత్వ సమాచారం",
    mandi_header: "మండి ధరల డ్యాష్‌బోర్డ్",
    trend_header: "7 రోజుల ధరల ధోరణి (₹/క్వింటాల్)",
    buyers_header: "ధృవీకరించబడిన హోల్‌సేల్ వ్యాపారులు",
    dealers_header: "ఎరువులు, విత్తనాలు మరియు పురుగుమందుల డీలర్లు",
    stock_status: "స్టాక్ లభ్యత:",
    rating: "రేటింగ్",
    whats_app_chat: "వాట్సాప్",
    call: "కాల్ చేయండి",
    prompt_placeholder: "అడగండి ఉదా. 'వరంగల్‌లో మిర్చి ధర ఎంత'...",
    send: "పంపండి",
    offline_mode: "ఆఫ్‌లైన్ మోడ్ (పాత ధరలు సక్రియంగా ఉన్నాయి)",
    last_updated: "చివరి అప్‌డేట్",
    no_records: "ధరల వివరాలు లభ్యం కాలేదు. వేరే మండి లేదా పంటను ఎంచుకోండి.",
    msp: "కనీస మద్దతు ధర (MSP)",
    greeting: "నమస్కారం! మీ వ్యవసాయ సంబంధిత సందేహాలకు నేను ఎలా సహాయపడగలను?"
  },
  ml: {
    app_title: "കൃഷിമിത്ര AI",
    tagline: "നിങ്ങളുടെ പ്രാദേശിക ചന്ത നിരക്കുകളും കൃഷി സഹായിയും",
    tab_assistant: "വോയ്സ് അസിസ്റ്റന്റ്",
    not_found_alert: "ഈ മാർക്കറ്റിൽ ഈ വിളയുടെ സജീവ വില വിവരങ്ങൾ ലഭ്യമല്ല.",
    not_found_suggestion: "മറ്റ് വിളകളുടെ വില പരിശോധിക്കാൻ താൽപ്പര്യമുണ്ടോ?",
    tab_mandi: "മാർക്കറ്റ് നിരക്ക്",
    tab_market: "മാർക്കറ്റ്പ്ലെയ്സ്",
    tab_whatsapp: "വാട്ട്സ്ആപ്പ് ചാറ്റ്",
    btn_mic_start: "സംസാരിക്കാൻ അമർത്തുക",
    btn_mic_stop: "ശ്രദ്ധിക്കുന്നു... നിർത്താൻ അമർത്തുക",
    btn_upload_csv: "നിരക്കുകൾ അപ്‌ലോഡ് ചെയ്യുക (CSV)",
    select_lang: "ഭാഷ തിരഞ്ഞെടുക്കുക",
    select_state: "സംസ്ഥാനം തിരഞ്ഞെടുക്കുക",
    select_district: "ജില്ല തിരഞ്ഞെടുക്കുക",
    select_mandi: "മാർക്കറ്റ് തിരഞ്ഞെടുക്കുക",
    select_commodity: "വിള തിരഞ്ഞെടുക്കുക",
    min_price: "കുറഞ്ഞ നിരക്ക്",
    max_price: "കൂടിയ നിരക്ക്",
    modal_price: "ശരാശരി നിരക്ക്",
    gov_verified: "ഔദ്യോഗിക സർക്കാർ സ്രോതസ്സ്",
    mandi_header: "വിപണി നിരക്ക് ഡാഷ്‌ബോർഡ്",
    trend_header: "കഴിഞ്ഞ 7 ദിവസങ്ങളിലെ വില വ്യതിയാനം (₹/ക്വിന്റൽ)",
    buyers_header: "സ്ഥിരീകരിച്ച മൊത്തവ്യാപാരികൾ",
    dealers_header: "വളം, വിത്ത്, കീടനാശിനി ഡീലർമാർ",
    stock_status: "ലഭ്യമായ സ്റ്റോക്ക്:",
    rating: "റേറ്റിംഗ്",
    whats_app_chat: "വാട്ട്സ്ആപ്പ്",
    call: "വിളിക്കുക",
    prompt_placeholder: "ചോദിക്കൂ ഉദാഹരണത്തിന് 'ഏലക്കായുടെ ഇന്നത്തെ വില'...",
    send: "അയക്കുക",
    offline_mode: "ഓഫ്‌ലൈൻ മോഡ്",
    last_updated: "അവസാനം പുതുക്കിയത്",
    no_records: "വില വിവരങ്ങൾ ലഭ്യമല്ല. മറ്റൊരു മാർക്കറ്റോ വിളയോ തിരഞ്ഞെടുക്കുക.",
    msp: "താങ്ങുവില (MSP)",
    greeting: "നമസ്കാരം! നിങ്ങളുടെ കൃഷി സംശയങ്ങൾക്ക് ഞാൻ എങ്ങനെ സഹായിക്കണം?"
  },
  pa: {
    app_title: "ਕ੍ਰਿਸ਼ੀਮਿੱਤਰ AI",
    tagline: "ਤੁਹਾਡਾ ਹਾਈਪਰਲੋਕਲ ਮੰਡੀ ਤੇ ਖੇਤੀ ਸਹਾਇਕ",
    tab_assistant: "ਆਵਾਜ਼ ਸਹਾਇਕ",
    tab_mandi: "ਮੰਡੀ ਦੇ ਭਾਅ",
    tab_market: "ਮਾਰਕੀਟਪਲੇਸ",
    tab_whatsapp: "ਵ੍ਹਟਸਐਪ ਚੈਟ",
    btn_mic_start: "ਬੋਲਣ ਲਈ ਦਬਾਓ",
    btn_mic_stop: "ਸੁਣ ਰਿਹਾ ਹਾਂ... ਰੋਕਣ ਲਈ ਦਬਾਓ",
    btn_upload_csv: "ਦਰ ਅੱਪਲੋਡ ਕਰੋ (CSV)",
    select_lang: "ਭਾਸ਼ਾ ਚੁਣੋ",
    select_state: "ਰਾਜ ਚੁਣੋ",
    select_district: "ਜ਼ਿਲ੍ਹਾ ਚੁਣੋ",
    select_mandi: "ਮੰਡੀ ਚੁਣੋ",
    select_commodity: "ਫ਼ਸਲ/ਅਨਾਜ ਚੁਣੋ",
    min_price: "ਘੱਟੋ-ਘੱਟ ਭਾਅ",
    max_price: "ਵੱਧ ਤੋਂ ਵੱਧ ਭਾਅ",
    modal_price: "ਮਾਡਲ ਭਾਅ",
    gov_verified: "ਸਰਕਾਰੀ ਪ੍ਰਮਾਣਿਤ ਸਰੋਤ",
    mandi_header: "ਮੰਡੀ ਭਾਅ ਡੈਸ਼ਬੋਰਡ",
    trend_header: "ਪਿਛਲੇ 7 ਦਿਨਾਂ ਦੇ ਭਾਅ ਦਾ ਰੁਝਾਨ (₹/ਕੁਇੰਟਲ)",
    buyers_header: "ਪ੍ਰਮਾਣਿਤ ਥੋਕ ਵਪਾਰੀ ਅਤੇ ਖਰੀਦਦਾਰ",
    dealers_header: "ਖਾਦ, ਬੀਜ ਅਤੇ ਕੀਟਨਾਸ਼ਕ ਡੀਲਰ",
    stock_status: "ਸਟਾਕ ਵਿੱਚ:",
    rating: "ਰੇਟਿੰਗ",
    whats_app_chat: "ਵ੍ਹਟਸਐਪ",
    call: "ਕਾਲ ਕਰੋ",
    prompt_placeholder: "ਪੁੱਛੋ ਜਿਵੇਂ 'ਲੁਧਿਆਣਾ ਵਿੱਚ ਕਣਕ ਦਾ ਭਾਅ'...",
    send: "ਭੇਜੋ",
    offline_mode: "ਔਫਲਾਈਨ ਮੋਡ",
    last_updated: "ਆਖ਼ਰੀ ਅੱਪਡੇਟ",
    no_records: "ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ ਮਿਲਿਆ। ਦੂਜੀ ਮੰਡੀ ਜਾਂ ਫ਼ਸਲ ਚੁਣੋ।",
    msp: "ਘੱਟੋ-ਘੱਟ ਸਮਰਥਨ ਮੁੱਲ (MSP)",
    greeting: "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਅੱਜ ਤੁਹਾਡੀ ਖੇਤੀ ਸਬੰਧੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?"
  },
  bn: {
    app_title: "কৃষিমিত্র AI",
    tagline: "আপনার স্থানীয় মান্ডি ও কৃষি সহায়ক",
    tab_assistant: "ভয়েস সহকারী",
    tab_mandi: "মান্ডির দর",
    tab_market: "মার্কেটপ্লেস",
    tab_whatsapp: "হোয়াটসঅ্যাপ চ্যাট",
    btn_mic_start: "বলতে চাপুন",
    btn_mic_stop: "শুনছি... থামাতে চাপুন",
    btn_upload_csv: "দর আপলোড করুন (CSV)",
    select_lang: "ভাষা নির্বাচন করুন",
    select_state: "রাজ্য নির্বাচন করুন",
    select_district: "জেলা নির্বাচন করুন",
    select_mandi: "মান্ডি নির্বাচন করুন",
    select_commodity: "ফসল নির্বাচন করুন",
    min_price: "সর্বনিম্ন দর",
    max_price: "সর্বোচ্চ দর",
    modal_price: "মডেল দর",
    gov_verified: "সরকারি অনুমোদিত তথ্য",
    mandi_header: "মান্ডির দর ড্যাশবোর্ড",
    trend_header: "বিগত ৭ দিনের দামের গতিপ্রকৃতি (₹/কুইন্টাল)",
    buyers_header: "যাচাইকৃত পাইকারি ব্যবসায়ী ও ক্রেতা",
    dealers_header: "সার, বীজ এবং কীটনাশক বিক্রেতা",
    stock_status: "স্টকে আছে:",
    rating: "রেটিং",
    whats_app_chat: "হোয়াটসঅ্যাপ",
    call: "কল করুন",
    prompt_placeholder: "জিজ্ঞাসা করুন যেমন 'বর্ধমান মান্ডিতে চালের দাম'...",
    send: "পাঠান",
    offline_mode: "অফলাইন মোড",
    last_updated: "সর্বশেষ আপডেট",
    no_records: "কোনো তথ্য পাওয়া যায়নি। অন্য মান্ডি বা ফসল বেছে নিন।",
    msp: "ন্যূনতম সহায়ক মূল্য (MSP)",
    greeting: "নমস্কার! আজ আপনার কৃষি সংক্রান্ত বিষয়ে আমি কীভাবে সাহায্য করতে পারি?"
  },
  or: {
    app_title: "କୃଷିମିତ୍ର AI",
    tagline: "ଆପଣଙ୍କ ହାଇପରଲୋକାଲ ମଣ୍ଡି ଓ କୃଷି ସହାୟକ",
    tab_assistant: "ଭଏସ୍ ସହାୟକ",
    not_found_alert: "ଏହି ମଣ୍ଡିରେ ଏହି ଫସଲ ପାଇଁ କୌଣସି ସକ୍ରିୟ ଦର ମିଳିଲା ନାହିଁ।",
    not_found_suggestion: "ଆପଣ ଅନ୍ୟ କୌଣସି ଫସଲର ଦର ଯାଞ୍ଚ କରିବାକୁ ଚାହାଁନ୍ତି କି?",
    tab_mandi: "ମଣ୍ଡି ଦର",
    tab_market: "ବଜାର (ମାର୍କେଟ)",
    tab_whatsapp: "ହ୍ୱାଟ୍ସଆପ୍ ଚାଟ୍",
    btn_mic_start: "କହିବା ପାଇଁ ଦବାନ୍ତୁ",
    btn_mic_stop: "ଶୁଣୁଛି... ବନ୍ଦ କରିବା ପାଇଁ ଦବାନ୍ତୁ",
    btn_upload_csv: "ଦର ଅପଲୋଡ କରନ୍ତୁ (CSV)",
    select_lang: "ଭାଷା ବାଛନ୍ତୁ",
    select_state: "ରାଜ୍ୟ ବାଛନ୍ତୁ",
    select_district: "ଜିଲ୍ଲା ବାଛନ୍ତୁ",
    select_mandi: "ମଣ୍ଡି ବାଛନ୍ତୁ",
    select_commodity: "ଫସଲ/ଶସ୍ୟ ବାଛନ୍ତୁ",
    min_price: "ସର୍ବନିମ୍ନ ଦର",
    max_price: "ସର୍ବାଧିକ ଦର",
    modal_price: "ମଡେଲ ଦର",
    gov_verified: "ସରକାରୀ ପ୍ରମାଣିତ ତଥ୍ୟ",
    mandi_header: "ମଣ୍ଡି ଦର ଡ୍ୟାସବୋର୍ଡ",
    trend_header: "୭ ଦିନର ଦର ଟ୍ରେଣ୍ଡ (₹/କ୍ୱିଣ୍ଟାଲ)",
    buyers_header: "ପ୍ରମାଣିତ ହୋଲସେଲ ବ୍ୟବସାୟୀ ଓ କ୍ରେତା",
    dealers_header: "ସାର, ବିହନ ଏବଂ କୀଟନାଶକ ବିକ୍ରେତା",
    stock_status: "ଷ୍ଟକରେ ଅଛି:",
    rating: "ରେଟିଂ",
    whats_app_chat: "ହ୍ୱାଟ୍ସଆପ୍",
    call: "କଲ୍ କରନ୍ତୁ",
    prompt_placeholder: "ପଚାରନ୍ତୁ ଯେପରି 'ଭୁବନେଶ୍ୱରରେ ଧାନର ଦର'...",
    send: "ପଠାନ୍ତୁ",
    offline_mode: "ଅଫଲାଇନ୍ ମୋଡ୍",
    last_updated: "ଶେଷ ଅପଡେଟ୍",
    no_records: "କୌଣସି ଦର ରେକର୍ଡ ମିଳିଲା ନାହିଁ। ଅନ୍ୟ ମଣ୍ଡି ବାଛନ୍ତୁ।",
    msp: "ସର୍ବନିମ୍ନ ସହାୟକ ମୂଲ୍ୟ (MSP)",
    greeting: "ନମସ୍କାର! ଆଜି ଆପଣଙ୍କ କୃଷି ସମ୍ବନ୍ଧୀୟ ପ୍ରଶ୍ନରେ ମୁଁ କିପରି ସାହାଯ୍ୟ କରିପାରିବି?"
  },
  as: {
    app_title: "কৃষিমিত্ৰ AI",
    tagline: "আপোনাৰ স্থানীয় মণ্ডি আৰু কৃষি সহায়ক",
    tab_assistant: "ভইচ সহায়ক",
    tab_mandi: "মণ্ডিৰ দৰ",
    tab_market: "বজাৰ (মার্কেট)",
    tab_whatsapp: "হোৱাটছএপ চেট",
    btn_mic_start: "ক'বলৈ টিপক",
    btn_mic_stop: "শুনি আছোঁ... বন্ধ কৰিবলৈ টিপক",
    btn_upload_csv: "দৰ আপলোড কৰক (CSV)",
    select_lang: "ভাষা বাছক",
    select_state: "ৰাজ্য বাছক",
    select_district: "জিলা বাছক",
    select_mandi: "মণ্ডি বাছক",
    select_commodity: "শস্য বাছক",
    min_price: "সৰ্বনিম্ন দৰ",
    max_price: "সৰ্বোচ্চ দৰ",
    modal_price: "মডেল দৰ",
    gov_verified: "চৰকাৰী প্ৰমাণিত উৎস",
    mandi_header: "মণ্ডিৰ দৰ ডেশ্বব'ৰ্ড",
    trend_header: "৭ দিনৰ দৰৰ গতিধাৰা (₹/কুইণ্টল)",
    buyers_header: "প্ৰমাণিত পাইকাৰী ব্যৱসায়ী আৰু ক্ৰেতা",
    dealers_header: "সাৰ, বীজ আৰু কীটনাশক বিক্ৰেতা",
    stock_status: "ষ্টকত আছে:",
    rating: "ৰেটিং",
    whats_app_chat: "হোৱাটছএপ",
    call: "কল কৰক",
    prompt_placeholder: "সোধক যেনে 'গুৱাহাটীত আলুৰ দাম কিমান'...",
    send: "প্ৰেৰণ কৰক",
    offline_mode: "অফলাইন ম'ড",
    last_updated: "সৰ্বশেষ আপডেট",
    no_records: "কোনো দৰ পোৱা নগ'ল। অন্য মণ্ডি বা শস্য বাছক।",
    msp: "নূন্যতম সমৰ্থন মূল্য (MSP)",
    greeting: "নমস্কাৰ! আজি আপোনাৰ কৃষি সম্বন্ধীয় সমস্যাত মই কেনেকৈ সহায় কৰিব পাৰোঁ?"
  },
  ks: {
    app_title: "کرٛشۍمِتَر AI",
    tagline: "تُہُند لوکل منڈی تہٕ کھیتی باڑی مددگار",
    tab_assistant: "آواز مددگار",
    tab_mandi: "منڈی قٟمَتھ",
    tab_market: "مارکیٹ",
    tab_whatsapp: "واٹس ایپ چیٹ",
    btn_mic_start: "تھاو کَتھ کرنہٕ باپتھ",
    btn_mic_stop: "بوزان چُھ... رُکاو کَتھ",
    btn_upload_csv: "قٟمَتھ اَپلوڈ کٔرِو (CSV)",
    select_lang: "زَبان چُھنوو",
    select_state: "ریاسَتھ چُھنوو",
    select_district: "ضِلہٕ چُھنوو",
    select_mandi: "منڈی چُھنوو",
    select_commodity: "فَصٕل چُھنوو",
    min_price: "کم ترین قٟمَتھ",
    max_price: "زیٛادٕ قٟمَتھ",
    modal_price: "عام قٟمَتھ",
    gov_verified: "سرکٲرۍ تصدیق شُدٕ",
    mandi_header: "منڈی قٟمَتھ ڈیش بورڈ",
    trend_header: "۷ دۄہَن ہُنٛد قٟمَتھ رُجحان (₹/کوئنٹل)",
    buyers_header: "تصدیق شُدٕ ہول سیل تاجر",
    dealers_header: "کھاد، بیٚول تہٕ دوا وِکنے وٲلۍ",
    stock_status: "سٹاک مَنٛز:",
    rating: "ریٹنگ",
    whats_app_chat: "واٹس ایپ",
    call: "کال کٔرِو",
    prompt_placeholder: "پرِژھِو مِثال: 'سوپور مَنٛز ژوٗنٛٹھ ہُنٛد قٟمَتھ' ...",
    send: "سوزِو",
    offline_mode: "آف لائن موڈ",
    last_updated: "ٲخری اَپڈیٹ",
    no_records: "کانٛہہ قٟمَتھ مِلیو نہٕ۔ دوٚیم منڈی چُھنوو۔",
    msp: "سرکٲرۍ حِمایتی قٟمَتھ (MSP)",
    greeting: "سلام! بٕہ کِتھ پٲٹھۍ ہٮ۪کاو تُہنٛز کٔشیرۍ کھیتی باڑی سوالَن مَنٛز مَدَتھ کٔرِتھ؟"
  }
};

const LANGUAGES = [
  { code: "en", name: "English" },
  { code: "hi", name: "हिंदी (Hindi)" },
  { code: "kn", name: "ಕನ್ನಡ (Kannada)" },
  { code: "gu", name: "ગુજરાતી (Gujarati)" },
  { code: "mr", name: "मराठी (Marathi)" },
  { code: "ta", name: "தமிழ் (Tamil)" },
  { code: "te", name: "తెలుగు (Telugu)" },
  { code: "ml", name: "മലയാളം (Malayalam)" },
  { code: "pa", name: "ਪੰਜਾਬੀ (Punjabi)" },
  { code: "bn", name: "বাংলা (Bengali)" },
  { code: "or", name: "ଓଡ଼ିଆ (Odia)" },
  { code: "as", name: "অসমীয়া (Assamese)" },
  { code: "ks", name: "کٲشُر (Kashmiri)" }
];

export default function Home() {
  const [lang, setLang] = useState<string>("en");
  const getTranslation = (l: string) => {
    if (TRANSLATIONS[l]) return TRANSLATIONS[l];
    return TRANSLATIONS["en"]; // Fallback to English
  };
  const t = getTranslation(lang);
  const [activeTab, setActiveTab] = useState<"assistant" | "mandi" | "market" | "whatsapp">("assistant");
  
  // State for offline detection
  const [isOffline, setIsOffline] = useState(false);
  
  // API URL Config
  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  // Mandi Dropdown States
  const [states, setStates] = useState<string[]>([]);
  const [districts, setDistricts] = useState<string[]>([]);
  const [mandis, setMandis] = useState<any[]>([]);
  const [commodities, setCommodities] = useState<any[]>([]);

  const [selectedState, setSelectedState] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [selectedMandi, setSelectedMandi] = useState("");
  const [selectedCommodity, setSelectedCommodity] = useState("");
  
  const [priceData, setPriceData] = useState<any>(null);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [upagOutlook, setUpagOutlook] = useState<any>(null);

  // Marketplace states
  const [buyers, setBuyers] = useState<any[]>([]);
  const [dealers, setDealers] = useState<any[]>([]);
  const [marketCommodityFilter, setMarketCommodityFilter] = useState("");
  const [marketDistrictFilter, setMarketDistrictFilter] = useState("");
  
  // Reservation states
  const [selectedDealerForReservation, setSelectedDealerForReservation] = useState<any>(null);
  const [dealerInventory, setDealerInventory] = useState<any[]>([]);
  const [reservationSuccess, setReservationSuccess] = useState<any>(null);
  const [reservationPhone, setReservationPhone] = useState("");

  // Admin upload states
  const [showAdminUploadModal, setShowAdminUploadModal] = useState(false);
  const [csvInput, setCsvInput] = useState("");
  const [adminPin, setAdminPin] = useState("");
  const [uploadStatus, setUploadStatus] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleAdminUpload = (csvText?: string) => {
    const payloadCsv = csvText || csvInput;
    if (!adminPin.trim()) {
      alert("Please enter the Admin Security PIN.");
      return;
    }
    if (!payloadCsv.trim()) {
      alert("Please paste CSV data or select a CSV file.");
      return;
    }
    setIsUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    formData.append("csv_text", payloadCsv);
    formData.append("admin_pin", adminPin.trim());

    fetch(`${BACKEND_URL}/api/admin/upload-rates`, {
      method: "POST",
      headers: {
        "X-Admin-PIN": adminPin.trim()
      },
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        setIsUploading(false);
        setUploadStatus(data);
        if (data.success) {
          fetch(`${BACKEND_URL}/api/mandi/states`)
            .then(r => r.json())
            .then(st => setStates(st));
        }
      })
      .catch(() => {
        setIsUploading(false);
        setUploadStatus({ success: false, detail: "Error connecting to backend server." });
      });
  };

  // Assistant states
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const [inputText, setInputText] = useState("");
  const [chatLog, setChatLog] = useState<Array<{ sender: "user" | "bot"; text: string }>>([
    { sender: "bot", text: getTranslation(lang).greeting }
  ]);

  // WhatsApp simulation states
  const [waText, setWaText] = useState("");
  const [isWaListening, setIsWaListening] = useState(false);
  const [waLog, setWaLog] = useState<Array<{ sender: "user" | "bot"; text: string; time: string }>>([
    { sender: "bot", text: getTranslation(lang).greeting, time: "12:00 PM" }
  ]);

  // Chat auto-scroll refs
  const assistantEndRef = useRef<HTMLDivElement>(null);
  const waEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll when messages are added
  useEffect(() => {
    assistantEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatLog]);

  useEffect(() => {
    waEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [waLog]);

  // Trigger TTS voice synthesis with markdown stripping, natural date formatting, and voice selection
  const speakText = (text: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      
      const monthsEn = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
      const monthsHi = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"];
      const monthsKn = ["ಜನವರಿ", "ಫೆಬ್ರವರಿ", "ಮಾರ್ಚ್", "ಏಪ್ರಿಲ್", "ಮೇ", "ಜೂನ್", "ಜುಲೈ", "ಆಗಸ್ಟ್", "ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್", "ನವೆಂಬರ್", "ಡಿಸೆಂಬರ್"];
      const monthsTa = ["ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்", "ஜூலை", "ஆகஸ்ட்", "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"];

      let monthList = monthsEn;
      if (lang === "hi") monthList = monthsHi;
      else if (lang === "kn") monthList = monthsKn;
      else if (lang === "ta") monthList = monthsTa;

      // Clean markdown formatting (*, #, •, bullet points, links) and naturalize dates (YYYY-MM-DD -> 5 September 2026)
      const cleanText = text
        .replace(/(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})/g, (_, y, m, d) => {
          const monthName = monthList[parseInt(m, 10) - 1] || m;
          return `${parseInt(d, 10)} ${monthName} ${y}`;
        })
        .replace(/(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})/g, (_, d, m, y) => {
          const monthName = monthList[parseInt(m, 10) - 1] || m;
          return `${parseInt(d, 10)} ${monthName} ${y}`;
        })
        .replace(/[*#_`~•]/g, "")
        .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
        .replace(/http[s]?:\/\/\S+/g, "")
        .replace(/\n+/g, ". ");

      const utterance = new SpeechSynthesisUtterance(cleanText);
      const voiceLangs: Record<string, string> = {
        hi: "hi-IN", kn: "kn-IN", gu: "gu-IN", mr: "mr-IN",
        ta: "ta-IN", te: "te-IN", ml: "ml-IN", pa: "pa-IN", bn: "bn-IN",
        or: "or-IN", as: "as-IN", ks: "ur-IN", en: "en-IN"
      };
      utterance.lang = voiceLangs[lang] || "en-IN";
      utterance.rate = 0.95; // Calm, natural pacing
      utterance.pitch = 1.05; // Warm, pleasant pitch

      // Try selecting preferred native voice engine if available
      try {
        const voices = window.speechSynthesis.getVoices();
        const targetLangCode = (voiceLangs[lang] || "en-IN").split("-")[0];
        const preferredVoice = voices.find(v => 
          v.lang.toLowerCase().startsWith(targetLangCode) ||
          v.lang.toLowerCase().includes(targetLangCode) ||
          (lang === "or" && v.name.toLowerCase().includes("odia")) ||
          (lang === "as" && v.name.toLowerCase().includes("assamese")) ||
          (lang === "bn" && v.name.toLowerCase().includes("bengali")) ||
          (lang === "mr" && v.name.toLowerCase().includes("marathi")) ||
          (lang === "gu" && v.name.toLowerCase().includes("gujarati")) ||
          (lang === "te" && v.name.toLowerCase().includes("telugu")) ||
          (lang === "pa" && v.name.toLowerCase().includes("punjabi")) ||
          (lang === "ml" && v.name.toLowerCase().includes("malayalam")) ||
          (lang === "en" && (v.lang.includes("en-IN") || v.name.includes("India")))
        );
        if (preferredVoice) {
          utterance.voice = preferredVoice;
        }
      } catch (e) {}

      window.speechSynthesis.speak(utterance);
    }
  };

  // Sync default greetings when language changes
  useEffect(() => {
    setChatLog([
      { sender: "bot", text: getTranslation(lang).greeting }
    ]);
    setWaLog([
      { sender: "bot", text: getTranslation(lang).greeting, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
    ]);
  }, [lang]);

  // Load Initial Metadata
  useEffect(() => {
    // Check if offline
    if (typeof window !== "undefined") {
      setIsOffline(!window.navigator.onLine);
      window.addEventListener("online", () => setIsOffline(false));
      window.addEventListener("offline", () => setIsOffline(true));
    }

    fetch(`${BACKEND_URL}/api/mandi/states`)
      .then(res => res.json())
      .then(data => setStates(data))
      .catch(err => {
        console.error("Failed to load states:", err);
        // Load fallback offline states
        setStates(["Karnataka", "Madhya Pradesh", "Maharashtra"]);
      });

    fetch(`${BACKEND_URL}/api/mandi/commodities`)
      .then(res => res.json())
      .then(data => setCommodities(data))
      .catch(err => {
        console.error("Failed to load commodities:", err);
        setCommodities([
          { id: "1", commodity_name: "Maize", local_name: '{"en":"Maize","hi":"मक्का","kn":"ಮೆಕ್ಕೆಜೋಳ"}' },
          { id: "2", commodity_name: "Wheat", local_name: '{"en":"Wheat","hi":"गेहूं","kn":"ಗೋಧಿ"}' },
          { id: "3", commodity_name: "Onion", local_name: '{"en":"Onion","hi":"प्याज","kn":"ಈರುಳ್ಳಿ"}' }
        ]);
      });
      
    // Load marketplace
    loadMarketplace();
  }, []);

  // Parse incoming URL query params (e.g. from chatbot link clicks)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const tabParam = params.get("tab");
      const mandiParam = params.get("mandi");
      const commodityParam = params.get("commodity");

      if (tabParam || mandiParam) {
        // Clear query parameters in browser search bar for clean UX
        window.history.replaceState({}, document.title, window.location.pathname);
        
        if (tabParam === "marketplace" || tabParam === "market") {
          setActiveTab("market");
        } else if (tabParam === "whatsapp") {
          setActiveTab("whatsapp");
        } else if (tabParam === "assistant") {
          setActiveTab("assistant");
        }

        if (mandiParam) {
          setActiveTab("mandi");
          fetch(`${BACKEND_URL}/api/mandi/details?mandi_name=${encodeURIComponent(mandiParam)}`)
            .then(res => res.json())
            .then(details => {
              if (details.state && details.district) {
                setSelectedState(details.state);
                setSelectedDistrict(details.district);
                setSelectedMandi(details.mandi_name);
                if (commodityParam) {
                  setSelectedCommodity(commodityParam);
                }
              }
            })
            .catch(err => console.error("Error loading query param details:", err));
        }
      }
    }
  }, [states, commodities]);

  // Handle internal in-place link navigation (e.g. from chatbot "Click Here" trends link)
  const handleInternalLinkClick = (url: string): boolean => {
    try {
      let parsedUrl: URL;
      if (url.startsWith("http://") || url.startsWith("https://")) {
        parsedUrl = new URL(url);
      } else {
        parsedUrl = new URL(url, "https://krishi-mitra.local");
      }

      const tabParam = parsedUrl.searchParams.get("tab");
      const mandiParam = parsedUrl.searchParams.get("mandi");
      const commodityParam = parsedUrl.searchParams.get("commodity");

      if (tabParam === "marketplace" || tabParam === "market") {
        setActiveTab("market");
        return true;
      } else if (tabParam === "whatsapp") {
        setActiveTab("whatsapp");
        return true;
      } else if (tabParam === "assistant") {
        setActiveTab("assistant");
        return true;
      }

      if (tabParam === "mandi" || mandiParam) {
        setActiveTab("mandi");
        if (mandiParam) {
          fetch(`${BACKEND_URL}/api/mandi/details?mandi_name=${encodeURIComponent(mandiParam)}`)
            .then(res => res.json())
            .then(details => {
              if (details && details.state && details.district) {
                setSelectedState(details.state);
                setSelectedDistrict(details.district);
                setSelectedMandi(details.mandi_name);
                if (commodityParam) {
                  setSelectedCommodity(commodityParam);
                }
              }
            })
            .catch(err => console.error("Error navigating to mandi details:", err));
        } else if (commodityParam) {
          setSelectedCommodity(commodityParam);
        }
        return true;
      }
    } catch (e) {
      console.error("Error parsing link URL:", e);
    }
    return false;
  };

  // Validate and sanitize URLs to allow only safe http/https or relative paths
  const sanitizeLinkUrl = (url: string): string | null => {
    if (!url) return null;
    const trimmed = url.trim();
    if (!trimmed) return null;

    try {
      // Allow only root-relative paths (single leading slash, not protocol-relative).
      if (trimmed.startsWith("/")) {
        if (!/^\/(?!\/)/.test(trimmed)) {
          return null;
        }
        const parsedRelative = new URL(trimmed, "https://krishimitra.local");
        return parsedRelative.pathname + parsedRelative.search + parsedRelative.hash;
      }

      // Allow only absolute http/https URLs and return canonicalized href.
      const parsed = new URL(trimmed);
      if (parsed.protocol === "http:" || parsed.protocol === "https:") {
        return parsed.href;
      }
    } catch {
      return null;
    }
    return null;
  };

  // Render user message: strictly plain formatted text with bold markers only. Zero anchor tags or linkification.
  const renderUserMessage = (text: string) => {
    const lines = text.split("\n");
    return lines.map((line, lineIdx) => {
      if (!line.trim()) {
        return <span key={lineIdx} className="block h-2" />;
      }
      return (
        <span key={lineIdx} className="block leading-relaxed break-words [overflow-wrap:anywhere]">
          {renderBoldText(line, `${lineIdx}-user-full`, true)}
        </span>
      );
    });
  };

  // Helper to render formatted chat messages with bold, clickable internal hyperlinks, and zero overflow
  const renderFormattedMessage = (text: string, isUser = false) => {
    if (isUser) {
      return renderUserMessage(text);
    }
    const lines = text.split("\n");
    return lines.map((line, lineIdx) => {
      if (!line.trim()) {
        return <span key={lineIdx} className="block h-2" />;
      }

      // Regex matches markdown link [label](url) OR bare URL http(s)://...
      const linkRegex = /\[([^\]]+)\]\((https?:\/\/[^\s\)]+|\/[^\s\)]+)\)|(https?:\/\/[^\s\)]+)/g;
      const elements: React.ReactNode[] = [];
      let lastIndex = 0;
      let match;

      while ((match = linkRegex.exec(line)) !== null) {
        if (match.index > lastIndex) {
          elements.push(renderBoldText(line.substring(lastIndex, match.index), `${lineIdx}-${lastIndex}`, false));
        }

        const isMdLink = Boolean(match[1] && match[2]);
        const linkText = isMdLink ? match[1] : "Click Here";
        const rawLinkUrl = isMdLink ? match[2] : match[3];
        const safeLinkUrl = sanitizeLinkUrl(rawLinkUrl);

        if (!safeLinkUrl) {
          elements.push(renderBoldText(match[0], `${lineIdx}-raw-${match.index}`, false));
          lastIndex = match.index + match[0].length;
          continue;
        }

        elements.push(
          <button
            type="button"
            key={`${lineIdx}-link-${match.index}`}
            onClick={() => {
              if (!handleInternalLinkClick(safeLinkUrl)) {
                try {
                  const targetUrl = new URL(safeLinkUrl, window.location.origin);
                  if (targetUrl.protocol === "http:" || targetUrl.protocol === "https:") {
                    window.open(targetUrl.href, "_blank", "noopener,noreferrer");
                  }
                } catch {
                  // ignore
                }
              }
            }}
            className="font-bold underline underline-offset-2 transition-colors cursor-pointer inline-flex items-center gap-0.5 mx-0.5 break-all text-primary-600 hover:text-primary-800 decoration-primary-400 hover:decoration-primary-700 bg-green-50/80 hover:bg-green-100/90 px-1.5 py-0.5 rounded text-left"
          >
            {linkText}
            <span className="text-[11px] opacity-75">↗</span>
          </button>
        );

        lastIndex = match.index + match[0].length;
      }

      if (lastIndex < line.length) {
        elements.push(renderBoldText(line.substring(lastIndex), `${lineIdx}-${lastIndex}`, false));
      }

      return (
        <span key={lineIdx} className="block break-words [overflow-wrap:anywhere]">
          {elements}
        </span>
      );
    });
  };

  const renderBoldText = (str: string, keyPrefix: string, isUser = false): React.ReactNode => {
    const boldRegex = /\*([^*]+)\*/g;
    const parts: React.ReactNode[] = [];
    let lastIdx = 0;
    let bMatch;

    while ((bMatch = boldRegex.exec(str)) !== null) {
      if (bMatch.index > lastIdx) {
        parts.push(str.substring(lastIdx, bMatch.index));
      }
      parts.push(
        <strong key={`${keyPrefix}-b-${bMatch.index}`} className={isUser ? "font-bold text-white" : "font-bold text-gray-900"}>
          {bMatch[1]}
        </strong>
      );
      lastIdx = bMatch.index + bMatch[0].length;
    }
    if (lastIdx < str.length) {
      parts.push(str.substring(lastIdx));
    }
    return parts.length > 0 ? parts : str;
  };

  const openReservationModal = (dealer: any) => {
    setSelectedDealerForReservation(dealer);
    setReservationSuccess(null);
    setReservationPhone("");
    setDealerInventory([]);
    
    // Fetch inventory
    fetch(`${BACKEND_URL}/api/marketplace/inventory/${dealer.id}`)
      .then(res => res.json())
      .then(data => {
        // add quantity state to each item
        setDealerInventory(data.map((item: any) => ({ ...item, reserveQty: 1 })));
      })
      .catch(err => console.error("Error fetching inventory", err));
  };

  const handleReserve = (inventoryId: string, reserveQty: number) => {
    if (!reservationPhone || reservationPhone.length < 10) {
      alert("Please enter a valid phone number.");
      return;
    }
    
    fetch(`${BACKEND_URL}/api/marketplace/reserve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dealer_id: selectedDealerForReservation.id,
        inventory_id: inventoryId,
        quantity: reserveQty,
        farmer_phone: reservationPhone
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setReservationSuccess(data);
          // Refresh inventory after booking
          openReservationModal(selectedDealerForReservation);
        } else {
          alert(data.error || "Reservation failed.");
        }
      })
      .catch(err => alert("Error reserving inventory."));
  };

  const loadMarketplace = (comm = "", dist = "") => {
    fetch(`${BACKEND_URL}/api/marketplace/buyers?commodity=${comm}&district=${dist}`)
      .then(res => res.json())
      .then(data => setBuyers(data))
      .catch(() => {});
      
    fetch(`${BACKEND_URL}/api/marketplace/dealers?location=${dist}`)
      .then(res => res.json())
      .then(data => setDealers(data))
      .catch(() => {});
  };

  // State Change handler
  useEffect(() => {
    if (!selectedState) return;
    fetch(`${BACKEND_URL}/api/mandi/districts?state=${selectedState}`)
      .then(res => res.json())
      .then(data => setDistricts(data))
      .catch(() => setDistricts([]));
  }, [selectedState]);

  // District Change handler
  useEffect(() => {
    if (!selectedState || !selectedDistrict) return;
    fetch(`${BACKEND_URL}/api/mandi/list?state=${selectedState}&district=${selectedDistrict}`)
      .then(res => res.json())
      .then(data => setMandis(data))
      .catch(() => setMandis([]));
  }, [selectedDistrict]);

  // Mandi Change handler: reload crops available in this specific mandi
  useEffect(() => {
    const url = selectedMandi 
      ? `${BACKEND_URL}/api/mandi/commodities?mandi_name=${encodeURIComponent(selectedMandi)}`
      : `${BACKEND_URL}/api/mandi/commodities`;
      
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setCommodities(data);
        if (selectedMandi && selectedCommodity && !data.some((c: any) => c.commodity_name?.toLowerCase() === selectedCommodity.toLowerCase())) {
          setSelectedCommodity("");
        }
      })
      .catch(() => {});
  }, [selectedMandi]);

  // Fetch prices when mandi & commodity selected
  useEffect(() => {
    if (!selectedState || !selectedDistrict || !selectedMandi || !selectedCommodity) return;

    fetch(`${BACKEND_URL}/api/mandi/price?state=${selectedState}&district=${selectedDistrict}&mandi_name=${selectedMandi}&commodity_name=${selectedCommodity}`)
      .then(res => res.json())
      .then(data => {
        setPriceData(data);
      })
      .catch(() => setPriceData(null));

    fetch(`${BACKEND_URL}/api/mandi/trend?mandi_name=${selectedMandi}&commodity_name=${selectedCommodity}`)
      .then(res => res.json())
      .then(data => {
        setTrendData(data.trend || []);
      })
      .catch(() => setTrendData([]));

    // Fetch Phase 5 UPAg Market Outlook & Advisory
    fetch(`${BACKEND_URL}/api/advisory/market-outlook?state=${encodeURIComponent(selectedState)}&commodity=${encodeURIComponent(selectedCommodity)}`)
      .then(res => res.json())
      .then(data => {
        setUpagOutlook(data.error ? null : data);
      })
      .catch(() => setUpagOutlook(null));
  }, [selectedMandi, selectedCommodity, selectedState]);

  // Cancel active speech when switching tabs
  useEffect(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  }, [activeTab]);

  // Handle Assistant Chat Query
  const handleAssistantSend = async (textToSend = inputText) => {
    if (!textToSend.trim()) return;
    
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    
    setChatLog(prev => [...prev, { sender: "user", text: textToSend }]);
    setInputText("");
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textToSend, language: lang })
      });
      
      const data = await response.json();
      setChatLog(prev => [...prev, { sender: "bot", text: data.text }]);
      
      // Auto speak the response out loud
      speakText(data.text);
    } catch (err) {
      // Offline fallback mock
      const mockReply = `Received query: "${textToSend}". Backend is seeding, simulating response. Today's Maize modal rate in Shivamogga is ₹2,320/quintal. (Offline Simulation)`;
      setChatLog(prev => [...prev, { sender: "bot", text: mockReply }]);
      speakText(mockReply);
    }
  };

  // Simulated Voice recording handler with real browser Web Speech API
  const toggleListening = () => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Defaulting to mock prompt.");
      // Fallback
      if (isListening) {
        setIsListening(false);
        handleAssistantSend("What is today's Wheat rate in Shimoga?");
      } else {
        setIsListening(true);
        setTimeout(() => {
          setIsListening(false);
          handleAssistantSend("What is today's Wheat rate in Shimoga?");
        }, 3000);
      }
      return;
    }

    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
    } else {
      setIsListening(true);
      const recognition = new SpeechRecognition();
      
      // Determine language mappings across all 13 languages
      const speechLangs: Record<string, string> = {
        hi: "hi-IN", kn: "kn-IN", gu: "gu-IN", mr: "mr-IN",
        ta: "ta-IN", te: "te-IN", ml: "ml-IN", pa: "pa-IN", bn: "bn-IN",
        or: "or-IN", as: "as-IN", ks: "ur-IN", en: "en-IN"
      };
      recognition.lang = speechLangs[lang] || "en-IN";
      recognition.continuous = false;
      recognition.interimResults = false;
      
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          handleAssistantSend(transcript);
        }
      };
      
      recognition.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current = recognition;
      recognition.start();
    }
  };

  // WhatsApp simulation send
  const handleWaSend = async () => {
    if (!waText.trim()) return;
    
    const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setWaLog(prev => [...prev, { sender: "user", text: waText, time: timeNow }]);
    const currentWaText = waText;
    setWaText("");

    try {
      // Simulate Twilio Webhook hit
      const formData = new URLSearchParams();
      formData.append("From", "whatsapp:+919876543210");
      formData.append("Body", currentWaText);
      
      const response = await fetch(`${BACKEND_URL}/api/whatsapp/twilio`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData
      });
      
      // Wait a moment and then query the backend to see what it would reply 
      // (For simulation, we call /api/query or parse directly)
      const parseResponse = await fetch(`${BACKEND_URL}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: currentWaText })
      });
      const data = await parseResponse.json();
      
      setTimeout(() => {
        setWaLog(prev => [...prev, { sender: "bot", text: data.text, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
        speakText(data.text);
      }, 700);
      
    } catch (err) {
      setTimeout(() => {
        const mockReply = `[Simulated WhatsApp reply] Target: +919876543210.\nToday's Wheat modal price in Indore is ₹2,540/quintal. Source: AGMARKNET.`;
        setWaLog(prev => [...prev, { sender: "bot", text: mockReply, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
        speakText(mockReply);
      }, 700);
    }
  };

  const handleWaVoice = () => {
    if (isWaListening) return;
    setIsWaListening(true);
    
    const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setWaLog(prev => [...prev, { sender: "user", text: "🎙️ Sending voice note...", time: timeNow }]);
    
    
      // Real Browser Speech Recognition
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
              const langMap: Record<string, string> = {
        hi: "hi-IN", kn: "kn-IN", gu: "gu-IN", mr: "mr-IN",
        ta: "ta-IN", te: "te-IN", ml: "ml-IN", pa: "pa-IN", bn: "bn-IN",
        or: "or-IN", as: "as-IN", ks: "ur-IN", en: "en-IN"
      };
      recognition.lang = langMap[lang] || "en-IN";
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        recognition.onresult = async (event: any) => {
          setIsWaListening(false);
          const queryText = event.results[0][0].transcript;
          
          setWaLog(prev => {
            const updated = [...prev];
            if (updated.length > 0) {
              updated[updated.length - 1] = {
                sender: "user",
                text: `🎤 Voice note: "${queryText}"`,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              };
            }
            return updated;
          });
          
          try {
            const formData = new URLSearchParams();
            formData.append("From", "whatsapp:+919876543210");
            formData.append("Body", queryText);
            formData.append("NumMedia", "0");
            
            await fetch(`${BACKEND_URL}/api/whatsapp/twilio`, {
              method: "POST",
              headers: { "Content-Type": "application/x-www-form-urlencoded" },
              body: formData
            });

            // Wait a moment and then query the backend to see what it would reply
            const parseResponse = await fetch(`${BACKEND_URL}/api/query`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ text: queryText })
            });
            const data = await parseResponse.json();
            
            setTimeout(() => {
              setWaLog(prev => [...prev, { sender: "bot", text: data.text, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
              speakText(data.text);
            }, 700);
          } catch (e) {
            console.error(e);
          }
        };
        
        recognition.onerror = () => {
          setIsWaListening(false);
          setWaLog(prev => [...prev, { sender: "bot", text: "Microphone error or no speech detected.", time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
        };
        
        recognition.start();
      } else {
        setIsWaListening(false);
        setWaLog(prev => [...prev, { sender: "bot", text: "Speech Recognition API not supported in this browser.", time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
      }

  };

  return (
    <div className="flex flex-col h-screen max-h-screen text-gray-800">
      
      {/* Header bar */}
      <header className="bg-primary-600 text-white p-4 flex flex-col items-center justify-between shadow">
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <img src="/logo.png" className="w-8 h-8 rounded-full border border-green-200 bg-white" alt="logo" />
            <div>
              <h1 className="font-extrabold text-xl tracking-tight">{t.app_title}</h1>
              <p className="text-xs text-green-100">{t.tagline}</p>
            </div>
          </div>
          
          {/* Language toggle selector dropdown */}
          <div className="flex items-center gap-1 border border-primary-500 rounded-lg p-1 bg-primary-700">
            <span className="text-[10px] text-green-200 font-bold px-1 hidden sm:inline">🗣️</span>
            <select
              value={lang}
              onChange={(e) => {
                const selectedVal = e.target.value;
                setLang(selectedVal);
              }}
              className="text-xs bg-primary-700 text-white rounded font-bold focus:outline-none p-1 cursor-pointer border-none"
            >
              {LANGUAGES.map(l => (
                <option key={l.code} value={l.code} className="bg-primary-700 text-white font-bold">
                  {l.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Offline indicator bar */}
        {isOffline && (
          <div className="bg-orange-500 text-white text-xs w-full text-center py-1 mt-2 rounded font-bold animate-bounce flex items-center justify-center gap-1">
            <CloudSun size={14} />
            {t.offline_mode}
          </div>
        )}
      </header>

      {/* Main Container */}
      <main className="flex-1 p-4 bg-gray-50 overflow-hidden flex flex-col min-h-0">
        
        {/* TAB 1: Voice Assistant */}
        {activeTab === "assistant" && (
          <div className="flex flex-col flex-1 h-full min-h-0 overflow-hidden gap-4">
            
            {/* Conversation Log */}
            <div className="flex-1 overflow-y-auto space-y-4 pr-1">
              {chatLog.map((chat, idx) => (
                <div 
                  key={idx} 
                  className={`flex ${chat.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div className={`rounded-2xl p-3 max-w-[85%] shadow-sm break-words [overflow-wrap:anywhere] ${
                    chat.sender === "user" 
                      ? "bg-primary-600 text-white rounded-br-none" 
                      : "bg-white text-gray-800 border border-gray-100 rounded-bl-none"
                  }`}>
                    <div className="text-sm break-words [overflow-wrap:anywhere]">
                      {chat.sender === "user" ? renderUserMessage(chat.text) : renderFormattedMessage(chat.text, false)}
                    </div>
                    {chat.sender === "bot" && (
                      <div className="flex gap-3 mt-2 border-t border-gray-100 pt-2">
                        <button 
                          onClick={() => speakText(chat.text)} 
                          className="text-xs text-primary-600 hover:text-primary-700 flex items-center gap-1 font-semibold"
                        >
                          <Volume2 size={14} /> Listen
                        </button>
                        <button 
                          onClick={() => {
                            if (typeof window !== "undefined" && "speechSynthesis" in window) {
                              window.speechSynthesis.cancel();
                            }
                          }} 
                          className="text-xs text-red-500 hover:text-red-600 flex items-center gap-1 font-semibold"
                        >
                          ⏹️ Stop
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={assistantEndRef} />
            </div>

            {/* Voice Controller & Form */}
            <div className="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm flex flex-col items-center gap-3">
              <button 
                onClick={toggleListening}
                className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${
                  isListening 
                    ? "bg-red-500 text-white animate-ping" 
                    : "bg-primary-600 text-white shadow-lg hover:bg-primary-700"
                }`}
              >
                {isListening ? <MicOff size={36} /> : <Mic size={36} />}
              </button>
              <span className="text-xs text-gray-500 font-bold">
                {isListening ? t.btn_mic_stop : t.btn_mic_start}
              </span>

              {/* Text fallback input */}
              <div className="w-full flex gap-2 border border-gray-200 rounded-xl p-1 bg-gray-50">
                <input 
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder={t.prompt_placeholder}
                  className="flex-1 bg-transparent px-3 text-sm focus:outline-none"
                  onKeyDown={(e) => e.key === "Enter" && handleAssistantSend()}
                />
                <button 
                  onClick={() => handleAssistantSend()}
                  className="bg-primary-600 text-white p-2 rounded-lg"
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: Mandi Rates */}
        {activeTab === "mandi" && (
          <div className="flex-1 overflow-y-auto space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-extrabold text-gray-900 border-l-4 border-primary-600 pl-2">{t.mandi_header}</h2>
              <button 
                onClick={() => {
                  setShowAdminUploadModal(true);
                  setUploadStatus(null);
                  setCsvInput("");
                }}
                className="text-xs bg-primary-600 hover:bg-primary-700 text-white font-bold px-3 py-1.5 rounded-lg flex items-center gap-1 shadow-sm transition cursor-pointer"
              >
                📤 {t.btn_upload_csv}
              </button>
            </div>
            
            {/* Selectors */}
            <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-3">
              <div>
                <label className="text-xs text-gray-500 font-bold block mb-1">{t.select_state}</label>
                <select 
                  value={selectedState} 
                  onChange={(e) => {
                    setSelectedState(e.target.value);
                    setSelectedDistrict("");
                    setSelectedMandi("");
                  }}
                  className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
                >
                  <option value="">-- {t.select_state} --</option>
                  {states.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>

              {selectedState && (
                <div>
                  <label className="text-xs text-gray-500 font-bold block mb-1">{t.select_district}</label>
                  <select 
                    value={selectedDistrict} 
                    onChange={(e) => {
                      setSelectedDistrict(e.target.value);
                      setSelectedMandi("");
                    }}
                    className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
                  >
                    <option value="">-- {t.select_district} --</option>
                    {districts.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
              )}

              {selectedDistrict && (
                <div>
                  <label className="text-xs text-gray-500 font-bold block mb-1">{t.select_mandi}</label>
                  <select 
                    value={selectedMandi} 
                    onChange={(e) => setSelectedMandi(e.target.value)}
                    className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
                  >
                    <option value="">-- {t.select_mandi} --</option>
                    {mandis.map(m => <option key={m.id} value={m.mandi_name}>{m.mandi_name}</option>)}
                  </select>
                </div>
              )}

              <div>
                <label className="text-xs text-gray-500 font-bold block mb-1">{t.select_commodity}</label>
                <select 
                  value={selectedCommodity} 
                  onChange={(e) => setSelectedCommodity(e.target.value)}
                  className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
                >
                  <option value="">-- {t.select_commodity} --</option>
                  {commodities.map(c => {
                    let localName = c.commodity_name;
                    try {
                      const jsonL = JSON.parse(c.local_name);
                      localName = jsonL[lang] || c.commodity_name;
                    } catch {}
                    return <option key={c.id} value={c.commodity_name}>{localName}</option>;
                  })}
                </select>
              </div>
            </div>

            {/* Results Grid */}
            {priceData && (
              <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-extrabold text-lg text-primary-700">{priceData.commodity}</h3>
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      <MapPin size={12} /> {priceData.mandi}
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="bg-green-100 text-green-800 text-[10px] font-bold px-2 py-1 rounded flex items-center gap-1">
                      <UserCheck size={10} /> {t.gov_verified}
                    </span>
                    {priceData.is_enam && (
                      <span className="bg-amber-100 text-amber-900 border border-amber-300 text-[9px] font-extrabold px-2 py-0.5 rounded-full flex items-center gap-1 shadow-xs">
                        {t.enam_badge || "⚡ e-NAM Unified Market"}
                      </span>
                    )}
                  </div>
                </div>

                {/* Phase 4: e-NAM Trade Depth, Arrivals & Variety */}
                {(priceData.arrivals_qty > 0 || priceData.variety) && (
                  <div className="bg-amber-50/80 border border-amber-200/80 rounded-lg p-2.5 flex flex-wrap items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-1.5 text-amber-950 font-semibold">
                      <span>📦</span>
                      <span>{t.arrivals || "Daily Arrivals"}: <strong className="font-extrabold text-amber-950">{priceData.arrivals_qty} Qtl</strong></span>
                    </div>
                    <div className="flex items-center gap-2">
                      {priceData.variety && (
                        <span className="bg-white/90 px-2 py-0.5 rounded border border-amber-300 text-[11px] font-bold text-gray-800">
                          {t.variety_grade || "Variety"}: {priceData.variety} ({priceData.grade || "Grade A"})
                        </span>
                      )}
                      <span className="bg-green-100 text-green-800 text-[10px] font-extrabold px-2 py-0.5 rounded uppercase">
                        {priceData.trade_type || "e-Auction"}
                      </span>
                    </div>
                  </div>
                )}

                {priceData.modal_price <= 0 ? (
                  <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl text-center text-amber-900 space-y-1 my-2">
                    <p className="font-bold text-sm">
                      ⚠️ {t.not_found_alert || "No active price records found for this crop in this mandi."}
                    </p>
                    <p className="text-xs text-amber-700">
                      {t.not_found_suggestion || "Would you like to check prices for other commodities or select a nearby market?"}
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="bg-gray-50 p-2 rounded-lg">
                        <p className="text-[10px] text-gray-500 font-bold uppercase">{t.min_price}</p>
                        <p className="font-bold text-sm text-gray-800">₹{priceData.min_price}</p>
                      </div>
                      <div className="bg-primary-50 p-2 rounded-lg border border-primary-100">
                        <p className="text-[10px] text-primary-700 font-bold uppercase">{t.modal_price}</p>
                        <p className="font-extrabold text-base text-primary-600">₹{priceData.modal_price}</p>
                      </div>
                      <div className="bg-gray-50 p-2 rounded-lg">
                        <p className="text-[10px] text-gray-500 font-bold uppercase">{t.max_price}</p>
                        <p className="font-bold text-sm text-gray-800">₹{priceData.max_price}</p>
                      </div>
                    </div>

                    <div className="text-xs text-gray-500 flex justify-between">
                      <span>{t.last_updated}: {priceData.date}</span>
                      <span>Source: {priceData.source}</span>
                    </div>
                  </>
                )}

                {/* 7-day trend chart */}
                {trendData.length > 0 && (
                  <div className="space-y-1">
                    <h4 className="text-xs font-bold text-gray-500 uppercase">{t.trend_header}</h4>
                    <div className="h-44 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={trendData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" tick={{fontSize: 10}} />
                          <YAxis domain={['auto', 'auto']} tick={{fontSize: 10}} />
                          <Tooltip />
                          <Line type="monotone" dataKey="modal_price" stroke="#16a34a" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {/* Phase 5: UPAg Macro Intelligence & Seasonal Outlook Card */}
                {upagOutlook && (
                  <div className="mt-4 bg-gradient-to-br from-blue-50/70 to-indigo-50/50 border border-blue-200/80 rounded-xl p-3.5 shadow-xs space-y-3">
                    <div className="flex justify-between items-center border-b border-blue-100 pb-2">
                      <div className="flex items-center gap-1.5">
                        <span className="text-base">📊</span>
                        <h4 className="text-xs font-extrabold text-blue-950 uppercase tracking-wide">
                          {t.upag_header || "UPAg Macro Intelligence & Seasonal Outlook"}
                        </h4>
                      </div>
                      <span className="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-900">
                        {upagOutlook.supply_outlook}
                      </span>
                    </div>

                    {/* Retail vs Wholesale Spread Bar */}
                    <div className="bg-white p-2.5 rounded-lg border border-blue-100/90 shadow-xs space-y-2">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-bold text-gray-700">{t.retail_spread_label || "Wholesale vs Consumer Retail Spread"}:</span>
                        <span className="font-extrabold text-indigo-700 bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded">
                          +{upagOutlook.retail_spread_pct}% Retail Margin
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-center pt-1">
                        <div className="bg-gray-50 p-2 rounded">
                          <p className="text-[10px] text-gray-500 font-bold uppercase">APMC Wholesale Rate</p>
                          <p className="font-bold text-sm text-gray-800">₹{upagOutlook.wholesale_price_avg}/kg</p>
                        </div>
                        <div className="bg-indigo-50/60 p-2 rounded border border-indigo-100">
                          <p className="text-[10px] text-indigo-700 font-bold uppercase">City Retail (DoCA)</p>
                          <p className="font-bold text-sm text-indigo-950">₹{upagOutlook.retail_price_avg}/kg</p>
                        </div>
                      </div>
                    </div>

                    {/* Climate & Actionable Strategic Recommendation */}
                    <div className="bg-amber-50/90 border-l-4 border-amber-500 p-2.5 rounded-r-lg text-xs space-y-1">
                      <p className="font-extrabold text-amber-950 flex items-center gap-1">
                        <span>💡</span> {t.advisory_label || "Strategic Farmer Advisory"}:
                      </p>
                      <p className="text-amber-900 font-medium text-[11px] leading-relaxed">
                        {upagOutlook.advisory_recommendation}
                      </p>
                      <div className="mt-1.5 text-[10px] text-gray-500 flex justify-between items-center border-t border-amber-200/60 pt-1">
                        <span>🌧️ CWWG Rainfall: {upagOutlook.rainfall_departure_pct}% (Reservoir: {upagOutlook.reservoir_storage_pct}%)</span>
                        <span className="italic">{upagOutlook.source}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: Marketplace */}
        {activeTab === "market" && (
          <div className="flex-1 overflow-y-auto space-y-6">
            
            {/* Buyers section */}
            <div className="space-y-3">
              <h2 className="text-lg font-extrabold text-gray-900 border-l-4 border-primary-600 pl-2">{t.buyers_header}</h2>
              
              {/* Simple filters */}
              <div className="flex gap-2">
                <input 
                  type="text" 
                  placeholder="Filter crop..."
                  value={marketCommodityFilter}
                  onChange={(e) => {
                    setMarketCommodityFilter(e.target.value);
                    loadMarketplace(e.target.value, marketDistrictFilter);
                  }}
                  className="w-1/2 text-xs border border-gray-200 rounded-lg p-2 bg-white"
                />
                <input 
                  type="text" 
                  placeholder="Filter district..."
                  value={marketDistrictFilter}
                  onChange={(e) => {
                    setMarketDistrictFilter(e.target.value);
                    loadMarketplace(marketCommodityFilter, e.target.value);
                  }}
                  className="w-1/2 text-xs border border-gray-200 rounded-lg p-2 bg-white"
                />
              </div>

              {/* Buyers list */}
              <div className="space-y-3">
                {buyers.map(b => (
                  <div key={b.id} className="bg-white p-3 rounded-xl border border-gray-100 shadow-sm flex flex-col gap-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-bold text-sm text-gray-900">{b.company}</h4>
                        <p className="text-[10px] text-gray-500 uppercase">Crop: {b.commodity} | District: {b.district}</p>
                      </div>
                      <span className="bg-primary-50 text-primary-700 text-[10px] px-2 py-0.5 rounded-full font-bold">
                        ⭐ {b.rating.toFixed(1)}
                      </span>
                    </div>
                    {b.gst_number && (
                      <p className="text-[9px] text-green-600 font-bold bg-green-50 px-2 py-0.5 rounded self-start">
                        ✓ GST VERIFIED: {b.gst_number}
                      </p>
                    )}
                    <div className="flex gap-2 mt-1">
                      <a 
                        href={`https://wa.me/${encodeURIComponent(b.phone.replace(/[^0-9]/g, ''))}?text=${encodeURIComponent(`Hello, I am interested in selling my ${b.commodity}`)}`}
                        target="_blank"
                        rel="noreferrer"
                        className="flex-1 bg-green-500 hover:bg-green-600 text-white font-bold text-xs py-2 rounded-lg flex items-center justify-center gap-1"
                      >
                        <MessageCircle size={14} /> {t.whats_app_chat}
                      </a>
                      <a 
                        href={`tel:${encodeURIComponent(b.phone.replace(/[^0-9+]/g, ''))}`}
                        className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold text-xs p-2 rounded-lg flex items-center justify-center"
                      >
                        <PhoneCall size={14} />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Dealers section */}
            <div className="space-y-3">
              <h2 className="text-lg font-extrabold text-gray-900 border-l-4 border-primary-600 pl-2">{t.dealers_header}</h2>
              <div className="space-y-3">
                {dealers.map(d => (
                  <div key={d.id} className="bg-white p-3 rounded-xl border border-gray-100 shadow-sm flex flex-col gap-1">
                    <h4 className="font-bold text-sm text-gray-900">{d.shop_name}</h4>
                    <p className="text-[10px] text-gray-500">📍 Location: {d.location}</p>
                    
                    <div className="flex gap-1 mt-2">
                      <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${d.fertilizer ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-400"}`}>
                        Fertilizer
                      </span>
                      <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${d.seed ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-400"}`}>
                        Seeds
                      </span>
                      <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${d.pesticide ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-400"}`}>
                        Pesticides
                      </span>
                    </div>
                    
                    <button 
                      onClick={() => openReservationModal(d)}
                      className="mt-3 w-full bg-primary-100 text-primary-800 text-xs font-bold py-2 rounded-lg border border-primary-200 hover:bg-primary-200 transition-colors"
                    >
                      Check Stock & Reserve
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: WhatsApp Simulator */}
        {activeTab === "whatsapp" && (
          <div className="flex flex-col flex-1 h-full min-h-0 bg-[#efeae2] rounded-2xl border border-gray-200 shadow-inner overflow-hidden relative">
            
            {/* Direct WhatsApp Connect Card & QR Code */}
            <div className="bg-white p-3 border-b border-gray-200 flex flex-row items-center gap-3 shadow-sm">
              <img 
                src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://wa.me/919876543210?text=Hi%20KrishiMitra" 
                alt="WhatsApp QR Code" 
                className="w-16 h-16 border rounded-lg p-1 bg-white shadow-sm shrink-0"
              />
              <div className="flex-1 min-w-0">
                <div className="inline-block bg-green-100 text-green-800 text-[9px] font-bold px-2 py-0.5 rounded-full mb-0.5">
                  📱 WhatsApp Bot (+91 98765 43210)
                </div>
                <h4 className="font-bold text-xs text-gray-800 truncate">Scan QR to Chat on Mobile</h4>
                <p className="text-[10px] text-gray-500 line-clamp-1">
                  Scan code with phone camera or tap button to launch WhatsApp directly.
                </p>
                <a 
                  href="https://wa.me/919876543210?text=Hi%20KrishiMitra" 
                  target="_blank" 
                  rel="noreferrer" 
                  className="inline-flex items-center gap-1 mt-1 bg-[#25D366] hover:bg-[#1ebd59] text-white font-bold text-[10px] px-2.5 py-1 rounded shadow-sm transition-all"
                >
                  <span>Open WhatsApp</span> ↗
                </a>
              </div>
            </div>

            {/* WhatsApp Simulator Header */}
            <div className="bg-[#075e54] text-white p-2.5 flex items-center gap-2">
              <div className="w-8 h-8 bg-green-200 rounded-full flex items-center justify-center font-bold text-green-800 text-xs">
                KM
              </div>
              <div>
                <h3 className="font-bold text-xs">KrishiMitra Chatbot</h3>
                <p className="text-[9px] text-green-100">Online | Official Business Account</p>
              </div>
            </div>

            {/* Message window */}
            <div className="flex-1 p-3 overflow-y-auto space-y-3 flex flex-col">
              {waLog.map((chat, idx) => (
                <div 
                  key={idx}
                  className={`flex flex-col max-w-[85%] ${
                    chat.sender === "user" ? "self-end items-end" : "self-start items-start"
                  }`}
                >
                  <div className={`p-3 rounded-lg text-xs shadow-sm relative break-words [overflow-wrap:anywhere] ${
                    chat.sender === "user" 
                      ? "bg-[#d9fdd3] text-gray-800 rounded-tr-none" 
                      : "bg-white text-gray-800 rounded-tl-none"
                  }`}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="whitespace-normal flex-1 text-xs break-words [overflow-wrap:anywhere]">
                        {chat.sender === "user" ? renderUserMessage(chat.text) : renderFormattedMessage(chat.text, false)}
                      </div>
                      {chat.sender === "bot" && (
                        <button
                          onClick={() => speakText(chat.text)}
                          title="Listen to audio"
                          className="p-1 text-primary-600 hover:text-primary-800 hover:bg-green-50 rounded-full transition-colors shrink-0"
                        >
                          <Volume2 size={13} />
                        </button>
                      )}
                    </div>
                    <span className="text-[8px] text-gray-400 block text-right mt-1">{chat.time}</span>
                  </div>
                </div>
              ))}
              <div ref={waEndRef} />
            </div>

            {/* Input bar */}
            <div className="bg-gray-100 p-2 flex gap-2 border-t border-gray-200">
              <input 
                type="text"
                value={waText}
                onChange={(e) => setWaText(e.target.value)}
                placeholder="Type agricultural query..."
                className="flex-1 bg-white rounded-full px-4 py-2 text-xs focus:outline-none"
                onKeyDown={(e) => e.key === "Enter" && handleWaSend()}
                disabled={isWaListening}
              />
              <button 
                onClick={handleWaVoice}
                className={`p-2 rounded-full shadow transition-all ${
                  isWaListening 
                    ? "bg-red-500 text-white animate-pulse" 
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                {isWaListening ? <MicOff size={14} /> : <Mic size={14} />}
              </button>
              <button 
                onClick={handleWaSend}
                className="bg-[#075e54] hover:bg-[#128c7e] text-white p-2 rounded-full shadow"
                disabled={isWaListening}
              >
                <Send size={14} />
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer Navigation Bar */}
      <footer className="bg-white border-t border-gray-200 grid grid-cols-4 text-center z-10 py-1">
        <button 
          onClick={() => setActiveTab("assistant")}
          className={`flex flex-col items-center py-2 text-xs font-bold gap-1 ${
            activeTab === "assistant" ? "text-primary-600 border-t-2 border-primary-600" : "text-gray-500"
          }`}
        >
          <Mic size={18} />
          {t.tab_assistant}
        </button>
        <button 
          onClick={() => setActiveTab("mandi")}
          className={`flex flex-col items-center py-2 text-xs font-bold gap-1 ${
            activeTab === "mandi" ? "text-primary-600 border-t-2 border-primary-600" : "text-gray-500"
          }`}
        >
          <TrendingUp size={18} />
          {t.tab_mandi}
        </button>
        <button 
          onClick={() => setActiveTab("market")}
          className={`flex flex-col items-center py-2 text-xs font-bold gap-1 ${
            activeTab === "market" ? "text-primary-600 border-t-2 border-primary-600" : "text-gray-500"
          }`}
        >
          <Store size={18} />
          {t.tab_market}
        </button>
        <button 
          onClick={() => setActiveTab("whatsapp")}
          className={`flex flex-col items-center py-2 text-xs font-bold gap-1 ${
            activeTab === "whatsapp" ? "text-primary-600 border-t-2 border-primary-600" : "text-gray-500"
          }`}
        >
          <MessageCircle size={18} />
          {t.tab_whatsapp}
        </button>
      </footer>
      <div className="bg-gray-100 text-[9px] text-gray-400 text-center py-1 border-t border-gray-200">
        © 2026 Crestsubarn Company. All rights reserved.
      </div>

      {/* Reservation Modal Overlay */}
      {selectedDealerForReservation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto flex flex-col">
            
            <div className="p-4 border-b border-gray-100 flex justify-between items-center sticky top-0 bg-white">
              <h3 className="font-bold text-gray-900">Reserve at {selectedDealerForReservation.shop_name}</h3>
              <button 
                onClick={() => setSelectedDealerForReservation(null)}
                className="text-gray-400 hover:text-gray-800"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-4 flex-1">
              {reservationSuccess ? (
                <div className="bg-green-50 text-green-800 p-6 rounded-lg text-center border border-green-200">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle size={32} className="text-green-600" />
                  </div>
                  <h4 className="font-bold text-lg mb-2">Reservation Confirmed!</h4>
                  <p className="text-sm mb-4">{reservationSuccess.message}</p>
                  <div className="bg-white border-2 border-dashed border-green-300 p-4 rounded-lg">
                    <p className="text-xs text-green-600 font-bold uppercase tracking-wider mb-1">Your Pickup PIN</p>
                    <p className="text-4xl font-black text-green-700 tracking-widest">{reservationSuccess.pin_code}</p>
                  </div>
                  <button 
                    onClick={() => setSelectedDealerForReservation(null)}
                    className="mt-6 w-full bg-green-600 text-white font-bold py-3 rounded-lg hover:bg-green-700"
                  >
                    Done
                  </button>
                </div>
              ) : (
                <>
                  <div className="mb-4">
                    <label className="block text-xs font-bold text-gray-700 mb-1">Your Phone Number</label>
                    <input 
                      type="tel"
                      value={reservationPhone}
                      onChange={e => setReservationPhone(e.target.value)}
                      placeholder="e.g. 9876543210"
                      className="w-full border border-gray-300 rounded-lg p-2 text-sm text-gray-900 focus:outline-none focus:border-primary-500"
                    />
                    <p className="text-[10px] text-gray-500 mt-1">We need this to reserve your stock securely.</p>
                  </div>

                  <h4 className="font-bold text-sm text-gray-800 border-b pb-2 mb-3">Available Inventory</h4>
                  
                  {dealerInventory.length === 0 ? (
                    <p className="text-sm text-gray-500 text-center py-4">No inventory items found.</p>
                  ) : (
                    <div className="space-y-4">
                      {dealerInventory.map(item => (
                        <div key={item.id} className="border border-gray-100 p-3 rounded-lg flex flex-col gap-2 shadow-sm">
                          <div className="flex justify-between items-start">
                            <div>
                              <h5 className="font-bold text-sm text-gray-900">{item.item_name}</h5>
                              <span className="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-bold">{item.category}</span>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-primary-700">₹{item.price}</p>
                              <p className="text-[10px] text-gray-500">per {item.unit.replace(/s$/, "")}</p>
                            </div>
                          </div>
                          
                          <div className="bg-orange-50 border border-orange-100 rounded px-2 py-1 flex items-center justify-between mt-1">
                            <span className="text-[11px] text-orange-800 font-bold">In Stock: {item.stock_quantity} {item.unit}</span>
                          </div>

                          {item.stock_quantity > 0 ? (
                            <div className="flex items-center gap-2 mt-2">
                              <input 
                                type="number" 
                                min="1" 
                                max={item.stock_quantity}
                                value={item.reserveQty}
                                onChange={e => {
                                  const val = parseInt(e.target.value) || 1;
                                  setDealerInventory(prev => prev.map(inv => 
                                    inv.id === item.id ? { ...inv, reserveQty: val > item.stock_quantity ? item.stock_quantity : val } : inv
                                  ));
                                }}
                                className="w-16 border border-gray-300 rounded p-1.5 text-sm text-center focus:outline-none focus:border-primary-500"
                              />
                              <span className="text-xs text-gray-500">{item.unit}</span>
                              <button 
                                onClick={() => handleReserve(item.id, item.reserveQty)}
                                className="ml-auto bg-primary-600 hover:bg-primary-700 text-white text-xs font-bold py-2 px-4 rounded transition-colors"
                              >
                                Reserve
                              </button>
                            </div>
                          ) : (
                            <div className="mt-2 text-center py-2 bg-gray-50 text-gray-500 text-xs font-bold rounded">
                              Out of Stock
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Admin Bulk Rate Upload Modal Overlay */}
      {showAdminUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto flex flex-col">
            
            <div className="p-4 border-b border-gray-100 flex justify-between items-center sticky top-0 bg-white">
              <div className="flex items-center gap-2">
                <span className="text-lg">📤</span>
                <h3 className="font-bold text-gray-900">Admin: Bulk Upload Local Mandi Rates</h3>
              </div>
              <button 
                onClick={() => setShowAdminUploadModal(false)}
                className="text-gray-400 hover:text-gray-800"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <p className="text-xs text-gray-600">
                Upload or paste local mandi rates in CSV or Excel format. Missing mandis or commodities will be auto-created.
              </p>

              {/* Sample CSV Download Helper */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-900 space-y-2">
                <div className="flex justify-between items-center">
                  <p className="font-bold">💡 Expected CSV Format:</p>
                  <a 
                    href="/sample_mandi_rates.csv" 
                    download="sample_mandi_rates.csv"
                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-[11px] px-2.5 py-1 rounded flex items-center gap-1 shadow-sm transition cursor-pointer"
                  >
                    📥 Download Sample CSV
                  </a>
                </div>
                <code className="block bg-white p-2 rounded border border-blue-200 text-[11px] font-mono text-gray-800 overflow-x-auto">
                  state,district,mandi_name,commodity,date,min_price,modal_price,max_price<br/>
                  Karnataka,Shivamogga,Shimoga APMC,Maize,2026-09-05,2200,2350,2500<br/>
                  Maharashtra,Nashik,Lasalgaon APMC,Onion,2026-09-05,1800,2100,2400
                </code>
              </div>

              {/* Admin Security PIN Field */}
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">🔑 Admin Security PIN / Password</label>
                <input 
                  type="password"
                  value={adminPin}
                  onChange={(e) => setAdminPin(e.target.value)}
                  placeholder="Enter Admin Security PIN (Default: 2026)"
                  className="w-full border border-gray-300 rounded-lg p-2 text-xs font-bold text-gray-900 focus:outline-none focus:border-primary-500"
                />
              </div>

              {/* File Upload input */}
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Option 1: Select CSV File</label>
                <input 
                  type="file" 
                  accept=".csv,.txt"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      const reader = new FileReader();
                      reader.onload = (evt) => {
                        const txt = evt.target?.result as string;
                        setCsvInput(txt);
                      };
                      reader.readAsText(file);
                    }
                  }}
                  className="w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 cursor-pointer"
                />
              </div>

              {/* CSV Textarea input */}
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Option 2: Or Paste CSV / Data Text Directly</label>
                <textarea 
                  rows={5}
                  value={csvInput}
                  onChange={(e) => setCsvInput(e.target.value)}
                  placeholder="state,district,mandi_name,commodity,date,min_price,modal_price,max_price&#10;Karnataka,Shivamogga,Shimoga APMC,Maize,2026-09-05,2200,2350,2500"
                  className="w-full border border-gray-300 rounded-lg p-2 text-xs font-mono text-gray-900 focus:outline-none focus:border-primary-500"
                />
              </div>

              {/* Upload Feedback */}
              {uploadStatus && (
                <div className={`p-3 rounded-lg text-xs font-semibold ${uploadStatus.success ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
                  {uploadStatus.success ? (
                    <div>
                      ✅ Successfully processed {uploadStatus.processed} records!
                      {uploadStatus.errors && uploadStatus.errors.length > 0 && (
                        <div className="mt-1 text-[11px] text-amber-700">
                          Warnings/Errors: {uploadStatus.errors.join(", ")}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div>❌ Error: {uploadStatus.detail || "Failed to upload rates"}</div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2 justify-end pt-2">
                <button 
                  onClick={() => setShowAdminUploadModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 text-xs font-bold rounded-lg hover:bg-gray-50"
                >
                  Close
                </button>
                <button 
                  onClick={() => handleAdminUpload()}
                  disabled={isUploading}
                  className="px-5 py-2 bg-primary-600 hover:bg-primary-700 text-white text-xs font-bold rounded-lg disabled:opacity-50 flex items-center gap-1 cursor-pointer"
                >
                  {isUploading ? "Uploading..." : "Upload & Save Rates"}
                </button>
              </div>

            </div>
          </div>
        </div>
      )}
    </div>
  );
}
