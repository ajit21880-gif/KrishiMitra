"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
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
    greeting: "Hello! How can I help you with your agriculture queries today?",
    enam_badge: "⚡ e-NAM Unified Market",
    arrivals: "Daily Arrivals",
    qtl: "Qtl",
    variety_grade: "Variety",
    source_label: "Source",
    upag_header: "UPAg Macro Intelligence & Seasonal Outlook",
    retail_spread_label: "Wholesale vs Consumer Retail Spread",
    retail_margin: "Retail Margin",
    apmc_wholesale_rate: "APMC Wholesale Rate",
    city_retail_rate: "City Retail (DoCA)",
    advisory_label: "Strategic Farmer Advisory",
    cwwg_rainfall: "CWWG Rainfall",
    reservoir: "Reservoir",
    unit_kg: "kg",
    cached_rates: "Cached Rates",
    live_sync: "Synced Live"
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
    greeting: "नमस्ते! मैं आपकी कृषि संबंधी समस्याओं में कैसे मदद कर सकता हूँ?",
    enam_badge: "⚡ ई-नाम एकीकृत बाजार",
    arrivals: "दैनिक आवक",
    qtl: "क्विंटल",
    variety_grade: "किस्म",
    source_label: "स्रोत",
    upag_header: "यूपीएजी मैक्रो इंटेलिजेंस और मौसमी परिदृश्य",
    retail_spread_label: "थोक बनाम उपभोक्ता खुदरा मूल्य अंतर",
    retail_margin: "खुदरा मार्जिन",
    apmc_wholesale_rate: "एपीएमसी थोक दर",
    city_retail_rate: "शहर खुदरा दर (DoCA)",
    advisory_label: "महत्वपूर्ण किसान सलाह",
    cwwg_rainfall: "सीडबल्यूडबल्यूजी वर्षा",
    reservoir: "जलाशय",
    unit_kg: "किग्रा",
    cached_rates: "कैश भाव",
    live_sync: "लाइव सिंक"
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
    greeting: "ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಕೃಷಿ ಸಂಬಂಧಿತ ಪ್ರಶ್ನೆಗಳಿಗೆ ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
    enam_badge: "⚡ ಇ-ನ್ಯಾಮ್ ಏಕೀಕೃತ ಮಾರುಕಟ್ಟೆ",
    arrivals: "ದೈನಂದಿನ ಆವಕ",
    qtl: "ಕ್ವಿಂಟಾಲ್",
    variety_grade: "ತಳಿ",
    source_label: "ಮೂಲ",
    upag_header: "ಯುಪಿಎಜಿ ಮ್ಯಾಕ್ರೋ ಇಂಟೆಲಿಜೆನ್ಸ್ ಮತ್ತು ಕಾಲೋಚಿತ ಮುನ್ನೋಟ",
    retail_spread_label: "ಸಗಟು ಮತ್ತು ಚಿಲ್ಲರೆ ದರದ ವ್ಯತ್ಯಾಸ",
    retail_margin: "ಚಿಲ್ಲರೆ ಮಾರ್ಜಿನ್",
    apmc_wholesale_rate: "ಎಪಿಎಂಸಿ ಸಗಟು ದರ",
    city_retail_rate: "ನಗರ ಚಿಲ್ಲರೆ ದರ (DoCA)",
    advisory_label: "ರೈತರಿಗೆ ಕಾರ್ಯತಂತ್ರದ ಸಲಹೆ",
    cwwg_rainfall: "ಸಿಡಬ್ಲ್ಯೂಡಬ್ಲ್ಯೂಜಿ ಮಳೆ",
    reservoir: "ಜಲಾಶಯ",
    unit_kg: "ಕೆಜಿ",
    cached_rates: "ಕ್ಯಾಶ್ ದರ",
    live_sync: "ಲೈವ್ ಸಿಂಕ್"
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
    greeting: "નમસ્તે! હું તમારા ખેતી સંબંધિત પ્રશ્નોમાં કેવી રીતે મદદ કરી શકું?",
    enam_badge: "⚡ ઈ-નામ સંકલિત બજાર",
    arrivals: "દૈનિક આવક",
    qtl: "ક્વિન્ટલ",
    variety_grade: "જાત",
    source_label: "સ્ત્રોત",
    upag_header: "યુપીએજી મેક્રો ઇન્ટેલિજન્સ અને મોસમી આઉટલુક",
    retail_spread_label: "જથ્થાબંધ વિરુદ્ધ છૂટક ભાવ તફાવત",
    retail_margin: "છૂટક માર્જિન",
    apmc_wholesale_rate: "એપીએમસી જથ્થાબંધ ભાવ",
    city_retail_rate: "શહેર છૂટક ભાવ (DoCA)",
    advisory_label: "ખેડૂત માટે વ્યૂહાત્મક સલાહ",
    cwwg_rainfall: "સીડબલ્યુડબલ્યુજી વરસાદ",
    reservoir: "જળાશય",
    unit_kg: "કિલો",
    cached_rates: "કેશ્ડ ભાવ",
    live_sync: "લાઈવ સિંક"
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
    greeting: "नमस्कार! मी आज आपल्या कृषी विषयक प्रश्नांमध्ये कशी मदत करू शकतो?",
    enam_badge: "⚡ ई-नाम एकीकृत बाजार",
    arrivals: "दैनंदिन आवक",
    qtl: "क्विंटल",
    variety_grade: "प्रकार",
    source_label: "स्रोत",
    upag_header: "UPAg मॅक्रो इंटेलिजन्स आणि हंगामी दृष्टिकोन",
    retail_spread_label: "घाऊक वि ग्राहक किरकोळ फरक",
    retail_margin: "किरकोळ मार्जिन",
    apmc_wholesale_rate: "APMC घाऊक दर",
    city_retail_rate: "शहरातील किरकोळ दर (DoCA)",
    advisory_label: "शेतकऱ्यांसाठी धोरणात्मक सल्ला",
    cwwg_rainfall: "CWWG पाऊस",
    reservoir: "जलाशय",
    unit_kg: "किग्रॅ",
    cached_rates: "कॅश केलेले भाव",
    live_sync: "थेट सिंक"
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
    greeting: "வணக்கம்! உங்கள் விவசாயம் சார்ந்த கேள்விகளுக்கு நான் எவ்வாறு உதவ முடியும்?",
    enam_badge: "⚡ இ-நாம் ஒருங்கிணைந்த சந்தை",
    arrivals: "தினசரி வரத்து",
    qtl: "குவிண்டால்",
    variety_grade: "ரகம்",
    source_label: "ஆதாரம்",
    upag_header: "UPAg மேக்ரோ நுண்ணறிவு மற்றும் பருவகாலக் கண்ணோட்டம்",
    retail_spread_label: "மொத்த மற்றும் சில்லறை விலை வேறுபாடு",
    retail_margin: "சில்லறை விளிம்பு",
    apmc_wholesale_rate: "APMC மொத்த விலை",
    city_retail_rate: "நகர சில்லறை விலை (DoCA)",
    advisory_label: "விவசாயிகளுக்கான உத்திசார் ஆலோசனை",
    cwwg_rainfall: "CWWG மழைப்பொழிவு",
    reservoir: "நீர்த்தேக்கம்",
    unit_kg: "கிலோ",
    cached_rates: "சேமிக்கப்பட்ட விலைகள்",
    live_sync: "நேரலை ஒத்திசைவு"
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
    greeting: "నమస్కారం! మీ వ్యవసాయ సంబంధిత సందేహాలకు నేను ఎలా సహాయపడగలను?",
    enam_badge: "⚡ ఈ-నామ్ ఏకీకృత మార్కెట్",
    arrivals: "రోజువారీ రాకలు",
    qtl: "క్వింటాల్",
    variety_grade: "రకం",
    source_label: "మూలం",
    upag_header: "UPAg స్థూల నిఘా & కాలానుగుణ ఔట్‌లుక్",
    retail_spread_label: "టోకు వర్సెస్ వినియోగదారు రిటైల్ వ్యత్యాసం",
    retail_margin: "రిటైల్ మార్జిన్",
    apmc_wholesale_rate: "APMC టోకు ధర",
    city_retail_rate: "నగర రిటైల్ ధర (DoCA)",
    advisory_label: "రైతులకు వ్యూహాత్మక సలహా",
    cwwg_rainfall: "CWWG వర్షపాతం",
    reservoir: "జలాశయం",
    unit_kg: "కిలో",
    cached_rates: "కాష్ ధరలు",
    live_sync: "ప్రత్యక్ష సమకాలీకరణ"
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
    greeting: "നമസ്കാരം! നിങ്ങളുടെ കൃഷി സംശയങ്ങൾക്ക് ഞാൻ എങ്ങനെ സഹായിക്കണം?",
    enam_badge: "⚡ ഇ-നാം ഏകീകൃത മാർക്കറ്റ്",
    arrivals: "പ്രതിദിന വരവ്",
    qtl: "ക്വിന്റൽ",
    variety_grade: "ഇനം",
    source_label: "ഉറവിടം",
    upag_header: "UPAg മാക്രോ ഇന്റലിജൻസും സീസണൽ കാഴ്ചപ്പാടും",
    retail_spread_label: "മൊത്തവ്യാപാരവും ചില്ലറവ്യാപാരവും തമ്മിലുള്ള അന്തരം",
    retail_margin: "റീട്ടെയിൽ മാർജിൻ",
    apmc_wholesale_rate: "APMC മൊത്തവില",
    city_retail_rate: "നഗര ചില്ലറവില (DoCA)",
    advisory_label: "കർഷകർക്കുള്ള തന്ത്രപരമായ നിർദ്ദേശം",
    cwwg_rainfall: "CWWG മഴ",
    reservoir: "ജലസംഭരണി",
    unit_kg: "കിലോ",
    cached_rates: "കാഷെ ചെയ്ത നിരക്കുകൾ",
    live_sync: "തത്സമയ സമന്വയം"
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
    greeting: "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਅੱਜ ਤੁਹਾਡੀ ਖੇਤੀ ਸਬੰਧੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?",
    enam_badge: "⚡ ਈ-ਨਾਮ ਏਕੀਕ੍ਰਿਤ ਮੰਡੀ",
    arrivals: "ਰੋਜ਼ਾਨਾ ਆਮਦ",
    qtl: "ਕੁਇੰਟਲ",
    variety_grade: "ਕਿਸਮ",
    source_label: "ਸਰੋਤ",
    upag_header: "UPAg ਮੈਕਰੋ ਇੰਟੈਲੀਜੈਂਸ ਅਤੇ ਮੌਸਮੀ ਦ੍ਰਿਸ਼ਟੀਕੋਣ",
    retail_spread_label: "ਥੋਕ ਬਨਾਮ ਪ੍ਰਚੂਨ ਮੁੱਲ ਅੰਤਰ",
    retail_margin: "ਪ੍ਰਚੂਨ ਮਾਰਜਿਨ",
    apmc_wholesale_rate: "APMC ਥੋਕ ਰੇਟ",
    city_retail_rate: "ਸ਼ਹਿਰ ਪ੍ਰਚੂਨ ਰੇਟ (DoCA)",
    advisory_label: "ਕਿਸਾਨਾਂ ਲਈ ਰਣਨੀਤਕ ਸਲਾਹ",
    cwwg_rainfall: "CWWG ਮੀਂਹ",
    reservoir: "ਜਲ ਭੰਡਾਰ",
    unit_kg: "ਕਿਲੋ",
    cached_rates: "ਕੈਸ਼ਡ ਰੇਟ",
    live_sync: "ਲਾਈਵ ਸਿੰਕ"
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
    greeting: "নমস্কার! আজ আপনার কৃষি সংক্রান্ত বিষয়ে আমি কীভাবে সাহায্য করতে পারি?",
    enam_badge: "⚡ ই-নাম সমন্বিত বাজার",
    arrivals: "দৈনিক আমদানি",
    qtl: "কুইন্টাল",
    variety_grade: "জাত",
    source_label: "উৎস",
    upag_header: "UPAg ম্যাক্রো ইন্টেলিজেন্স ও মৌসুমী দৃষ্টিভঙ্গি",
    retail_spread_label: "পাইকারি বনাম খুচরা মূল্য ব্যবধান",
    retail_margin: "খুচরা মার্জিন",
    apmc_wholesale_rate: "এপিএমসি পাইকারি দর",
    city_retail_rate: "শহরের খুচরা দর (DoCA)",
    advisory_label: "কৃষকদের কৌশলগত পরামর্শ",
    cwwg_rainfall: "সিডাব্লুডাব্লুজি বৃষ্টিপাত",
    reservoir: "জলাধার",
    unit_kg: "কেজি",
    cached_rates: "ক্যাশে করা দর",
    live_sync: "লাইভ সিঙ্ক"
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
    greeting: "ନମସ୍କାର! ଆଜି ଆପଣଙ୍କ କୃଷି ସମ୍ବନ୍ଧୀୟ ପ୍ରଶ୍ନରେ ମୁଁ କିପରି ସାହାଯ୍ୟ କରିପାରିବି?",
    enam_badge: "⚡ ଇ-ନାମ୍ ସମନ୍ୱିତ ବଜାର",
    arrivals: "ଦୈନିକ ଆଗମନ",
    qtl: "କ୍ୱିଣ୍ଟାଲ",
    variety_grade: "କିସମ",
    source_label: "ଉତ୍ସ",
    upag_header: "UPAg ବୃହତ ବଜାର ସୂଚନା ଏବଂ ଋତୁକାଳୀନ ଦୃଷ୍ଟିକୋଣ",
    retail_spread_label: "ପାଇକାରୀ ବନାମ ଖୁଚୁରା ମୂଲ୍ୟ ବ୍ୟବଧାନ",
    retail_margin: "ଖୁଚୁରା ମାର୍ଜିନ",
    apmc_wholesale_rate: "APMC ପାଇକାରୀ ଦର",
    city_retail_rate: "ସହର ଖୁଚୁରା ଦର (DoCA)",
    advisory_label: "କୃଷକଙ୍କ ପାଇଁ ରଣନୈତିକ ପରାମର୍ଶ",
    cwwg_rainfall: "CWWG ବର୍ଷା",
    reservoir: "ଜଳଭଣ୍ଡାର",
    unit_kg: "କିଗ୍ରା",
    cached_rates: "କ୍ୟାଚ୍ ଦର",
    live_sync: "ଲାଇଭ୍ ସିଙ୍କ"
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
    greeting: "নমস্কাৰ! আজি আপোনাৰ কৃষি সম্বন্ধীয় সমস্যাত মই কেনেকৈ সহায় কৰিব পাৰোঁ?",
    enam_badge: "⚡ ই-নাম একত্ৰিত বজাৰ",
    arrivals: "দৈনিক আগমন",
    qtl: "কুইণ্টল",
    variety_grade: "জাত",
    source_label: "উৎস",
    upag_header: "UPAg মেক্ৰ' ইনটেলিজেন্স আৰু ঋতুকালীন দৃষ্টিকোণ",
    retail_spread_label: "পাইকাৰী বনাম খুচুৰা মূল্যৰ ব্যৱধান",
    retail_margin: "খুচুৰা মাৰ্জিন",
    apmc_wholesale_rate: "APMC পাইকাৰী দৰ",
    city_retail_rate: "চহৰৰ খুচুৰা দৰ (DoCA)",
    advisory_label: "কৃষকৰ বাবে কৌশলগত পৰামৰ্শ",
    cwwg_rainfall: "CWWG বৰষুণ",
    reservoir: "জলাশয়",
    unit_kg: "কেজি",
    cached_rates: "কেশ্ব কৰা দৰ",
    live_sync: "লাইভ চিঙ্ক"
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
    greeting: "سلام! بٕہ کِتھ پٲٹھۍ ہٮ۪کاو تُہنٛز کٔشیرۍ کھیتی باڑی سوالَن مَنٛز مَدَتھ کٔرِتھ؟",
    enam_badge: "⚡ ای-نام یکجا منڈی",
    arrivals: "روزانہ آمد",
    qtl: "کوئنٹل",
    variety_grade: "قسم",
    source_label: "ذرائع",
    upag_header: "یو پی اے جی میکرو انٹیلی جنس اور موسمی جائزہ",
    retail_spread_label: "تھوک بمقابلہ پرچون فرق",
    retail_margin: "پرچون مارجن",
    apmc_wholesale_rate: "اے پی ایم سی تھوک ریٹ",
    city_retail_rate: "شہری پرچون ریٹ (DoCA)",
    advisory_label: "کسانوں کیلئے حکمت عملی مشورہ",
    cwwg_rainfall: "بارش",
    reservoir: "ڈیم/ذخیرہ",
    unit_kg: "کلو",
    cached_rates: "محفوظ شدہ ریٹ",
    live_sync: "براہ راست مطابقت"
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


// Pre-bundled static location translations for immediate 0ms rendering
const STATIC_LOCATIONS: {
  states: Record<string, Record<string, string>>;
  districts: Record<string, Record<string, string>>;
} = {"states": {"Odisha": {"en": "Odisha", "hi": "ओडिशा", "kn": "ಒಡಿಶಾ", "or": "ଓଡ଼ିଶା", "mr": "ओडिशा", "ta": "ஒடிசா", "te": "ఒడిశా", "ml": "ഒഡീഷ", "gu": "ઓડિશા", "pa": "ਉੜੀਸਾ", "bn": "ওড়িশা", "as": "ওড়িশা", "ks": "اوٚڈِشا"}, "Karnataka": {"en": "Karnataka", "hi": "कर्नाटक", "kn": "ಕರ್ನಾಟಕ", "or": "କର୍ଣ୍ଣାଟକ", "mr": "कर्नाटक", "ta": "கர்நாடகா", "te": "కర్ణాటక", "ml": "കർണാടക", "gu": "કર્ણાટક", "pa": "ਕਰਨਾਟਕ", "bn": "কর্ণাটক", "as": "কৰ্ণাটক", "ks": "کَرناٹَک"}, "Maharashtra": {"en": "Maharashtra", "hi": "महाराष्ट्र", "kn": "ಮಹಾರಾಷ್ಟ್ರ", "or": "ମହାରାଷ୍ଟ୍ର", "mr": "महाराष्ट्र", "ta": "மகாராஷ்டிரா", "te": "మహారాష్ట్ర", "ml": "മഹാരാഷ്ട്ര", "gu": "મહારાષ્ટ્ર", "pa": "ਮਹਾਂਰਾਸ਼ਟਰ", "bn": "মহারাষ্ট্র", "as": "মহাৰাষ্ট্ৰ", "ks": "مَہَاراشٹرا"}, "Gujarat": {"en": "Gujarat", "hi": "गुजरात", "kn": "ಗುಜರಾತ್", "or": "ଗୁଜରାଟ", "mr": "गुजरात", "ta": "குஜராத்", "te": "గుజరాత్", "ml": "ഗുജറാത്ത്", "gu": "ગુજરાત", "pa": "ਗੁਜਰਾਤ", "bn": "গুজরাত", "as": "গুজৰাট", "ks": "گُجرات"}, "Madhya Pradesh": {"en": "Madhya Pradesh", "hi": "मध्य प्रदेश", "kn": "ಮಧ್ಯಪ್ರದೇಶ", "or": "ମଧ୍ୟପ୍ରଦେଶ", "mr": "मध्य प्रदेश", "ta": "மத்தியப் பிரதேசம்", "te": "మధ్యప్రదేశ్", "ml": "മധ്യപ്രദേശ്", "gu": "મધ્ય પ્રદેશ", "pa": "ਮੱਧ ਪ੍ਰਦੇਸ਼", "bn": "মধ্যপ্রদেশ", "as": "মধ্যপ্ৰদেশ", "ks": "مَدھیَہ پَرٛدیش"}, "Tamil Nadu": {"en": "Tamil Nadu", "hi": "तमिलनाडु", "kn": "ತಮಿಳುನಾಡು", "or": "ତାମିଲନାଡୁ", "mr": "तमिळनाडू", "ta": "தமிழ்நாடு", "te": "తమిళనాడు", "ml": "തമിഴ്നാട്", "gu": "તમિલનાડુ", "pa": "ਤਾਮਿਲਨਾਡੂ", "bn": "তামিলনাড়ু", "as": "তামিলনাডু", "ks": "تَمِل ناڈوٗ"}, "Andhra Pradesh": {"en": "Andhra Pradesh", "hi": "आंध्र प्रदेश", "kn": "ಆಂಧ್ರಪ್ರದೇಶ", "or": "ଆନ୍ଧ୍ରପ୍ରଦେଶ", "mr": "आंध्र प्रदेश", "ta": "ஆந்திரப் பிரதேசம்", "te": "ఆంధ్రప్రదేశ్", "ml": "ആന്ധ്രാപ്രദേശ്", "gu": "આંધ્ર પ્રદેશ", "pa": "ਆਂਧਰਾ ਪ੍ਰਦੇਸ਼", "bn": "অন্ধ্রপ্রদেশ", "as": "অন্ধ্ৰপ্ৰদেশ", "ks": "آندھرا پَرٛدیش"}, "Telangana": {"en": "Telangana", "hi": "तेलंगाना", "kn": "ತೆಲಂಗಾಣ", "or": "ତେଲେଙ୍ଗାନା", "mr": "तेलंगणा", "ta": "தெலங்கானா", "te": "తెలంగాణ", "ml": "തെലങ്കാന", "gu": "તેલંગાણા", "pa": "ਤੇਲੰਗਾਨਾ", "bn": "তেলেঙ্গানা", "as": "তেলেংগানা", "ks": "تیلَنگانہ"}, "Punjab": {"en": "Punjab", "hi": "पंजाब", "kn": "ಪಂಜಾಬ್", "or": "ପଞ୍ଜାବ", "mr": "पंजाब", "ta": "பஞ்சாப்", "te": "పంజాబ్", "ml": "പഞ്ചാബ്", "gu": "પંજાબ", "pa": "ਪੰਜਾਬ", "bn": "পাঞ্জাব", "as": "পঞ্জাৱ", "ks": "پَنجاب"}, "Haryana": {"en": "Haryana", "hi": "हरियाणा", "kn": "ಹರಿಯಾಣ", "or": "ହରିୟାଣା", "mr": "हरियाणा", "ta": "ஹரியானா", "te": "హర్యానా", "ml": "ഹരിയാന", "gu": "હરિયાણા", "pa": "ਹਰਿਆਣਾ", "bn": "হরিয়ানা", "as": "হাৰিয়ানা", "ks": "ہَریانہ"}, "Rajasthan": {"en": "Rajasthan", "hi": "राजस्थान", "kn": "ರಾಜಸ್ಥಾನ", "or": "ରାଜସ୍ଥାନ", "mr": "राजस्थान", "ta": "ராஜஸ்தான்", "te": "రాజస్థాన్", "ml": "രാജസ്ഥാൻ", "gu": "રાજસ્થાન", "pa": "ਰਾਜਸਥਾਨ", "bn": "রাজস্থান", "as": "ৰাজস্থান", "ks": "راجَستھان"}, "Uttar Pradesh": {"en": "Uttar Pradesh", "hi": "उत्तर प्रदेश", "kn": "ಉತ್ತರ ಪ್ರದೇಶ", "or": "ଉତ୍ତର ପ୍ରଦେଶ", "mr": "उत्तर प्रदेश", "ta": "உத்தரப் பிரதேசம்", "te": "ఉత్తరప్రదేశ్", "ml": "ഉത്തർപ്രദേശ്", "gu": "ઉત્તર પ્રદેશ", "pa": "ਉੱਤਰ ਪ੍ਰਦੇਸ਼", "bn": "উত্তরপ্রদেশ", "as": "উত্তৰপ্ৰদেশ", "ks": "اُتَر پَرٛدیش"}, "West Bengal": {"en": "West Bengal", "hi": "पश्चिम बंगाल", "kn": "ಪಶ್ಚಿಮ ಬಂಗಾಳ", "or": "ପଶ୍ଚିମ ବଙ୍ଗ", "mr": "पश्चिम बंगाल", "ta": "மேற்கு வங்காளம்", "te": "పశ్చిమ బెంగాల్", "ml": "പശ്ചിമ ബംഗാൾ", "gu": "પશ્ચિમ બંગાળ", "pa": "ਪੱਛਮੀ ਬੰਗਾਲ", "bn": "পশ্চিমবঙ্গ", "as": "পশ্চিমবংগ", "ks": "مَغرِبی بَنٛگال"}, "Bihar": {"en": "Bihar", "hi": "बिहार", "kn": "ಬಿಹಾರ", "or": "ବିହାର", "mr": "बिहार", "ta": "பீகார்", "te": "బీహార్", "ml": "ബീഹാർ", "gu": "બિહાર", "pa": "ਬਿਹਾਰ", "bn": "বিহার", "as": "বিহাৰ", "ks": "بِہار"}, "Kerala": {"en": "Kerala", "hi": "केरल", "kn": "ಕೇರಳ", "or": "କେରଳ", "mr": "केरळ", "ta": "கேரளா", "te": "కేరళ", "ml": "കേരളം", "gu": "કેરળ", "pa": "ਕੇਰਲ", "bn": "কেরল", "as": "কেৰালা", "ks": "کیٚرَلا"}, "Keralam": {"en": "Keralam", "hi": "केरल", "kn": "ಕೇರಳ", "or": "କେରଳ", "mr": "केरळ", "ta": "கேரளா", "te": "కేరళ", "ml": "കേരളം", "gu": "કેરળ", "pa": "ਕੇਰਲ", "bn": "কেরল", "as": "কেৰালা", "ks": "کیٚرَلا"}, "Assam": {"en": "Assam", "hi": "असम", "kn": "ಅಸ್ಸಾಂ", "or": "ଆସାମ", "mr": "आसाम", "ta": "அசாம்", "te": "అస్సాం", "ml": "അസം", "gu": "આસામ", "pa": "ਅਸਾਮ", "bn": "আসাম", "as": "অসম", "ks": "آسام"}, "Jammu and Kashmir": {"en": "Jammu and Kashmir", "hi": "जम्मू और कश्मीर", "kn": "ಜಮ್ಮು ಮತ್ತು ಕಾಶ್ಮೀರ", "or": "ଜାମ୍ମୁ ଓ କାଶ୍ମୀର", "mr": "जम्मू आणि काश्मीर", "ta": "ஜம்மு காஷ்மீர்", "te": "జమ్మూ కాశ్మీర్", "ml": "ജമ്മു കശ്മീർ", "gu": "જમ્મુ અને કાશ્મીર", "pa": "ਜੰਮੂ ਅਤੇ ਕਸ਼ਮੀਰ", "bn": "জম্মু ও কাশ্মীর", "as": "জম্মু আৰু কাশ্মীৰ", "ks": "جۆم تہٕ کٔشیٖر"}, "Himachal Pradesh": {"en": "Himachal Pradesh", "hi": "हिमाचल प्रदेश", "kn": "ಹಿಮಾಚಲ ಪ್ರದೇಶ", "or": "ହିମାଚଳ ପ୍ରଦେଶ", "mr": "हिमाचल प्रदेश", "ta": "இமாச்சலப் பிரதேசம்", "te": "హిమాచల్ ప్రదేశ్", "ml": "ഹിമാചൽ പ്രദേശ്", "gu": "હિમાચલ પ્રદેશ", "pa": "ਹਿਮਾਚਲ ਪ੍ਰਦੇਸ਼", "bn": "হিমাচল প্রদেশ", "as": "হিমাচল প্ৰদেশ", "ks": "ہِماچَل پَرٛدیش"}, "Uttarakhand": {"en": "Uttarakhand", "hi": "उत्तराखंड", "kn": "ಉತ್ತರಾಖಂಡ", "or": "ଉତ୍ତରାଖଣ୍ଡ", "mr": "उत्तराखंड", "ta": "உத்தரகாண்ட்", "te": "ఉత్తరాఖండ్", "ml": "ഉത്തരാഖണ്ഡ്", "gu": "ઉત્તરાખંડ", "pa": "ਉੱਤਰਾਖੰਡ", "bn": "উত্তরাখণ্ড", "as": "উত্তৰাখণ্ড", "ks": "اُتراکھَنٛڈ"}, "Chattisgarh": {"en": "Chattisgarh", "hi": "छत्तीसगढ़", "kn": "ಛತ್ತೀಸ್‌ಗಢ", "or": "ଛତିଶଗଡ଼", "mr": "छत्तीसगढ", "ta": "சத்தீஸ்கர்", "te": "ఛత్తీస్‌గఢ్", "ml": "ഛത്തീസ്ഗഢ്", "gu": "છત્તીસગઢ", "pa": "ਛੱਤੀਸਗੜ੍ਹ", "bn": "ছত্তিশগড়", "as": "ছত্তীশগড়", "ks": "چھَتِیس گَڑھ"}, "Tripura": {"en": "Tripura", "hi": "त्रिपुरा", "kn": "ತ್ರಿಪುರ", "or": "ତ୍ରିପୁରା", "mr": "त्रिपुरा", "ta": "திரிபுரா", "te": "త్రిపుర", "ml": "ത്രിപുര", "gu": "ત્રિપુરા", "pa": "ਤ੍ਰਿਪੁਰਾ", "bn": "ত্রিপুরা", "as": "ত্ৰিপুৰা", "ks": "تِرپوٗرا"}, "Delhi": {"en": "Delhi", "hi": "दिल्ली", "kn": "ದೆಹಲಿ", "or": "ଦିଲ୍ଲୀ", "mr": "दिल्ली", "ta": "டெல்லி", "te": "ఢిల్లీ", "ml": "ഡൽഹി", "gu": "દિલ્હી", "pa": "ਦਿੱਲੀ", "bn": "দিল্লি", "as": "দিল্লী", "ks": "دِلی"}, "NCT of Delhi": {"en": "NCT of Delhi", "hi": "दिल्ली", "kn": "ದೆಹಲಿ", "or": "ଦିଲ୍ଲୀ", "mr": "दिल्ली", "ta": "டெல்லி", "te": "ఢిల్లీ", "ml": "ഡൽഹി", "gu": "દિલ્હી", "pa": "ਦਿੱਲੀ", "bn": "দিল্লি", "as": "দিল্লী", "ks": "دِلی"}, "Chandigarh": {"en": "Chandigarh", "hi": "चंडीगढ़", "kn": "ಚಂಡೀಗಢ", "or": "ଚଣ୍ଡିଗଡ଼", "mr": "चंदिगढ", "ta": "சண்டிகர்", "te": "చండీగఢ్", "ml": "ചണ്ഡീഗഡ്", "gu": "ચંદીગઢ", "pa": "ਚੰਡੀਗੜ੍ਹ", "bn": "চণ্ডীগড়", "as": "চণ্ডীগড়", "ks": "چَنڈی گَڑھ"}}, "districts": {"Shivamogga": {"en": "Shivamogga", "hi": "शिवमोग्गा", "kn": "ಶಿವಮೊಗ್ಗ", "or": "ଶିବମୋଗା", "mr": "शिवमोग्गा", "ta": "சிவமோகா", "te": "శివమొగ్గ", "ml": "ശിവമോഗ", "gu": "શિવમોગ્ગા", "pa": "ਸ਼ਿਵਮੋਗਾ", "bn": "শিবমোগ্গা", "as": "শিৱমোগ্গা", "ks": "شِواموگا"}, "Shimoga": {"en": "Shimoga", "hi": "शिमोगा", "kn": "ಶಿವಮೊಗ್ಗ", "or": "ଶିବମୋଗା", "mr": "शिमोगा", "ta": "ஷிமோகா", "te": "షిమోగా", "ml": "ഷിമോഗ", "gu": "શિમોગા", "pa": "ਸ਼ਿਮੋਗਾ", "bn": "শিমোগা", "as": "শিমোগা", "ks": "شِموگا"}, "Davanagere": {"en": "Davanagere", "hi": "दावणगेरे", "kn": "ದಾವಣಗೆರೆ", "or": "ଦାବଣଗେରେ", "mr": "दावणगेरे", "ta": "தாவணகெரே", "te": "దావణగెరె", "ml": "ദാവൺഗരെ", "gu": "દાવણગેરે", "pa": "ਦਾਵਣਗੇਰੇ", "bn": "দাবানগেরে", "as": "দাৱনগেৰে", "ks": "داوَن گیرے"}, "Bengaluru": {"en": "Bengaluru", "hi": "बेंगलुरु", "kn": "ಬೆಂಗಳೂರು", "or": "ବେଙ୍ଗାଲୁରୁ", "mr": "बंगळुरू", "ta": "பெங்களூரு", "te": "బెంగళూరు", "ml": "ബെംഗളൂരു", "gu": "બેંગલુરુ", "pa": "ਬੈਂਗਲੁਰੂ", "bn": "বেঙ্গালুরু", "as": "বেংগালুৰু", "ks": "بَنگلوروٗ"}, "Bengaluru South": {"en": "Bengaluru South", "hi": "बेंगलुरु दक्षिण", "kn": "ಬೆಂಗಳೂರು ದಕ್ಷಿಣ", "or": "ବେଙ୍ଗାଲୁରୁ ଦକ୍ଷିଣ", "mr": "बंगळुरू दक्षिण", "ta": "தெற்கு பெங்களூரு", "te": "బెంగళూరు దక్షిణ", "ml": "തെക്കൻ ബെംഗളൂരു", "gu": "બેંગલુરુ દક્ષિણ", "pa": "ਬੈਂਗਲੁਰੂ ਦੱਖਣ", "bn": "বেঙ্গালুরু দক্ষিণ", "as": "বেংগালুৰু দক্ষিণ", "ks": "جَنوٗبی بَنگلوروٗ"}, "Dharwad": {"en": "Dharwad", "hi": "धारवाड़", "kn": "ಧಾರವಾಡ", "or": "ଧାରୱାଡ଼", "mr": "धारवाड", "ta": "தார்வாட்", "te": "ధార్వాడ్", "ml": "ധാർവാഡ്", "gu": "ધારવાડ", "pa": "ਧਾਰਵਾੜ", "bn": "ধারওয়াড়", "as": "ধাৰৱাড়", "ks": "دھارواڑ"}, "Mysuru": {"en": "Mysuru", "hi": "मैसूरु", "kn": "ಮೈಸೂರು", "or": "ମହୀଶୂର", "mr": "म्हैसूर", "ta": "மைசூரு", "te": "మైసూరు", "ml": "മൈസൂരു", "gu": "મૈસુરુ", "pa": "ਮੈਸੂਰ", "bn": "মহীশূর", "as": "মহীশূৰ", "ks": "مَیسوٗروٗ"}, "Vijayanagara": {"en": "Vijayanagara", "hi": "विजयनगर", "kn": "ವಿಜಯನಗರ", "or": "ବିଜୟନଗର", "mr": "विजयनगर", "ta": "விஜயநகரா", "te": "విజయనగరం", "ml": "വിജയനഗര", "gu": "વિજયનગર", "pa": "ਵਿਜੇਨਗਰ", "bn": "বিজয়নগর", "as": "বিজয়নগৰ", "ks": "وِجَی نَگَر"}, "Koppal": {"en": "Koppal", "hi": "कोप्पल", "kn": "ಕೊಪ್ಪಳ", "or": "କୋପ୍ପଳ", "mr": "कोप्पळ", "ta": "கொப்பல்", "te": "కొప్పల్", "ml": "കൊപ്പൽ", "gu": "કોપ્પલ", "pa": "ਕੋਪਲ", "bn": "কোপ্পল", "as": "কোপ্পাল", "ks": "کوپَل"}, "Kantabaji": {"en": "Kantabaji", "hi": "कांटाबांजी", "kn": "ಕಾಂಟಾಬಾಂಜಿ", "or": "କଣ୍ଟାବାଞ୍ଜି", "mr": "कांटाबांजी", "ta": "காந்தாபாஞ்சி", "te": "కాంటాబాంజీ", "ml": "കാന്താബാഞ്ചി", "gu": "કાંટાબાંજી", "pa": "ਕਾਂਟਾਬਾਂਜੀ", "bn": "কাঁটাবাঞ্জি", "as": "কাঁটাবাঞ্জী", "ks": "کانٹابانجی"}, "Balangir": {"en": "Balangir", "hi": "बलांगिर", "kn": "ಬಲಾಂಗೀರ್", "or": "ବଲାଙ୍ଗୀର", "mr": "बलांगिर", "ta": "பலாங்கிர்", "te": "బలాంగీర్", "ml": "ബലാംഗിർ", "gu": "બલાંગીર", "pa": "ਬਲਾਂਗੀਰ", "bn": "বলাঙ্গির", "as": "বলাংগীৰ", "ks": "بالانٛگِر"}, "Cuttack": {"en": "Cuttack", "hi": "कटक", "kn": "ಕಟಕ್", "or": "କଟକ", "mr": "कटक", "ta": "கட்டாக்", "te": "కటక్", "ml": "കട്ടക്ക്", "gu": "કટક", "pa": "ਕਟਕ", "bn": "কটক", "as": "কটক", "ks": "کَٹَک"}, "Sambalpur": {"en": "Sambalpur", "hi": "संबलपुर", "kn": "ಸಂಬಲ್ಪುರ", "or": "ସମ୍ବଲପୁର", "mr": "संबलपूर", "ta": "சம்பல்பூர்", "te": "సంబల్పూర్", "ml": "സമ്പൽപൂർ", "gu": "સંબલપુર", "pa": "ਸੰਬਲਪੁਰ", "bn": "সম্বলপুর", "as": "সম্বলপুৰ", "ks": "سَمبَلپوٗر"}, "Indore": {"en": "Indore", "hi": "इंदौर", "kn": "ಇಂದೋರ್", "or": "ଇନ୍ଦୋର", "mr": "इंदूर", "ta": "இந்தூர்", "te": "ఇండోర్", "ml": "ഇൻഡോർ", "gu": "ઇન્દોર", "pa": "ਇੰਦੌਰ", "bn": "ইন্দোর", "as": "ইન્દোৰ", "ks": "اِندور"}, "Pune": {"en": "Pune", "hi": "पुणे", "kn": "ಪುಣೆ", "or": "ପୁଣେ", "mr": "पुणे", "ta": "புனே", "te": "పూణే", "ml": "പൂനെ", "gu": "પુણે", "pa": "ਪੁਣੇ", "bn": "পুনে", "as": "পুনে", "ks": "پوٗنے"}, "Nashik": {"en": "Nashik", "hi": "नासिक", "kn": "ನಾಸಿಕ್", "or": "ନାସିକ", "mr": "नाशिक", "ta": "நாசிக்", "te": "నాసిక్", "ml": "നാസിക്", "gu": "નાસિક", "pa": "ਨਾਸਿਕ", "bn": "নাসিক", "as": "নাচিক", "ks": "ناسِک"}, "Ahmedabad": {"en": "Ahmedabad", "hi": "अहमदाबाद", "kn": "ಅಹಮದಾಬಾದ್", "or": "ଅହମଦାବାଦ", "mr": "अहमदाबाद", "ta": "அகமதாபாத்", "te": "అహ్మదాబాద్", "ml": "അഹമ്മദാബാദ്", "gu": "અમદાવાદ", "pa": "ਅਹਿਮਦਾਬਾਦ", "bn": "আহমেদাবাদ", "as": "আহমেদাবাদ", "ks": "اَحمَد آباد"}, "Surat": {"en": "Surat", "hi": "सूरत", "kn": "ಸೂರತ್", "or": "ସୁರତ", "mr": "सुरत", "ta": "சூரத்", "te": "సూరత్", "ml": "സൂററ്റ്", "gu": "સૂરત", "pa": "ਸੂਰਤ", "bn": "সুরাট", "as": "চুৰাট", "ks": "سوٗرَت"}, "Baramulla": {"en": "Baramulla", "hi": "बारामूला", "kn": "ಬಾರಾಮುಲ್ಲಾ", "or": "ବାରାମୁଲ୍ଲା", "mr": "बारामुल्ला", "ta": "பாராமுல்லா", "te": "బారాముల్లా", "ml": "ബാരാമുള്ള", "gu": "બારામુલ્લા", "pa": "ਬਾਰਾਮੂਲਾ", "bn": "বারামুল্লা", "as": "বাৰামুল্লা", "ks": "بارَہ موٗلَہ"}, "Sopore": {"en": "Sopore", "hi": "सोपोर", "kn": "ಸೋಪೋರ್", "or": "ସୋପୋର", "mr": "सोपोर", "ta": "சோபூர்", "te": "సోపోర్", "ml": "സോപോർ", "gu": "સોપોર", "pa": "ਸੋਪੋਰ", "bn": "সোপোর", "as": "চোপোৰ", "ks": "سوپوٗر"}, "Yeshwanthpur": {"en": "Yeshwanthpur", "hi": "यशवंतपुर", "kn": "ಯಶವಂತಪುರ", "or": "ୟଶବନ୍ତପୁର", "mr": "यशवंतपूर", "ta": "யஷ்வந்த்பூர்", "te": "యశ్వంతపూర్", "ml": "യശ്വന്ത്പൂർ", "gu": "યશવંતપુર", "pa": "ਯਸ਼ਵੰਤਪੁਰ", "bn": "যশবন্তপুর", "as": "যশৱন্তপুৰ", "ks": "یشونت پور"}}};

// Pre-bundled UPAg supply outlook & advisory translations
const STATIC_SUPPLY_OUTLOOK: Record<string, Record<string, string>> = {"Robust Government Procurement & Buffer Stocks": {"en": "Robust Government Procurement & Buffer Stocks", "hi": "मजबूत सरकारी खरीद और बफर स्टॉक", "kn": "ಬಲವಾದ ಸರ್ಕಾರಿ ಖರೀದಿ ಮತ್ತು ಬಫರ್ ಸ್ಟಾಕ್", "gu": "મજબૂત સરકારી ખરીદી અને બફર સ્ટોક", "mr": "मजबूत सरकारी खरेदी आणि बफर स्टॉक", "ta": "வலுவான அரசு கொள்முதல் & கையிருப்பு", "te": "బలమైన ప్రభుత్వ సేకరణ & బఫర్ స్టాక్", "ml": "ശക്തമായ സർക്കാർ സംഭരണവും ബഫർ സ്റ്റോക്കും", "pa": "ਮਜ਼ਬੂਤ ​​ਸਰਕਾਰੀ ਖਰੀਦ ਅਤੇ ਬਫਰ ਸਟਾਕ", "bn": "দৃঢ় সরকারি সংগ্রহ ও বাফার স্টক", "or": "ଦୃଢ଼ ସରକାରୀ ସଂଗ୍ରହ ଏବଂ ବଫର୍ ଷ୍ଟକ୍", "as": "দৃঢ় চৰকাৰী ক্ৰয় আৰু বাফাৰ মজুত", "ks": "مضبوط سرکاری خریداری اور بفر اسٹاک"}, "Adequate National Buffer Stocks": {"en": "Adequate National Buffer Stocks", "hi": "पर्याप्त राष्ट्रीय बफर स्टॉक", "kn": "ಸಾಕಷ್ಟು ರಾಷ್ಟ್ರೀಯ ಬಫರ್ ಸ್ಟಾಕ್", "gu": "પર્યાપ્ત રાષ્ટ્રીય બફર સ્ટોક", "mr": "पुरेसा राष्ट्रीय बफर स्टॉक", "ta": "போதுமான தேசிய கையிருப்பு", "te": "సరిపడా జాతీయ బఫర్ నిల్వలు", "ml": "മതിയായ ദേശീയ ബഫർ സ്റ്റോക്ക്", "pa": "ਲੋੜੀਂਦਾ ਰਾਸ਼ਟਰੀ ਬਫਰ ਸਟਾਕ", "bn": "পর্যাপ্ত জাতীয় বাফার স্টক", "or": "ପର୍ଯ୍ୟାପ୍ତ ଜାତୀୟ ବଫର୍ ଷ୍ଟକ୍", "as": "পৰ্যাপ্ত ৰাষ্ট্ৰীয় বাফাৰ মজুত", "ks": "کافی قومی بفر اسٹاک"}, "Normal Stable Supply": {"en": "Normal Stable Supply", "hi": "सामान्य स्थिर आपूर्ति", "kn": "ಸಾಮಾನ್ಯ ಸ್ಥಿರ ಪೂರೈಕೆ", "gu": "સામાન્ય સ્થિર પુરવઠો", "mr": "सामान्य स्थिर पुरवठा", "ta": "சாதாரண நிலையான விநியோகம்", "te": "సాధారణ స్థిరమైన సరఫరా", "ml": "സാധാരണ സ്ഥിരതയുള്ള വിതരണം", "pa": "ਆਮ ਸਥਿਰ ਸਪਲਾਈ", "bn": "স্বাভাবিক স্থিতিশীল সরবরাহ", "or": "ସାଧାରଣ ସ୍ଥିର ଯୋଗାଣ", "as": "সাধাৰণ সুস্থিৰ যোগান", "ks": "عام مستحکم سپلائی"}, "Bumper Harvest / Good Demand": {"en": "Bumper Harvest / Good Demand", "hi": "बंपर पैदावार / अच्छी मांग", "kn": "ಉತ್ತಮ ಫಸಲು / ಉತ್ತಮ ಬೇಡಿಕೆ", "gu": "વિપુલ પાક / સારી માંગ", "mr": "बंपर उत्पादन / चांगली मागणी", "ta": "அமோக விளைச்சல் / நல்ல தேவை", "te": "బంపర్ దిగుబడి / మంచి డిమాండ్", "ml": "ബമ്പർ വിളവെടുപ്പ് / നല്ല ഡിമാൻഡ്", "pa": "ਬੰਪਰ ਫ਼ਸਲ / ਚੰਗੀ ਮੰਗ", "bn": "বাম্পার ফলন / ভালো চাহিদা", "or": "ବମ୍ପର ଫସଲ / ଉତ୍ତମ ଚାହିଦା", "as": "বাম্পাৰ উৎপাদন / ভাল চাহিদা", "ks": "بمپر پیداوار / اچھی مانگ"}, "Steady Export & FCI Demand": {"en": "Steady Export & FCI Demand", "hi": "स्थिर निर्यात और एफसीआई मांग", "kn": "ಸ್ಥಿರ ರಫ್ತು ಮತ್ತು ಎಫ್‌ಸಿಐ ಬೇಡಿಕೆ", "gu": "સ્થિર નિકાસ અને એફસીઆઈ માંગ", "mr": "स्थिर निर्यात आणि एफसीआय मागणी", "ta": "நிலையான ஏற்றுமதி & FCI தேவை", "te": "స్థిరమైన ఎగుమతి & FCI డిమాండ్", "ml": "സ്ഥിരമായ കയറ്റുമതിയും FCI ഡിമാൻഡും", "pa": "ਸਥਿਰ ਨਿਰਯਾਤ ਅਤੇ FCI ਮੰਗ", "bn": "স্থিতিশীল রফতানি ও এফসিআই চাহিদা", "or": "ସ୍ଥିର ରପ୍ତାନୀ ଏବଂ ଏଫସିଆଇ ଚାହିଦା", "as": "সুস্থিৰ ৰপ্তানি আৰু এফচিআই চাহিদা", "ks": "مستحکم برآمد اور ایف سی آئی مانگ"}, "Tight Supply / Firm Prices Expected": {"en": "Tight Supply / Firm Prices Expected", "hi": "कम आपूर्ति / भाव में मजबूती की उम्मीद", "kn": "ಕಡಿಮೆ ಪೂರೈಕೆ / ದರ ಏರಿಕೆ ನಿರೀಕ್ಷೆ", "gu": "ઓછો પુરવઠો / ભાવ મજબૂત રહેવાની અપેક્ષા", "mr": "कमी पुरवठा / भाव वाढण्याची अपेक्षा", "ta": "குறைந்த விநியோகம் / விலை உயர்வு எதிர்பார்ப்பு", "te": "తక్కువ సరఫరా / ధరల పెరుగుదల అంచనా", "ml": "കുറഞ്ഞ വിതരണം / വിലവർദ്ധനവ് പ്രതീക്ഷിക്കുന്നു", "pa": "ਘੱਟ ਸਪਲਾਈ / ਮੁੱਲ ਚੜ੍ਹਨ ਦੀ ਉਮੀਦ", "bn": "কম সরবরাহ / দাম বৃদ্ধির প্রত্যাশা", "or": "କମ୍ ଯୋଗାଣ / ଦର ବୃଦ୍ଧିର ଆଶା", "as": "কম যোগান / দাম বৃদ্ধিৰ আশা", "ks": "تنگ سپلائی / مضبوط قیمتوں کی توقع"}, "Heavy Flush Arrivals": {"en": "Heavy Flush Arrivals", "hi": "भारी नई आवक", "kn": "ಭಾರೀ ಹೊಸ ಆವಕ", "gu": "ભારે નવી આવક", "mr": "मोठ्या प्रमाणावर नवीन आवक", "ta": "அதிகப்படியான புதிய வரத்து", "te": "భారీ కొత్త రాకలు", "ml": "വൻതോതിലുള്ള പുതിയ വരവ്", "pa": "ਭਾਰੀ ਨਵੀਂ ਆਮਦ", "bn": "বিপুল নতুন আমদানি", "or": "ଅଧିକ ନୂତନ ଆଗମନ", "as": "বিপুল নতুন আগমন", "ks": "بھاری نئی آمد"}, "Strong Textile Mill Inquiries": {"en": "Strong Textile Mill Inquiries", "hi": "टेक्सटाइल मिलों से मजबूत मांग", "kn": "ಜವಳಿ ಗಿರಣಿಗಳಿಂದ ಬಲವಾದ ಬೇಡಿಕೆ", "gu": "ટેક્સટાઇલ મિલો તરફથી મજબૂત માંગ", "mr": "कापड गिरण्यांकडून जोरदार मागणी", "ta": "ஜவுளி ஆலைகளிலிருந்து வலுவான தேவை", "te": "టెక్స్‌టైల్ మిల్లుల నుండి బలమైన డిమాండ్", "ml": "ടെക്സ്റ്റൈൽ മില്ലുകളിൽ നിന്നുള്ള ശക്തമായ ഡിമാൻഡ്", "pa": "ਟੈਕਸਟਾਈਲ ਮਿੱਲਾਂ ਤੋਂ ਭਾਰੀ ਮੰਗ", "bn": "টেক্সটাইল মিল থেকে শক্তিশালী চাহিদা", "or": "ଟେକ୍ସଟାଇଲ୍ ମିଲ୍ ଚାହିଦା", "as": "বস্ত্ৰ উদ্যোগৰ পৰা ভাল চাহিদা", "ks": "ٹیکسٹائل ملوں کی زبردست مانگ"}, "Robust Oil Mill Crushing Demand": {"en": "Robust Oil Mill Crushing Demand", "hi": "तेल मिलों की मजबूत पेराई मांग", "kn": "ಎಣ್ಣೆ ಗಿರಣಿಗಳಿಂದ ಉತ್ತಮ ಬೇಡಿಕೆ", "gu": "ઓઇલ મિલોની મજબૂત પિલાણ માંગ", "mr": "तेल गिरण्यांची मजबूत गाळप मागणी", "ta": "எண்ணெய் ஆலைகளின் வலுவான தேவை", "te": "ఆయిల్ మిల్లుల బలమైన క్రషింగ్ డిమాండ్", "ml": "ഓയിൽ മില്ലുകളുടെ ശക്തമായ ഡിമാൻഡ്", "pa": "ਤੇਲ ਮਿੱਲਾਂ ਦੀ ਮਜ਼ਬੂਤ ​​ਮੰਗ", "bn": "তেল মিলের জোরালো চাহিদা", "or": "ତୈଳ ମିଲ୍ ପେଡ଼ିବା ଚାହିଦା", "as": "তেল কলৰ শক্তিশালী চাহিদা", "ks": "تیل ملوں کی زبردست مانگ"}};
const STATIC_ADVISORIES: Record<string, Record<string, string>> = {"MSP procurement centers operating at full capacity. Register lots on e-NAM for quick settlement.": {"en": "MSP procurement centers operating at full capacity. Register lots on e-NAM for quick settlement.", "hi": "एमएसपी खरीद केंद्र पूरी क्षमता से चालू हैं। त्वरित भुगतान के लिए ई-नाम पर लॉट पंजीकृत करें।", "kn": "ಎಂಎಸ್‌ಪಿ ಖರೀದಿ ಕೇಂದ್ರಗಳು ಪೂರ್ಣ ಸಾಮರ್ಥ್ಯದಲ್ಲಿ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತಿವೆ. ತ್ವರಿತ ಇತ್ಯರ್ಥಕ್ಕಾಗಿ ಇ-ನ್ಯಾಮ್‌ನಲ್ಲಿ ನೋಂದಾಯಿಸಿ.", "gu": "એમએસપી ખરીદ કેન્દ્રો સંપૂર્ણ ક્ષમતા સાથે કાર્યરત છે. ઝડપી પતાવટ માટે ઈ-નામ પર લોટ નોંધાવો.", "mr": "हमीभाव (MSP) खरेदी केंद्र पूर्ण क्षमतेने सुरू आहेत. त्वरित पेमेंटसाठी ई-नामवर लॉट नोंदवा.", "ta": "MSP கொள்முதல் மையங்கள் முழு திறனுடன் செயல்படுகின்றன. விரைவான தீர்விற்கு இ-நாமில் பதிவு செய்யவும்.", "te": "MSP సేకరణ కేంద్రాలు పూర్తి సామర్థ్యంతో పనిచేస్తున్నాయి. శీఘ్ర చెల్లింపు కోసం ఇ-నామ్‌లో నమోదు చేయండి.", "ml": "എംഎസ്പി സംഭരണ ​​കേന്ദ്രങ്ങൾ പൂർണ്ണ ശേഷിയിൽ പ്രവർത്തിക്കുന്നു. വേഗത്തിലുള്ള ഒത്തുതീർപ്പിനായി ഇ-നാമിൽ രജിസ്റ്റർ ചെയ്യുക.", "pa": "ਐਮਐਸਪੀ ਖਰੀਦ ਕੇਂਦਰ ਪੂਰੀ ਸਮਰੱਥਾ ਨਾਲ ਚੱਲ ਰਹੇ ਹਨ। ਤੁਰੰਤ ਨਿਪਟਾਰੇ ਲਈ ਈ-ਨਾਮ 'ਤੇ ਲਾਟ ਦਰਜ ਕਰੋ।", "bn": "এমএসপি ক্রয় কেন্দ্রগুলি পূর্ণ ক্ষমতায় কাজ করছে। দ্রুত অর্থপ্রদানের জন্য ই-নামে লট নিবন্ধন করুন।", "or": "ଏମଏସପି କ୍ରୟ କେନ୍ଦ୍ରଗୁଡ଼ିକ ସମ୍ପୂର୍ଣ୍ଣ କାର୍ଯ୍ୟକ୍ଷମ ଅଛି। ଶୀଘ୍ର ବିଲ୍ ପାଇଁ ଇ-ନାମରେ ଲଟ୍ ପଞ୍ଜୀକରଣ କରନ୍ତୁ।", "as": "এমএছপি ক্ৰয় কেন্দ্ৰসমূহ সম্পূৰ্ণ ক্ষমতাত চলি আছে। দ্ৰুত নিষ্পত্তিৰ বাবে ই-নামত লট পঞ্জীয়ন কৰক।", "ks": "ایم ایس پی خریداری مراکز مکمل صلاحیت سے کام کر رہے ہیں۔ فوری تصفیہ کیلئے ای-نام پر لاٹ رجسٹر کریں۔"}, "Stable procurement price. Hold dry grain for 2-3 weeks for optimal realization.": {"en": "Stable procurement price. Hold dry grain for 2-3 weeks for optimal realization.", "hi": "खरीद भाव स्थिर है। बेहतर मूल्य प्राप्ति के लिए सूखे अनाज को 2-3 सप्ताह रोककर बेचें।", "kn": "ಖರೀದಿ ಬೆಲೆ ಸ್ಥಿರವಾಗಿದೆ. ಉತ್ತಮ ಲಾಭಕ್ಕಾಗಿ ಒಣ ಧಾನ್ಯವನ್ನು 2-3 ವಾರಗಳ ಕಾಲ ಇರಿಸಿ ನಂತರ ಮಾರಿ.", "gu": "ખરીદ ભાવ સ્થિર છે. શ્રેષ્ઠ વળતર મેળવવા માટે સૂકા અનાજને 2-3 અઠવાડિયા સાચવીને વેચો.", "mr": "खरेदी भाव स्थिर आहे. अधिक चांगल्या भावासाठी सुके धान्य 2-3 आठवडे थांबवून विका.", "ta": "கொள்முதல் விலை நிலையாக உள்ளது. சிறந்த விலைக்கு உலர் தானியங்களை 2-3 வாரங்கள் சேமித்து விற்கவும்.", "te": "సేకరణ ధర స్థిరంగా ఉంది. సరైన రాబడి కోసం ఎండిన ధాన్యాన్ని 2-3 వారాలు నిల్వ ఉంచి అమ్మండి.", "ml": "സംഭരണ ​​വില സ്ഥിരമാണ്. മികച്ച വരുമാനത്തിനായി ഉണങ്ങിയ ധാന്യങ്ങൾ 2-3 ആഴ്ച സൂക്ഷിച്ച് വിൽക്കുക.", "pa": "ਖਰੀਦ ਮੁੱਲ ਸਥਿਰ ਹੈ। ਵਧੀਆ ਮੁਨਾਫੇ ਲਈ ਸੁੱਕੇ ਅਨਾਜ ਨੂੰ 2-3 ਹਫ਼ਤੇ ਰੱਖ ਕੇ ਵੇਚੋ।", "bn": "সংগ্রহের দাম স্থিতিশীল। সেরা দাম পেতে শুকনো শস্য ২-৩ সপ্তাহ ধরে রেখে বিক্রি করুন।", "or": "ସଂଗ୍ରହ ଦର ସ୍ଥିର ରହିଛି। ଉତ୍ତମ ଲାଭ ପାଇଁ ଶୁଖିଲା ଶସ୍ୟକୁ ୨-୩ ସପ୍ତାହ ରଖି ବିକ୍ରୟ କରନ୍ତୁ।", "as": "ক্ৰয় মূল্য সুস্থিৰ। উত্তম মূল্য পাবলৈ শুকান শস্য ২-৩ সপ্তাহ ৰাখি বিক্ৰী কৰক।", "ks": "خریداری کی قیمت مستحکم ہے۔ بہترین آمدنی کیلئے سوکھے اناج کو 2-3 ہفتے رکھ کر بیچیں۔"}, "High festive demand in terminal markets. Favorable window for Grade A fruit selling.": {"en": "High festive demand in terminal markets. Favorable window for Grade A fruit selling.", "hi": "प्रमुख बाजारों में त्योहारी मांग अधिक है। ग्रेड ए फलों की बिक्री के लिए यह अनुकूल समय है।", "kn": "ಮುಖ್ಯ ಮಾರುಕಟ್ಟೆಗಳಲ್ಲಿ ಹಬ್ಬದ ಬೇಡಿಕೆ ಹೆಚ್ಚಾಗಿದೆ. ಗ್ರೇಡ್ ಎ ಹಣ್ಣುಗಳನ್ನು ಮಾರಾಟ ಮಾಡಲು ಇದು ಉತ್ತಮ ಸಮಯ.", "gu": "મુખ્ય બજારોમાં તહેવારોની માંગ વધારે છે. ગ્રેડ એ ફળોના વેચાણ માટે આ અનુકૂળ સમય છે.", "mr": "प्रमुख बाजारांमध्ये सणासुदीची मागणी जास्त आहे. ग्रेड ए फळांच्या विक्रीसाठी ही अनुकूल वेळ आहे.", "ta": "முக்கிய சந்தைகளில் பண்டிகைக்கால தேவை அதிகமாக உள்ளது. தரம் A பழங்களை விற்க இது உகந்த நேரம்.", "te": "ప్రధాన మార్కెట్లలో పండుగ డిమాండ్ ఎక్కువగా ఉంది. గ్రేడ్ ఎ పండ్లను విక్రయించడానికి ఇది అనుకూలమైన సమయం.", "ml": "പ്രധാന വിപണികളിൽ ഉത്സവ ഡിമാൻഡ് കൂടുതലാണ്. ഗ്രേഡ് എ പഴങ്ങൾ വിൽക്കാൻ ഇത് അനുയോജ്യമായ സമയമാണ്.", "pa": "ਵੱਡੇ ਬਾਜ਼ਾਰਾਂ ਵਿੱਚ ਤਿਉਹਾਰਾਂ ਦੀ ਮੰਗ ਜ਼ਿਆਦਾ ਹੈ। ਗ੍ਰੇਡ ਏ ਫਲਾਂ ਦੀ ਵਿਕਰੀ ਲਈ ਅਨੁਕੂਲ ਸਮਾਂ ਹੈ।", "bn": "প্রধান বাজারগুলিতে উৎসবের চাহিদা বেশি। গ্রেড এ ফল বিক্রির জন্য এটি উপযুক্ত সময়।", "or": "ପ୍ରମୁଖ ବଜାରରେ ପର୍ବପର୍ବାଣୀ ଚାହିଦା ଅଧିକ ରହିଛି। ଗ୍ରେଡ୍ ଏ ଫଳ ବିକ୍ରୟ ପାଇଁ ଅନୁକୂଳ ସମୟ।", "as": "প্ৰধান বজাৰত উৎসৱৰ চাহিদা বেছি। গ্ৰেড এ ফল বিক্ৰীৰ বাবে উপযুক্ত সময়।", "ks": "بڑی منڈیوں میں تہوار کی مانگ زیادہ ہے۔ گریڈ اے پھل بیچنے کا بہترین موقع ہے۔"}, "Procurement centers active. Sell to verified buyers or e-NAM mandis for MSP compliance.": {"en": "Procurement centers active. Sell to verified buyers or e-NAM mandis for MSP compliance.", "hi": "सरकारी खरीद केंद्र सक्रिय हैं। एमएसपी अनुपालन के लिए सत्यापित खरीदारों या ई-नाम मंडियों में बेचें।", "kn": "ಸರ್ಕಾರಿ ಖರೀದಿ ಕೇಂದ್ರಗಳು ಸಕ್ರಿಯವಾಗಿವೆ. ಎಂಎಸ್‌ಪಿ ದರ ಪಡೆಯಲು ಪರಿಶೀಲಿಸಿದ ಖರೀದಿದಾರರಿಗೆ ಅಥವಾ ಇ-ನ್ಯಾಮ್ ಮಂಡಿಗಳಲ್ಲಿ ಮಾರಿ.", "gu": "સરકારી ખરીદ કેન્દ્રો સક્રિય છે. એમએસપી દર મેળવવા માટે ચકાસાયેલ ખરીદદારો અથવા ઈ-નામ મંડીઓમાં વેચો.", "mr": "खरेदी केंद्र सक्रिय आहेत. हमीभावासाठी पडताळणी केलेल्या खरेदीदारांना किंवा ई-नाम मंडईंमध्ये विका.", "ta": "கொள்முதல் மையங்கள் செயல்படுகின்றன. MSP விலைக்கு சரிபார்க்கப்பட்ட வாங்குபவர்கள் அல்லது இ-நாம் மண்டிகளில் விற்கவும்.", "te": "సేకరణ కేంద్రాలు చురుగ్గా ఉన్నాయి. MSP కోసం ధృవీకరించబడిన కొనుగోలుదారులు లేదా ఇ-నామ్ మండీలలో అమ్మండి.", "ml": "സംഭരണ ​​കേന്ദ്രങ്ങൾ സജീവമാണ്. എംഎസ്പി ലഭിക്കാൻ പരിശോധിച്ചുറപ്പിച്ച വാങ്ങുന്നവർക്കോ ഇ-നാം മണ്ഡികൾക്കോ ​​വിൽക്കുക.", "pa": "ਖਰੀਦ ਕੇਂਦਰ ਸਰਗਰਮ ਹਨ। ਐਮਐਸਪੀ ਲਈ ਪ੍ਰਮਾਣਿਤ ਖਰੀਦਦਾਰਾਂ ਜਾਂ ਈ-ਨਾਮ ਮੰਡੀਆਂ ਵਿੱਚ ਵੇਚੋ।", "bn": "ক্রয় কেন্দ্রগুলি সক্রিয় রয়েছে। এমএসপির জন্য যাচাইকৃত ক্রেতা বা ই-নাম মান্ডিতে বিক্রি করুন।", "or": "କ୍ରୟ କେନ୍ଦ୍ର ସକ୍ରିୟ ଅଛି। ଏମଏସପି ପାଇବା ପାଇଁ ଯାଞ୍ଚ ହୋଇଥିବା କ୍ରେତା କିମ୍ବା ଇ-ନାମ ମଣ୍ଡିରେ ବିକ୍ରୟ କରନ୍ତୁ।", "as": "ক্ৰয় কেন্দ্ৰসমূহ সক্ৰিয়। এমএছপি পাবলৈ পৰীক্ষিত ক্ৰেতা বা ই-নাম মণ্ডিত বিক্ৰী কৰক।", "ks": "خریداری مراکز فعال ہیں۔ ایم ایس پی کیلئے تصدیق شدہ خریداروں یا ای-نام منڈیوں میں فروخت کریں۔"}, "Supply tight in key consuming cities. Prices expected to appreciate; avoid distress sales.": {"en": "Supply tight in key consuming cities. Prices expected to appreciate; avoid distress sales.", "hi": "प्रमुख उपभोक्ता शहरों में आपूर्ति कम है। भाव बढ़ने की उम्मीद है; जल्दबाजी में औने-पौने दाम पर न बेचें।", "kn": "ಪ್ರಮುಖ ನಗರಗಳಲ್ಲಿ ಪೂರೈಕೆ ಕಡಿಮೆಯಾಗಿದೆ. ಬೆಲೆಗಳು ಹೆಚ್ಚಾಗುವ ನಿರೀಕ್ಷೆಯಿದೆ; ಆತುರದಲ್ಲಿ ಕಡಿಮೆ ಬೆಲೆಗೆ ಮಾರಬೇಡಿ.", "gu": "મુખ્ય શહેરોમાં પુરવઠો ઓછો છે. ભાવ વધવાની ધારણા છે; ઉતાવળમાં ઓછી કિંમતે વેચશો નહીં.", "mr": "मोठ्या शहरांमध्ये पुरवठा कमी आहे. भाव वाढण्याची शक्यता आहे; घाईगडबडीत कमी भावात विकू नका.", "ta": "முக்கிய நகரங்களில் வரத்து குறைவு. விலை உயர வாய்ப்புள்ளது; அவசரப்பட்டு குறைந்த விலைக்கு விற்க வேண்டாம்.", "te": "ప్రధాన నగరాల్లో సరఫరా తక్కువగా ఉంది. ధరలు పెరిగే అవకాశం ఉంది; తొందరపడి తక్కువ ధరకు అమ్మవద్దు.", "ml": "പ്രധാന നഗരങ്ങളിൽ വിതരണം കുറവാണ്. വില ഉയരാൻ സാധ്യതയുണ്ട്; തിടുക്കത്തിൽ കുറഞ്ഞ വിലയ്ക്ക് വിൽക്കരുത്.", "pa": "ਵੱਡੇ ਸ਼ਹਿਰਾਂ ਵਿੱਚ ਸਪਲਾਈ ਘੱਟ ਹੈ। ਮੁੱਲ ਵਧਣ ਦੀ ਉਮੀਦ ਹੈ; ਕਾਹਲੀ ਵਿੱਚ ਘੱਟ ਰੇਟ 'ਤੇ ਨਾ ਵੇਚੋ।", "bn": "প্রধান শহরগুলিতে সরবরাহ কম। দাম বাড়ার সম্ভাবনা রয়েছে; তাড়াহুড়ো করে কম দামে বিক্রি করবেন না।", "or": "ପ୍ରମୁଖ ସହରରେ ଯୋଗାଣ କମ୍ ଅଛି। ଦର ବଢ଼ିବାର ସମ୍ଭାବନା ଅଛି; ଶସ୍ତାରେ ବିକ୍ରୟ କରନ୍ତୁ ନାହିଁ।", "as": "প্ৰধান চহৰত যোগান কম। দাম বৃদ্ধিৰ আশা আছে; কম দামত বিক্ৰী নকৰিব।", "ks": "بڑے شہروں میں سپلائی کم ہے۔ قیمتیں بڑھنے کا امکان ہے؛ جلدی میں کم دام پر نہ بیچیں۔"}, "High perishable arrivals. Immediate sale recommended to minimize post-harvest loss.": {"en": "High perishable arrivals. Immediate sale recommended to minimize post-harvest loss.", "hi": "जल्दी खराब होने वाली फसल की भारी आवक। कटाई उपरांत नुकसान से बचने के लिए तुरंत बिक्री की सलाह।", "kn": "ಬೇಗ ಕೆಡುವ ಬೆಳೆಯ ಭಾರೀ ಆವಕ. ನಷ್ಟ ತಪ್ಪಿಸಲು ತಕ್ಷಣ ಮಾರಾಟ ಮಾಡಲು ಸಲಹೆ ನೀಡಲಾಗಿದೆ.", "gu": "નાશવંત પાકની ભારે આવક. નુકસાન ઘટાડવા માટે તાત્કાલિક વેચાણ કરવાની સલાહ છે.", "mr": "नाशवंत मालाची मोठी आवक. नुकसान टाळण्यासाठी तात्काळ विक्री करण्याचा सल्ला दिला जातो.", "ta": "அழுகக்கூடிய பயிர்களின் அதிக வரத்து. இழப்பைத் தவிர்க்க உடனடியாக விற்க பரிந்துரைக்கப்படுகிறது.", "te": "త్వరగా పాడయ్యే పంటల భారీ రాకలు. నష్టాన్ని నివారించడానికి వెంటనే అమ్మడం మంచిది.", "ml": "എളുപ്പം നശിക്കുന്ന വിളകളുടെ വൻ വരവ്. നഷ്ടം ഒഴിവാക്കാൻ ഉടനടി വിൽക്കാൻ ശുപാർശ ചെയ്യുന്നു.", "pa": "ਜਲਦੀ ਖਰਾਬ ਹੋਣ ਵਾਲੀ ਫ਼ਸਲ ਦੀ ਭਾਰੀ ਆਮਦ। ਨੁਕਸਾਨ ਤੋਂ ਬਚਣ ਲਈ ਤੁਰੰਤ ਵੇਚਣ ਦੀ ਸਲਾਹ ਹੈ।", "bn": "পচনশীল ফসলের বিপুল আমদানি। ক্ষতি এড়াতে অবিলম্বে বিক্রি করার পরামর্শ দেওয়া হচ্ছে।", "or": "ଶୀଘ୍ର ନଷ୍ଟ ହେଉଥିବା ଫସଲର ଅଧିକ ଆଗମନ। କ୍ଷତିରୁ ବଞ୍ଚିବା ପାଇଁ ତୁରନ୍ତ ବିକ୍ରୟ କରନ୍ତୁ।", "as": "পচনশীল শস্যৰ প্ৰচুৰ আগমন। লোকচান ৰোধ কৰিবলৈ তৎকালে বিক্ৰী কৰক।", "ks": "جلد خراب ہونے والی فصل کی بھاری آمد۔ نقصان سے بچنے کیلئے فوری فروخت کی سفارش ہے۔"}, "Good spot demand for clean lint. Stagger sales across coming fortnights.": {"en": "Good spot demand for clean lint. Stagger sales across coming fortnights.", "hi": "साफ रुई की अच्छी हाजिर मांग। आने वाले 2-3 हफ्तों में धीरे-धीरे बिक्री करें।", "kn": "ಸ್ವಚ್ಛ ಹತ್ತಿಗೆ ಉತ್ತಮ ಬೇಡಿಕೆ ಇದೆ. ಮುಂದಿನ ದಿನಗಳಲ್ಲಿ ಹಂತ-ಹಂತವಾಗಿ ಮಾರಾಟ ಮಾಡಿ.", "gu": "ચોખ્ખા કપાસની સારી માંગ છે. આગામી પખવાડિયામાં તબક્કાવાર વેચાણ કરો.", "mr": "स्वच्छ कापसाला चांगली मागणी आहे. पुढील काही आठवड्यांत टप्प्याटप्प्याने विक्री करा.", "ta": "தரமான பருத்திக்கு நல்ல தேவை உள்ளது. அடுத்தடுத்த வாரங்களில் பிரித்து விற்கவும்.", "te": "నాణ్యమైన పత్తికి మంచి డిమాండ్ ఉంది. రాబోయే వారాల్లో విడతలవారీగా విక్రయించండి.", "ml": "ശുദ്ധമായ പരുത്തിക്ക് നല്ല ഡിമാൻഡ്. വരും ആഴ്ചകളിൽ ഘട്ടം ഘട്ടമായി വിൽക്കുക.", "pa": "ਸਾਫ਼ ਕਪਾਹ ਦੀ ਚੰਗੀ ਮੰਗ ਹੈ। ਆਉਣ ਵਾਲੇ ਹਫ਼ਤਿਆਂ ਵਿੱਚ ਹੌਲੀ-ਹੌਲੀ ਵੇਚੋ।", "bn": "পরিষ্কার তুলার ভালো চাহিদা রয়েছে। আগামী সপ্তাহগুলিতে ধাপে ধাপে বিক্রি করুন।", "or": "ସଫା କପାର ଉତ୍ତମ ଚାହିଦା ରହିଛି। ଆଗାମୀ ସପ୍ତାହଗୁଡ଼ିକରେ ଧୀରେ ଧୀରେ ବିକ୍ରୟ କରନ୍ତୁ।", "as": "পৰিষ্কাৰ কপাহৰ ভাল চাহিদা। পৰৱৰ্তী সপ্তাহবোৰত লাহে লাহে বিক্ৰী কৰক।", "ks": "صاف روئی کی اچھی مانگ ہے۔ آنے والے ہفتوں میں قسط وار فروخت کریں۔"}, "Oil extraction demand high. Favorable market window for moisture-compliant pods.": {"en": "Oil extraction demand high. Favorable market window for moisture-compliant pods.", "hi": "तेल मिलों में पेराई की मांग अधिक है। उचित नमी वाली फलियों के लिए यह अच्छा भाव पाने का सही समय है।", "kn": "ಎಣ್ಣೆ ಗಿರಣಿಗಳಿಂದ ಹೆಚ್ಚಿನ ಬೇಡಿಕೆ ಇದೆ. ಸರಿಯಾದ ತೇವಾಂಶವಿರುವ ಕಾಯಿಗಳಿಗೆ ಉತ್ತಮ ಬೆಲೆ ಪಡೆಯಲು ಇದು ಸೂಕ್ತ ಸಮಯ.", "gu": "તેલ મિલોમાં પિલાણની માંગ વધારે છે. યોગ્ય ભેજવાળા માલ માટે સારો ભાવ મેળવવાનો આ યોગ્ય સમય છે.", "mr": "तेल गिरण्यांमध्ये गाळपाची मागणी जास्त आहे. योग्य ओलावा असलेल्या मालासाठी चांगला भाव मिळण्याची हीच वेळ आहे.", "ta": "எண்ணெய் ஆலைகளில் தேவை அதிகம். சரியான ஈரப்பதமுள்ள விளைபொருளுக்கு நல்ல விலை கிடைக்க இதுவே உகந்த நேரம்.", "te": "ఆయిల్ మిల్లుల్లో క్రషింగ్ డిమాండ్ ఎక్కువగా ఉంది. సరైన తేమ ఉన్న కాయలకు మంచి ధర పొందడానికి ఇది సరైన సమయం.", "ml": "എണ്ണ മില്ലുകളിൽ ഡിമാൻഡ് കൂടുതലാണ്. ശരിയായ ഈർപ്പമുള്ള വിളകൾക്ക് നല്ല വില ലഭിക്കാൻ ഇത് നല്ല സമയമാണ്.", "pa": "ਤੇਲ ਮਿੱਲਾਂ ਵਿੱਚ ਪਿੜਾਈ ਦੀ ਮੰਗ ਜ਼ਿਆਦਾ ਹੈ। ਸਹੀ ਨਮੀ ਵਾਲੀ ਫ਼ਸਲ ਲਈ ਚੰਗਾ ਰੇਟ ਲੈਣ ਦਾ ਇਹ ਸਹੀ ਸਮਾਂ ਹੈ।", "bn": "তেল মিলগুলিতে পেষাইয়ের চাহিদা বেশি। সঠিক আর্দ্রতার ফসলের জন্য ভালো দাম পাওয়ার এটাই সঠিক সময়।", "or": "ତୈଳ ମିଲ୍ ଚାହିଦା ଅଧିକ ଅଛି। ଉପଯୁକ୍ତ ଆର୍ଦ୍ରତା ଥିବା ଫସଲ ପାଇଁ ଉତ୍ତମ ଦର ପାଇବାର ଏହା ସଠିକ୍ ସମୟ।", "as": "তেল কলসমূহত পেৰাৰ চাহিদা বেছি। সঠিক আৰ্দ্ৰতা থকা শস্যৰ ভাল দাম পোৱাৰ এইটো উপযুক্ত সময়।", "ks": "تیل ملوں میں کرشنگ کی مانگ زیادہ ہے۔ مناسب نمی والی فصل کیلئے اچھا ریٹ حاصل کرنے کا صحیح وقت ہے۔"}, "Market demand is consistent. Recommend staggered weekly selling for best price realization.": {"en": "Market demand is consistent. Recommend staggered weekly selling for best price realization.", "hi": "बाजार में मांग निरंतर बनी हुई है। सर्वोत्तम मूल्य प्राप्ति के लिए साप्ताहिक अंतराल पर बिक्री की सलाह।", "kn": "ಮಾರುಕಟ್ಟೆ ಬೇಡಿಕೆ ಸ್ಥಿರವಾಗಿದೆ. ಉತ್ತಮ ಬೆಲೆ ಪಡೆಯಲು ವಾರಕ್ಕೊಮ್ಮೆ ಹಂತ-ಹಂತವಾಗಿ ಮಾರಾಟ ಮಾಡಲು ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ.", "gu": "બજારમાં માંગ સતત છે. શ્રેષ્ઠ ભાવ મેળવવા માટે સાપ્તાહિક તબક્કાવાર વેચાણ કરવાની ભલામણ છે.", "mr": "बाजारात मागणी कायम आहे. उत्तम दर मिळण्यासाठी आठवड्याला टप्प्याटप्प्याने विक्री करण्याचा सल्ला.", "ta": "சந்தை தேவை சீராக உள்ளது. சிறந்த விலையைப் பெற வாரந்தோறும் பிரித்து விற்க பரிந்துரைக்கப்படுகிறது.", "te": "మార్కెట్ డిమాండ్ స్థిరంగా ఉంది. ఉత్తమ ధర పొందడానికి వారానికోసారి విడతలవారీగా విక్రయించమని సిఫార్సు చేయబడింది.", "ml": "വിപണിയിലെ ഡിമാൻഡ് സ്ഥിരമാണ്. മികച്ച വില ലഭിക്കാൻ ആഴ്ചതോറും ഘട്ടം ഘട്ടമായി വിൽക്കാൻ ശുപാർശ ചെയ്യുന്നു.", "pa": "ਮੰਡੀ ਵਿੱਚ ਮੰਗ ਲਗਾਤਾਰ ਬਣੀ ਹੋਈ ਹੈ। ਵਧੀਆ ਰੇਟ ਲਈ ਹਫ਼ਤਾਵਾਰੀ ਹੌਲੀ-ਹੌਲੀ ਵੇਚਣ ਦੀ ਸਿਫਾਰਸ਼ ਹੈ।", "bn": "বাজারে চাহিদা স্থিতিশীল রয়েছে। সর্বোত্তম মূল্য পাওয়ার জন্য সাপ্তাহিক ধাপে ধাপে বিক্রি করার পরামর্শ।", "or": "ବଜାର ଚାହିଦା ସ୍ଥିର ରହିଛି। ଉତ୍ତମ ଦର ପାଇଁ ସାପ୍ତାହିକ ଭାବେ ଧୀରେ ଧୀରେ ବିକ୍ରୟ କରିବାକୁ ପରାମର୍ଶ।", "as": "বজাৰত চাহিদা সুস্থিৰ। উত্তম দাম পাবলৈ সাপ্তাহিক হিচাপত বিক্ৰী কৰাৰ পৰামৰ্শ।", "ks": "مارکیٹ میں مانگ مستحکم ہے۔ بہترین ریٹ پانے کیلئے ہفتہ وار قسطوں میں فروخت کریں۔"}, "Market demand is stable. Gradual staggered selling recommended.": {"en": "Market demand is stable. Gradual staggered selling recommended.", "hi": "बाजार मांग स्थिर है। धीरे-धीरे रुक-रुक कर बिक्री करने की सलाह दी जाती है।", "kn": "ಮಾರುಕಟ್ಟೆ ಬೇಡಿಕೆ ಸ್ಥಿರವಾಗಿದೆ. ಹಂತ-ಹಂತವಾಗಿ ಮಾರಾಟ ಮಾಡಲು ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ.", "gu": "બજારની માંગ સ્થિર છે. તબક્કાવાર વેચાણ કરવાની ભલામણ છે.", "mr": "बाजारातील मागणी स्थिर आहे. टप्प्याटप्प्याने विक्री करण्याचा सल्ला दिला जातो.", "ta": "சந்தை தேவை நிலையாக உள்ளது. படிப்படியாக விற்க பரிந்துரைக்கப்படுகிறது.", "te": "మార్కెట్ డిమాండ్ స్థిరంగా ఉంది. క్రమంగా విక్రయించమని సిఫార్సు చేయబడింది.", "ml": "വിപണിയിലെ ഡിമാൻഡ് സ്ഥിരമാണ്. ഘട്ടം ഘട്ടമായുള്ള വിൽപ്പന ശുപാർശ ചെയ്യുന്നു.", "pa": "ਮੰਡੀ ਦੀ ਮੰਗ ਸਥਿਰ ਹੈ। ਹੌਲੀ-ਹੌਲੀ ਵੇਚਣ ਦੀ ਸਿਫਾਰਸ਼ ਕੀਤੀ ਜਾਂਦੀ ਹੈ।", "bn": "বাজারের চাহিদা স্থিতিশীল। ধীরে ধীরে বিক্রি করার পরামর্শ দেওয়া হচ্ছে।", "or": "ବଜାର ଚାହିଦା ସ୍ଥିର ଅଛି। ଧୀରେ ଧୀରେ ବିକ୍ରୟ କରିବାକୁ ପରାମର୍ଶ।", "as": "বজাৰৰ চাহিদা সুস্থিৰ। লাহে লাহে বিক্ৰী কৰিবলৈ পৰামৰ্শ দিয়া হ'ল।", "ks": "مارکیٹ کی مانگ مستحکم ہے۔ آہستہ آہستہ فروخت کرنے کا مشورہ دیا جاتا ہے۔"}};

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
  const [locationTranslations, setLocationTranslations] = useState<{
    states: Record<string, Record<string, string>>;
    districts: Record<string, Record<string, string>>;
  }>(STATIC_LOCATIONS);

  // Helper: Format state display as "English (Native)" e.g. "Odisha (ଓଡ଼ିଶା)"
  const formatStateDisplay = (stateName: string, activeLang: string): string => {
    if (!stateName) return "";
    if (activeLang === "en") return stateName;
    const native = locationTranslations.states?.[stateName]?.[activeLang];
    if (native && native.toLowerCase() !== stateName.toLowerCase()) {
      return `${stateName} (${native})`;
    }
    return stateName;
  };

  // Helper: Format district display as "English (Native)" e.g. "Shivamogga (ಶಿವಮೊಗ್ಗ)"
  const formatDistrictDisplay = (districtName: string, activeLang: string): string => {
    if (!districtName) return "";
    if (activeLang === "en") return districtName;
    const native = locationTranslations.districts?.[districtName]?.[activeLang];
    if (native && native.toLowerCase() !== districtName.toLowerCase()) {
      return `${districtName} (${native})`;
    }
    return districtName;
  };

  // Helper: Format mandi display as "English (Native)" e.g. "Kantabaji APMC (କଣ୍ଟାବାଞ୍ଜି APMC)"
  const formatMandiDisplay = (mandiName: string, activeLang: string): string => {
    if (!mandiName) return "";
    if (activeLang === "en") return mandiName;
    
    // Check direct mandi name translation
    const directNative = locationTranslations.districts?.[mandiName]?.[activeLang];
    if (directNative && directNative.toLowerCase() !== mandiName.toLowerCase()) {
      return `${mandiName} (${directNative})`;
    }

    // Check if mandi prefix/town matches known district
    for (const [town, transMap] of Object.entries(locationTranslations.districts || {})) {
      if (mandiName.toLowerCase().startsWith(town.toLowerCase())) {
        const nativeTown = (transMap as Record<string, string>)[activeLang];
        if (nativeTown && nativeTown.toLowerCase() !== town.toLowerCase()) {
          const suffix = mandiName.substring(town.length);
          return `${mandiName} (${nativeTown}${suffix})`;
        }
      }
    }
    return mandiName;
  };

  // Helper: Format commodity display as "Native (English)" e.g. "ಕುಂಬಳಕಾಯಿ (Pumpkin)"
  const formatCommodityDisplay = (c: any, activeLang: string): string => {
    if (!c) return "";
    const eng = c.commodity_name || "";
    if (!eng) return "";
    if (activeLang === "en") return eng;

    let native = "";
    try {
      if (typeof c.local_name === "string") {
        const parsed = JSON.parse(c.local_name);
        native = parsed[activeLang] || "";
      } else if (typeof c.local_name === "object" && c.local_name !== null) {
        native = c.local_name[activeLang] || "";
      }
    } catch {}

    if (native && native.toLowerCase() !== eng.toLowerCase()) {
      return `${native} (${eng})`;
    }
    return eng;
  };

  // Helper: Format commodity name for card title as "Native (English)" e.g. "गेहूं (Wheat)"
  const formatCommodityTitle = (commodityName: string, activeLang: string): string => {
    if (!commodityName) return "";
    if (activeLang === "en") return commodityName;
    const found = commodities.find(c => c.commodity_name.toLowerCase() === commodityName.toLowerCase());
    if (found) {
      return formatCommodityDisplay(found, activeLang);
    }
    return commodityName;
  };

  // Helper: Format variety text in regional language e.g. "Sharbati (FAQ)" -> "शरबती (FAQ)"
  const formatVarietyText = (variety: string, activeLang: string): string => {
    if (!variety) return "";
    if (activeLang === "en") return variety;
    if (variety.toLowerCase().includes("sharbati")) {
      const transMap: Record<string, string> = {
        hi: "शरबती", kn: "ಶರಬತಿ", gu: "શરબતી", mr: "शरबती", ta: "சர்பதி", te: "శర్బతి",
        ml: "ശർബതി", pa: "ਸ਼ਰਬਤੀ", bn: "শরবতি", or: "ଶରବତୀ", as: "শৰবতী", ks: "شربتی"
      };
      const native = transMap[activeLang] || "Sharbati";
      return variety.replace(/Sharbati/i, native);
    }
    return variety;
  };

  // Helper: Format quality grade
  const formatGradeText = (grade: string, activeLang: string): string => {
    if (!grade) return "Grade A";
    if (activeLang === "en") return grade;
    const gradeMap: Record<string, string> = {
      hi: "ग्रेड ए", kn: "ಗ್ರೇಡ್ ಎ", gu: "ગ્રેડ એ", mr: "ग्रेड ए", ta: "தரம் ஏ",
      te: "గ్రేడ్ ఎ", ml: "ഗ്രേഡ് എ", pa: "ਗ੍ਰੇਡ ਏ", bn: "গ্রেড এ", or: "ଗ୍ରେଡ୍ ଏ", as: "গ্ৰেড এ", ks: "گریڈ اے"
    };
    return gradeMap[activeLang] || grade;
  };

  // Helper: Format trade auction type
  const formatTradeTypeText = (tradeType: string, activeLang: string): string => {
    if (!tradeType) tradeType = "e-Auction";
    if (activeLang === "en") return tradeType;
    if (tradeType.toLowerCase().includes("auction")) {
      const auctionMap: Record<string, string> = {
        hi: "ई-नीलामी", kn: "ಇ-ಹರಾಜು", gu: "ઈ-હરાજી", mr: "ई-लिलाव", ta: "மின்னணு ஏலம்",
        te: "ఇ-వేలం", ml: "ഇ-ലേലം", pa: "ਈ-ਨਿਲਾਮੀ", bn: "ই-নিলাম", or: "ଇ-ନିଲାମ", as: "ই-নিলাম", ks: "ای-نیلامی"
      };
      return auctionMap[activeLang] || tradeType;
    }
    return tradeType;
  };

  // Helper: Format source text e.g. "AGMARKNET (Cached Rates)"
  const formatSourceText = (source: string, activeLang: string): string => {
    if (!source) return "AGMARKNET";
    if (activeLang === "en") return source;
    let s = source;
    const cacheMap: Record<string, string> = {
      hi: "(कैश भाव)", kn: "(ಕ್ಯಾಶ್ ದರ)", gu: "(કેશ્ડ ભાવ)", mr: "(कॅश केलेले भाव)",
      ta: "(சேமிக்கப்பட்ட விலை)", te: "(కాష్ ధరలు)", ml: "(കാഷെ ചെയ്ത നിരക്കുകൾ)",
      pa: "(ਕੈਸ਼ਡ ਰੇਟ)", bn: "(ক্যাশে করা দর)", or: "(କ୍ୟାଚ୍ ଦର)", as: "(কেশ্ব কৰা দৰ)", ks: "(محفوظ شدہ ریٹ)"
    };
    const liveMap: Record<string, string> = {
      hi: "(लाइव सिंक)", kn: "(ಲೈವ್ ಸಿಂಕ್)", gu: "(લાઈવ સિંક)", mr: "(थेट सिंक)",
      ta: "(நேரலை ஒத்திசைவு)", te: "(ప్రత్యక్ష సమకాలీకరణ)", ml: "(തത്സമയ സമന്വയം)",
      pa: "(ਲਾਈਵ ਸਿੰਕ)", bn: "(লাইভ সিঙ্ক)", or: "(ଲାଇଭ୍ ସିଙ୍କ)", as: "(লাইভ চিঙ্ক)", ks: "(براہ راست مطابقت)"
    };
    if (s.includes("(Cached Rates)") && cacheMap[activeLang]) {
      s = s.replace("(Cached Rates)", cacheMap[activeLang]);
    }
    if (s.includes("(Synced Live)") && liveMap[activeLang]) {
      s = s.replace("(Synced Live)", liveMap[activeLang]);
    }
    return s;
  };

  // Helper: Format UPAg Supply Outlook
  const formatSupplyOutlook = (outlookText: string, activeLang: string): string => {
    if (!outlookText) return "";
    if (activeLang === "en") return outlookText;
    const clean = outlookText.trim();
    if (STATIC_SUPPLY_OUTLOOK[clean] && STATIC_SUPPLY_OUTLOOK[clean][activeLang]) {
      return STATIC_SUPPLY_OUTLOOK[clean][activeLang];
    }
    for (const [k, v] of Object.entries(STATIC_SUPPLY_OUTLOOK)) {
      if (k.toLowerCase() === clean.toLowerCase() && v[activeLang]) {
        return v[activeLang];
      }
    }
    return outlookText;
  };

  // Helper: Format UPAg Advisory Recommendation
  const formatAdvisoryRecommendation = (advText: string, activeLang: string): string => {
    if (!advText) return "";
    if (activeLang === "en") return advText;
    const clean = advText.trim();
    if (STATIC_ADVISORIES[clean] && STATIC_ADVISORIES[clean][activeLang]) {
      return STATIC_ADVISORIES[clean][activeLang];
    }
    for (const [k, v] of Object.entries(STATIC_ADVISORIES)) {
      if (k.toLowerCase() === clean.toLowerCase() && v[activeLang]) {
        return v[activeLang];
      }
    }
    return advText;
  };

  // Helper: Format UPAg Source Attribution
  const formatUpagSource = (src: string, activeLang: string): string => {
    if (!src) return "UPAg";
    if (activeLang === "en") return src;
    const upagSrcMap: Record<string, string> = {
      hi: "यूपीएजी (कृषि सांख्यिकी एकीकृत पोर्टल - DAFW/DoCA/CWWG)",
      kn: "ಯುಪಿಎಜಿ (ಕೃಷಿ ಅಂಕಿಅಂಶಗಳ ಏಕೀಕೃತ ಪೋರ್ಟಲ್ - DAFW/DoCA/CWWG)",
      gu: "યુપીએજી (કૃષિ આંકડા માટેનું સંકલિત પોર્ટલ - DAFW/DoCA/CWWG)",
      mr: "UPAg (कृषी सांख्यिकी एकात्मिक पोर्टल - DAFW/DoCA/CWWG)",
      ta: "UPAg (வேளாண் புள்ளிவிவரங்களுக்கான ஒருங்கிணைந்த போர்டல் - DAFW/DoCA/CWWG)",
      te: "UPAg (వ్యవసాయ గణాంకాల సమగ్ర పోర్టల్ - DAFW/DoCA/CWWG)",
      ml: "UPAg (കാർഷിക സ്ഥിതിവിവരക്കണക്കുകൾക്കായുള്ള ഏകീകൃത പോർട്ടൽ - DAFW/DoCA/CWWG)",
      pa: "UPAg (ਖੇਤੀਬਾੜੀ ਅੰਕੜਿਆਂ ਲਈ ਏਕੀਕ੍ਰਿਤ ਪੋਰਟਲ - DAFW/DoCA/CWWG)",
      bn: "UPAg (কৃষি পরিসংখ্যানের সমন্বিত পোর্টাল - DAFW/DoCA/CWWG)",
      or: "UPAg (କୃଷି ପରିସଂଖ୍ୟାନ ଏକୀକୃତ ପୋର୍ଟାଲ୍ - DAFW/DoCA/CWWG)",
      as: "UPAg (কৃষি পৰিসংখ্যাৰ একত্ৰিত পৰ্টেল - DAFW/DoCA/CWWG)",
      ks: "یو پی اے جی (زرعی اعداد و شمار کا مربوط پورٹل - DAFW/DoCA/CWWG)"
    };
    return upagSrcMap[activeLang] || src;
  };

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
  const activeAudioRef = useRef<HTMLAudioElement | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
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

  // Stop any active Bhashini audio or browser speech synthesis
  const stopAudio = () => {
    if (activeAudioRef.current) {
      activeAudioRef.current.pause();
      activeAudioRef.current = null;
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  };

  // Trigger Bhashini high-fidelity TTS voice synthesis with fallback to browser Web Speech
  const speakText = async (text: string) => {
    stopAudio();

    const monthsEn = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const monthsHi = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"];
    const monthsKn = ["ಜನವರಿ", "ಫೆಬ್ರವರಿ", "ಮಾರ್ಚ್", "ಏಪ್ರಿಲ್", "ಮೇ", "ಜೂನ್", "ಜುಲೈ", "ಆಗಸ್ಟ್", "ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್", "ನವೆಂಬರ್", "ಡಿಸೆಂಬರ್"];
    const monthsTa = ["ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்", "ஜூலை", "ஆகஸ்ட்", "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"];

    let monthList = monthsEn;
    if (lang === "hi") monthList = monthsHi;
    else if (lang === "kn") monthList = monthsKn;
    else if (lang === "ta") monthList = monthsTa;

    // Clean markdown formatting (*, #, •, bullet points, links) and naturalize dates
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

    // 1. Try Digital India Bhashini high-fidelity regional TTS via backend
    try {
      const res = await fetch(`${BACKEND_URL}/api/voice/synthesize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: cleanText, language: lang })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.audio_base64) {
          const audio = new Audio(`data:audio/wav;base64,${data.audio_base64}`);
          activeAudioRef.current = audio;
          await audio.play();
          return;
        }
      }
    } catch (e) {
      console.warn("Bhashini TTS synthesis fallback to browser Web Speech:", e);
    }

    // 2. Fallback to native Web Speech API
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(cleanText);
      const voiceLangs: Record<string, string> = {
        hi: "hi-IN", kn: "kn-IN", gu: "gu-IN", mr: "mr-IN",
        ta: "ta-IN", te: "te-IN", ml: "ml-IN", pa: "pa-IN", bn: "bn-IN",
        or: "or-IN", as: "as-IN", ks: "ur-IN", en: "en-IN"
      };
      utterance.lang = voiceLangs[lang] || "en-IN";
      utterance.rate = 0.95;
      utterance.pitch = 1.05;

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

    // Fetch location translations dictionary (States & Districts in 13 languages)
    fetch(`${BACKEND_URL}/api/translations/locations`)
      .then(res => res.json())
      .then(data => {
        if (data && data.states) {
          setLocationTranslations(data);
        }
      })
      .catch(err => console.warn("Failed to load location translations:", err));

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

    // Fetch Phase 5 UPAg Market Outlook & Advisory with selected language
    fetch(`${BACKEND_URL}/api/advisory/market-outlook?state=${encodeURIComponent(selectedState)}&commodity=${encodeURIComponent(selectedCommodity)}&lang=${lang}`)
      .then(res => res.json())
      .then(data => {
        setUpagOutlook(data.error ? null : data);
      })
      .catch(() => setUpagOutlook(null));
  }, [selectedMandi, selectedCommodity, selectedState, lang]);

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

  // Voice recording handler prioritizing browser Web Speech API for auto-silence detection & instant auto-send
  const toggleListening = async () => {
    stopAudio();

    if (isListening) {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch (e) {}
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        try { mediaRecorderRef.current.stop(); } catch (e) {}
      }
      setIsListening(false);
      return;
    }

    // 1. Primary: Browser Web Speech API (Auto-detects silence & auto-sends speech instantly without requiring second tap)
    const SpeechRecognition = typeof window !== "undefined" ? ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition) : None;
    if (SpeechRecognition) {
      try {
        setIsListening(true);
        const recognition = new SpeechRecognition();
        const speechLangs: Record<string, string> = {
          hi: "hi-IN", kn: "kn-IN", gu: "gu-IN", mr: "mr-IN",
          ta: "ta-IN", te: "te-IN", ml: "ml-IN", pa: "pa-IN", bn: "bn-IN",
          or: "or-IN", as: "as-IN", ks: "ur-IN", en: "en-IN"
        };
        recognition.lang = speechLangs[lang] || "en-IN";
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onresult = (event: any) => {
          setIsListening(false);
          const transcript = event.results[0]?.[0]?.transcript;
          if (transcript && transcript.trim()) {
            handleAssistantSend(transcript.trim());
          }
        };

        recognition.onerror = (err: any) => {
          console.warn("SpeechRecognition error:", err);
          setIsListening(false);
        };
        
        recognition.onend = () => {
          setIsListening(false);
        };

        recognitionRef.current = recognition;
        recognition.start();
        return;
      } catch (err) {
        console.warn("Web Speech API start error, falling back to MediaRecorder:", err);
      }
    }

    // 2. Secondary Fallback: MediaRecorder for browsers without native Web Speech API (e.g. Firefox)
    if (typeof navigator !== "undefined" && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          setIsListening(false);
          stream.getTracks().forEach(track => track.stop());

          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
          if (audioBlob.size > 0) {
            try {
              const reader = new FileReader();
              reader.readAsDataURL(audioBlob);
              reader.onloadend = async () => {
                const base64Audio = reader.result as string;
                const res = await fetch(`${BACKEND_URL}/api/voice/transcribe`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ audio: base64Audio, language: lang, mime_type: "audio/wav" })
                });
                if (res.ok) {
                  const data = await res.json();
                  if (data.text && data.text.trim()) {
                    handleAssistantSend(data.text.trim());
                  }
                }
              };
            } catch (err) {
              console.error("Transcribe error:", err);
            }
          }
        };

        setIsListening(true);
        mediaRecorder.start();
        
        // Auto-stop after 6 seconds if user forgets to tap stop
        setTimeout(() => {
          if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
            mediaRecorderRef.current.stop();
          }
        }, 6000);
        return;
      } catch (err) {
        console.warn("Microphone getUserMedia not available:", err);
      }
    }

    setIsListening(false);
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
                          onClick={stopAudio} 
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
                  {states.map(s => <option key={s} value={s}>{formatStateDisplay(s, lang)}</option>)}
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
                    {districts.map(d => <option key={d} value={d}>{formatDistrictDisplay(d, lang)}</option>)}
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
                    {mandis.map(m => <option key={m.id} value={m.mandi_name}>{formatMandiDisplay(m.mandi_name, lang)}</option>)}
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
                  {commodities.map(c => (
                    <option key={c.id} value={c.commodity_name}>
                      {formatCommodityDisplay(c, lang)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Results Grid */}
            {priceData && (
              <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-extrabold text-lg text-primary-700">{formatCommodityTitle(priceData.commodity, lang)}</h3>
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      <MapPin size={12} /> {formatMandiDisplay(priceData.mandi, lang)}
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
                      <span>{t.arrivals || "Daily Arrivals"}: <strong className="font-extrabold text-amber-950">{priceData.arrivals_qty} {t.qtl || "Qtl"}</strong></span>
                    </div>
                    <div className="flex items-center gap-2">
                      {priceData.variety && (
                        <span className="bg-white/90 px-2 py-0.5 rounded border border-amber-300 text-[11px] font-bold text-gray-800">
                          {t.variety_grade || "Variety"}: {formatVarietyText(priceData.variety, lang)} ({formatGradeText(priceData.grade, lang)})
                        </span>
                      )}
                      <span className="bg-green-100 text-green-800 text-[10px] font-extrabold px-2 py-0.5 rounded uppercase">
                        {formatTradeTypeText(priceData.trade_type, lang)}
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
                      <span>{t.source_label || "Source"}: {formatSourceText(priceData.source, lang)}</span>
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
                        {formatSupplyOutlook(upagOutlook.supply_outlook, lang)}
                      </span>
                    </div>

                    {/* Retail vs Wholesale Spread Bar */}
                    <div className="bg-white p-2.5 rounded-lg border border-blue-100/90 shadow-xs space-y-2">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-bold text-gray-700">{t.retail_spread_label || "Wholesale vs Consumer Retail Spread"}:</span>
                        <span className="font-extrabold text-indigo-700 bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded">
                          +{upagOutlook.retail_spread_pct}% {t.retail_margin || "Retail Margin"}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-center pt-1">
                        <div className="bg-gray-50 p-2 rounded">
                          <p className="text-[10px] text-gray-500 font-bold uppercase">{t.apmc_wholesale_rate || "APMC Wholesale Rate"}</p>
                          <p className="font-bold text-sm text-gray-800">₹{upagOutlook.wholesale_price_avg}/{t.unit_kg || "kg"}</p>
                        </div>
                        <div className="bg-indigo-50/60 p-2 rounded border border-indigo-100">
                          <p className="text-[10px] text-indigo-700 font-bold uppercase">{t.city_retail_rate || "City Retail (DoCA)"}</p>
                          <p className="font-bold text-sm text-indigo-950">₹{upagOutlook.retail_price_avg}/{t.unit_kg || "kg"}</p>
                        </div>
                      </div>
                    </div>

                    {/* Climate & Actionable Strategic Recommendation */}
                    <div className="bg-amber-50/90 border-l-4 border-amber-500 p-2.5 rounded-r-lg text-xs space-y-1">
                      <p className="font-extrabold text-amber-950 flex items-center gap-1">
                        <span>💡</span> {t.advisory_label || "Strategic Farmer Advisory"}:
                      </p>
                      <p className="text-amber-900 font-medium text-[11px] leading-relaxed">
                        {formatAdvisoryRecommendation(upagOutlook.advisory_recommendation, lang)}
                      </p>
                      <div className="mt-1.5 text-[10px] text-gray-500 flex justify-between items-center border-t border-amber-200/60 pt-1">
                        <span>🌧️ {t.cwwg_rainfall || "CWWG Rainfall"}: {upagOutlook.rainfall_departure_pct}% ({t.reservoir || "Reservoir"}: {upagOutlook.reservoir_storage_pct}%)</span>
                        <span className="italic">{formatUpagSource(upagOutlook.source, lang)}</span>
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
      <div className="bg-gray-100 text-[10px] text-gray-500 text-center py-1.5 px-3 border-t border-gray-200 flex flex-wrap items-center justify-center gap-x-2 gap-y-0.5">
        <Link href="/about" className="hover:text-primary-600 hover:underline">About</Link>
        <span>•</span>
        <Link href="/acknowledgements" className="hover:text-primary-600 hover:underline">Govt Acknowledgements</Link>
        <span>•</span>
        <Link href="/terms" className="hover:text-primary-600 hover:underline">Terms & Conditions</Link>
        <span>•</span>
        <a href="mailto:support@crestsubarn.com" className="hover:text-primary-600 hover:underline">support@crestsubarn.com</a>
        <div className="w-full text-[9px] text-gray-400 mt-0.5">
          © 2026 Crestsubarn. All rights reserved.
        </div>
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
