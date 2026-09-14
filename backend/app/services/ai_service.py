import os
import json
import re
import requests
from typing import Dict, Any, Optional

# Comprehensive Indic Unicode script blocks (including Odia, Bengali/Assamese, and Perso-Arabic/Kashmiri)
LANG_PATTERNS = {
    "gu": re.compile(r"[઀-૿]"), # Gujarati
    "or": re.compile(r"[଀-୿]"), # Odia
    "ta": re.compile(r"[஀-௿]"), # Tamil
    "te": re.compile(r"[ఀ-౿]"), # Telugu
    "kn": re.compile(r"[ಀ-೿]"), # Kannada
    "ml": re.compile(r"[ഀ-ൿ]"), # Malayalam
    "pa": re.compile(r"[਀-੿]"), # Gurmukhi / Punjabi
    "devanagari": re.compile(r"[ऀ-ॿ]"), # Hindi / Marathi / Kashmiri Devanagari
    "perso_arabic": re.compile(r"[؀-ۿ]") # Kashmiri / Urdu
}

# Distinctive Assamese letters vs Bengali (both share base Eastern Nagari ঀ-৿)
ASSAMESE_CHARS = re.compile(r"[ৰৱ]") # Assamese unique 'ৰ' (Ra) and 'ৱ' (Va)
ASSAMESE_MARKERS = ["আহে", "নাই", "আছে", "দৰ", "দাম", "কিমান", "গুৱাহাটী", "কওক", "শস্য", "কৃষক", "বিক্ৰী", "আলুৰ", "ধানৰ", "চাহৰ", "ৰেট", "প্ৰাইচ"]

# Distinctive Kashmiri markers (Perso-Arabic and phonetics)
KASHMIRI_MARKERS = [
    "چُھ", "چھ", "ہُنٛد", "قٟمَتھ", "مَنٛز", "ژوٗنٛٹھ", "کٲشُر", "پرِژھِو", "کِتھ", "سوزِو", "باپتھ", 
    "سری نگر", "سوپور", "کونٛگ", "ڈوٗن", "گَنَم", "دانۍ", "آلوٚو", "گنڈٕ", "tsoonth", "sopore", "koshur", "kashmiri", "ریٹ"
]

# Distinctive Marathi markers (excluding words shared with Hindi like 'भाव' or 'दर')
MARATHI_MARKERS = ["आहे", "नाही", "काय", "शेतकरी", "कांदा", "बटाटा", "गहू", "पिक", "कसा", "करा", "बाजारभाव", "बाजार समिती", "पुण्यात", "नाशिकमध्ये"]

# Enhanced Colloquial Transliterated Markers for Code-Mixed / Romanized Indian queries
COLLOQUIAL_LANG_MARKERS = {
    "or": [r"\bkete\b", r"\bdara\b", r"\bkana\b", r"\bachhi\b", r"\bre\b", r"\bau\b", r"\btanka\b", r"\bdhanara\b", r"\baloora\b", r"\bpiajara\b", r"\bgahamara\b"],
    "as": [r"\bkiman\b", r"\bdora\b", r"\bdaam\b", r"\baase\b", r"\bte\b", r"\bkiya\b", r"\blagibo\b", r"\bkobo\b", r"\bdhanar\b", r"\baalur\b"],
    "bn": [r"\bkoto\b", r"\bdaam\b", r"\bache\b", r"\bhobe\b", r"\bdorkar\b", r"\bbolun\b", r"\bdhaner\b", r"\baluer\b"],
    "kn": [r"\beshtu\b", r"\byestu\b", r"\bdalli\b", r"\balli\b", r"\bide\b", r"\benu\b", r"\bbeku\b", r"\bagide\b", r"\bhege\b", r"\bkodri\b"],
    "mr": [r"\bkiti\b", r"\bahe\b", r"\bkay\b", r"\bmadhye\b", r"\bkasa\b", r"\bsang\b", r"\bpahije\b", r"\bvikane\b", r"\bkandacha\b"],
    "gu": [r"\bsu che\b", r"\bketla\b", r"\bketlo\b", r"\bche\b", r"\bnathi\b", r"\baapo\b", r"\bjovo\b", r"\bma\b"],
    "te": [r"\benta\b", r"\bundi\b", r"\bkavali\b", r"\bela\b", r"\bundhi\b", r"\bcheppandi\b", r"\bdharalu\b"],
    "ta": [r"\bevvalavu\b", r"\birukku\b", r"\bvenum\b", r"\beppadi\b", r"\bsollunga\b", r"\bvilai\b"],
    "ml": [r"\bethra\b", r"\bund\b", r"\bvenam\b", r"\bengane\b", r"\bparayoo\b", r"\bvila\b"],
    "pa": [r"\bkinna\b", r"\bkine\b", r"\bchahida\b", r"\bdasso\b", r"\bbhava\b"],
    "ks": [r"\bkyah chu\b", r"\bmanz\b", r"\bkati\b", r"\bwaniv\b", r"\bbaaputh\b"],
    "hi": [r"\bkya hai\b", r"\bkitna hai\b", r"\bkitna\b", r"\bkaisa\b", r"\bbatao\b", r"\bchahiye\b", r"\bmein\b", r"\bhoga\b"]
}

INDIC_SUFFIXES = [
    # Odia
    "ରେ", "ର", "କୁ", "ଠାରୁ", "ବାଲା",
    # Assamese / Bengali
    "ৰ", "র", "ত", "তে", "ৰপৰା", "ৰবাবে",
    # Devanagari (Hindi / Marathi)
    "मध्ये", "च्या", "चे", "ची", "चा", "ला", "त", "तील", "का", "की", "के", "में", "से", "वाला", "वाली",
    # Gujarati
    "માં", "નો", "ની", "નું", "ના", "વાળા",
    # Kannada
    "ನಲ್ಲಿ", "ದಲ್ಲಿ", "ಯಲ್ಲಿ", "ದ", "ಯ", "ಗೆ", "ಯಿಂದ",
    # Telugu
    "లో", "కి", "కు", "యొక్క", "నుండి",
    # Tamil
    "இல்", "க்கு", "உடைய", "இருந்து"
]

ROMAN_SUFFIXES = [
    # Multi-char suffixes first
    "madhye", "dalli", "alli", "mein", "wala", "wali", "are", "ara",
    # 2-char suffixes
    "re", "ra", "ar", "er", "ro", "cha", "chi", "che", "no", "ni", "nu", "na",
    "da", "ya", "lo", "la", "il", "te", "ka", "ki", "ke", "me", "se"
]

def strip_word_suffixes(w: str) -> list:
    """Return token itself plus stemmed variants with common Indian case suffixes stripped"""
    variants = [w]
    w_lower = w.lower()
    for sfx in ROMAN_SUFFIXES:
        if w_lower.endswith(sfx) and len(w_lower) > len(sfx) + 2:
            variants.append(w_lower[:-len(sfx)])
            break
    for sfx in INDIC_SUFFIXES:
        if w.endswith(sfx) and len(w) > len(sfx) + 1:
            variants.append(w[:-len(sfx)])
            break
    return variants

COMMODITY_KEYWORDS = {
    "Apple": ["apple", "apples", "seb", "sebu", "safarjan", "tsoonth", "tsunth", "aapil", "sewa", "seo", "सेब", "ಸೇಬು", "સફરજન", "सफरचंद", "ஆப்பிள்", "ఆపిల్", "ആപ്പിൾ", "ਸੇਬ", "আপেল", "ସେଓ", "আপেল", "ژوٗنٛٹھ", "سیب"],
    "Saffron": ["saffron", "kesar", "kong", "zafran", "kongh", "केसर", "ಕೇಸರಿ", "केशर", "குங்குமப்பூ", "కుంకుమపువ్వు", "കുങ്കുമപ്പൂവ്", "કેસર", "ਕੇਸਰ", "জাফরান", "ଜାଫ୍ରାନ", "জাফ্ৰান", "کونٛگ", "زعفران"],
    "Walnut": ["walnut", "walnuts", "akhrot", "doon", "dhoon", "अखरोट", "ಅಕ್ರೋಟು", "अक्रोड", "அக்ரூட்", "అక్రోట్లను", "അക്രൂട്ട്", "અખરોટ", "ਅਖਰੋਟ", "আখরোট", "ଅଖରୋଟ", "আখৰোট", "ڈوٗن"],
    "Tea": ["tea", "chai", "chah", "chaha", "cha", "চাহ", "চা", "ଚା", "चाय", "ಚಹಾ", "चहा", "தேநீர்", "టీ", "ചായ", "ચા", "ਚਾਹ", "چائے"],
    "Banana": ["banana", "bananas", "kela", "kele", "keli", "kadali", "balehannu", "valaippazham", "arati", "aratipandu", "kol", "kelaa", "केला", "ಬಾಳೆಹಣ್ಣು", "કેળાં", "કેળા", "केळी", "வாழைப்பழம்", "అరటిపండు", "വാഴപ്പഴം", "ਕੇਲਾ", "কলা", "କଦଳୀ", "কল", "کیٚل"],
    "Mango": ["mango", "mangoes", "aam", "keri", "amba", "mavina", "mavina hannu", "mambazham", "mamidi", "mamidipandu", "aambo", "aamra", "आम", "ಮಾವಿನಹಣ್ಣು", "કેરી", "आंबा", "மாம்பழம்", "మామిడిపండు", "അമ്പഴം", "ਅੰਬ", "আম", "ଆମ୍ବ", "আম", "آم"],
    "Potato": ["potato", "potatoes", "aloo", "aalu", "alu", "aluro", "aloora", "aalur", "batata", "batate", "aalugadde", "urulaikizhangu", "bangaladumpa", "aaloov", "आलू", "ಆಲೂಗಡ್ಡೆ", "બટાકા", "બટાટા", "बटाटा", "உருளைக்கிழங்கு", "బంగాళாదుంప", "ഉരുളക്കിഴങ്ങ്", "ਆਲੂ", "আলু", "ଆଳୁ", "আলু", "আলুৰ", "ଆଳୁର", "آلوٚو"],
    "Onion": ["onion", "onions", "pyaz", "pyaaz", "kanda", "kande", "kandya", "dungri", "dungli", "eerulli", "erulli", "ullipaya", "vengayam", "savala", "piaja", "piaza", "piajara", "pyaja", "gande", "प्याज", "कांदा", "कांद्या", "ಈರುಳ್ಳಿ", "ડુંગળી", "வெங்காயம்", "ఉల్లిపాయ", "സவாള", "ਪਿਆਜ਼", "পেঁয়াজ", "ପିଆଜ", "ପିଆଜର", "পিয়াঁজ", "گنڈٕ"],
    "Tomato": ["tomato", "tomatoes", "tamatar", "tameta", "tamate", "tamota", "thakkali", "bilati", "bilati baigan", "bilati baigana", "bilahi", "टमाटर", "ಟೊಮೆಟೊ", "ટામેટાં", "ટામેટા", "टोमॅटो", "தக்காளி", "టమోటా", "തக்காളി", "ਟਮਾਟਰ", "টমেটো", "ବିଲାତି", "ବିଲାତି ବାଇଗଣ", "বিলাহী", "ٹماٹَر"],
    "Wheat": ["wheat", "gehun", "gehu", "kanak", "ghau", "godhi", "godhumai", "godhumalu", "gahama", "gahamara", "gaham", "ganam", "गेहूं", "कनक", "ಗೋಧಿ", "ઘઉં", "गहू", "கோதுமை", "గోధుమలు", "ഗോതമ്പ്", "ਕਣਕ", "গম", "ଗହମ", "ଗହମର", "গম", "گَنَم"],
    "Paddy (Rice)": ["paddy", "rice", "chawal", "dhan", "dhana", "dhanara", "dhanar", "dhaner", "chaula", "chaul", "chaular", "bhatta", "daani", "tandula", "akki", "nellu", "vari", "jhona", "धान", "चावल", "ಚಾವಲ್", "ಭತ್ತ", "ರೈಸ್", "ડાંગર", "भात", "நெல்", "వరి", "നെല്ല്", "ਝੋਨਾ", "ধান", "ଧାନ", "ଧାନର", "ধানৰ", "চাউল", "ଚାଉଳ", "دانۍ"],
    "Maize": ["maize", "corn", "makka", "makai", "makaai", "jola", "mekkejola", "makka jola", "maka", "bhutta", "makaa", "makoi", "मक्का", "ಮಕ್ಕೆಜೋಳ", "ಮೆಕ್ಕೆಜೋಳ", "ಮಕ್ಕ ಜೋಳ", "ಜೋಳ", "મકાઈ", "मका", "ಮಕ್ಕாச்சோளம்", "మొక్కజొన్న", "ചോളം", "ਮੱਕੀ", "ভুট্টা", "ମକା", "ମକାର", "মাকৈ", "مکٲئی"],
    "Cotton": ["cotton", "kapas", "kapus", "patti", "hatti", "paruthi", "kapa", "kapaha", "kapahar", "कपास", "हत्ती", "ಹತ್ತಿ", "કપાસ", "कापूस", "பருத்தி", "పత్తి", "പരുத்தி", "ਕਪਾਹ", "তুলা", "କପା", "କପାର", "কপাহ", "کَپَس"],
    "Groundnut": ["groundnut", "peanut", "mungfali", "moongfali", "magfali", "bhuimug", "kadalekayi", "kadalekai", "verukadalai", "verusanaga", "nilakkadala", "chinabadam", "badam", "मूंगफली", "ಕಡಲೆಕಾಯಿ", "મગફળી", "भुईमूग", "வேர்க்கடலை", "వేరుశనగ", "നിലക്കടല", "ਮੂੰਗਫਲੀ", "চীনাবাদাম", "ଚିନାବାଦାମ", "বাদাম", "موٗنٛگ پھَلی"],
    "Soyabean": ["soyabean", "soybean", "soya", "सोयाबीन", "ಸೋಯಾಬೀನ್", "સોયાબીન", "சோயாபீன்", "సోయాబీన్", "ସୋୟାବିନ", "ছয়াবিন", "سویا بین"],
    "Toor Dal": ["toor dal", "toor", "tur", "arhar", "arhar dal", "tuver", "togari bele", "togari", "kandi pappu", "kandi", "harada", "harada dali", "rohor dail", "তুৰ", "തുവര", "तुअर", "अरहर", "ತೊಗರಿ ಬೇಳೆ", "ತೊಗರಿ", "તુર દાળ", "તૂવેર", "तूर डाळ", "துவரம் பருப்பு", "కందిపప్పు", "ହରଡ ଡାଲି", "ହରଡ", "ৰহৰ দাইল", "تُوٗر دال"],
    "Gram (Chana)": ["gram", "chana", "kadale", "kadale bele", "sanagalu", "senagalu", "harbhara", "kondaikkadalai", "kadala", "chhole", "buta", "boot", "चना", "ಕಡಲೆ", "ಕಡಲೆ ಬೇಳೆ", "ચણા", "हरभरा", "கொண்டைக்கடலை", "శనగలు", "കടല", "ਛੋਲੇ", "ছোলা", "ବୁଟ", "বুট", "چَنہٕ"],
    "Cumin (Jeera)": ["jeera", "cumin", "jiru", "jira", "jeerige", "seeragam", "jeelakarra", "jire", "జీలకర్ర", "जीरा", "ಜೀರಿಗೆ", "જીરું", "जिरे", "சீரகம்", "జీలకర్ర", "ਜੀਰਾ", "জিরে", "ଜିରା", "জীৰা", "زیوٗر"],
    "Sunflower": ["sunflower", "sunflowers", "surajmukhi", "sooryamukhi", "suraj mukhi", "सूरजमुखी", "સૂર્યમુખી", "ସୂର୍ଯ୍ୟମୁଖୀ", "সূর্যমুখী", "সূৰ্যমুখী", "ಸೂರ್ಯಕಾಂತಿ", "సూర్యముఖి", "சூரியகாந்தி", "سورج مکھی", "سُورج مۆکھی", "ਸੂਰਜਮੁਖੀ", "സൂര്യകാന്തി", "सूर्यफूल"],
    "Mustard": ["mustard", "sarson", "rai", "sasive", "kadugu", "avalu", "sorisa", "xoriyo", "सरसों", "राई", "સરસવ", "રાઈ", "ಸಾಸಿವೆ", "கடுகு", "ఆవాలు", "കടുക്", "ਸਰ੍ਹੋਂ", "সর্ষে", "ସୋରିଷ", "সৰিয়হ", "آسُر"],
    "Sugarcane": ["sugarcane", "ganna", "kabbu", "karumbu", "cheruku", "akhu", "गन्ना", "શેરડી", "ಕಬ್ಬು", "கரும்பு", "చెరకు", "കരിമ്പ്", "ਗੰਨਾ", "আখ", "ଆଖୁ", "কুঁহিয়াৰ", "گنٕ"],
    "Barley": ["barley", "jowar", "bajra", "jau", "ragi", "millet", "millets", "बाजरी", "ज्वारी", "બાજરી", "જુવાર", "ଜୋୱାର", "ମାଣ୍ଡିଆ", "বাঁজৰা", "باجرٕ"],
    "Coffee": ["coffee", "kafi", "kapi", "कॉफी", "ಕಾಫಿ", "காபி", "కాఫీ", "কফি", "କଫି", "کافی"],
    "Turmeric": ["turmeric", "haldi", "pasupu", "manjal", "halad", "arishina", "haridra", "haladhi", "haladi", "हल्दी", "ಅರಿಶಿನ", "હળદર", "हळद", "மஞ்சள்", "పసుపు", "മഞ്ഞൾ", "ਹਲਦੀ", "হলুদ", "ହଳଦୀ", "হালধি", "لَدٕر"]
}

LOCATION_KEYWORDS = {
    # Jammu & Kashmir
    "Sopore": {"district": "Baramulla", "state": "Jammu and Kashmir", "keywords": ["sopore", "baramulla", "سوپور", "بارہمولہ", "सोपोर"]},
    "Srinagar": {"district": "Srinagar", "state": "Jammu and Kashmir", "keywords": ["srinagar", "parimpora", "سری نگر", "پرِم پورہ", "श्रीनगर"]},
    "Jammu": {"district": "Jammu", "state": "Jammu and Kashmir", "keywords": ["jammu", "narwal", "جموں", "نروال", "जम्मू"]},
    
    # Odisha
    "Bhubaneswar": {"district": "Khordha", "state": "Odisha", "keywords": ["bhubaneswar", "khordha", "ଭୁବନେଶ୍ୱର", "ଖୋର୍ଦ୍ଧା", "भुवनेश्वर"]},
    "Cuttack": {"district": "Cuttack", "state": "Odisha", "keywords": ["cuttack", "chhatrabazar", "କଟକ", "ଛତ୍ରବଜାର", "कटक"]},
    "Sambalpur": {"district": "Sambalpur", "state": "Odisha", "keywords": ["sambalpur", "khetrajpur", "ସମ୍ବଲପୁର", "ଖେତରାଜପୁର", "संबलपुर"]},
    
    # Assam
    "Guwahati": {"district": "Kamrup Metropolitan", "state": "Assam", "keywords": ["guwahati", "gauhati", "kamrup", "pamohi", "গুৱাহাটী", "গুৱাহাটীত", "কামৰূপ", "गुवाहाटी"]},
    "Silchar": {"district": "Cachar", "state": "Assam", "keywords": ["silchar", "cachar", "শিলচৰ", "কাছাৰ", "सिलचर"]},
    "Jorhat": {"district": "Jorhat", "state": "Assam", "keywords": ["jorhat", "যোৰহাট", "जोरहाट"]},

    # Gujarat
    "Ahmedabad": {"district": "Ahmedabad", "state": "Gujarat", "keywords": ["ahmedabad", "amdavad", "અમદાવાદ", "અહમદાબાદ", "अहमदाबाद", "chimanbhai", "jamalpur"]},
    "Surat": {"district": "Surat", "state": "Gujarat", "keywords": ["surat", "સુરત", "सूरत"]},
    "Rajkot": {"district": "Rajkot", "state": "Gujarat", "keywords": ["rajkot", "રાજકોટ", "राजकोट"]},
    "Gondal": {"district": "Rajkot", "state": "Gujarat", "keywords": ["gondal", "ગોંડલ", "ગोंડલ"]},
    "Vadodara": {"district": "Vadodara", "state": "Gujarat", "keywords": ["vadodara", "baroda", "વડોદરા", "वडोदरा"]},
    "Anand": {"district": "Anand", "state": "Gujarat", "keywords": ["anand", "આણંદ", "आनंद"]},
    "Mehsana": {"district": "Mehsana", "state": "Gujarat", "keywords": ["mehsana", "unjha", "મહેસાણા", "ઊંઝા", "ऊंझा"]},
    
    # Karnataka
    "Shivamogga": {"district": "Shivamogga", "state": "Karnataka", "keywords": ["shimoga", "shivamogga", "ಶಿವಮೊಗ್ಗ", "शिवमोग्गा", "शिमोगा"]},
    "Davanagere": {"district": "Davanagere", "state": "Karnataka", "keywords": ["davanagere", "ದಾವಣಗೆರೆ", "दावणगेरे"]},
    "Bengaluru": {"district": "Bengaluru", "state": "Karnataka", "keywords": ["bengaluru", "bangalore", "ಬೆಂಗಳೂರು", "yeshwanthpur", "बेंगलुरु"]},
    "Hubli": {"district": "Dharwad", "state": "Karnataka", "keywords": ["hubli", "hubballi", "ಹುಬ್ಬಳ್ಳಿ", "हुबली"]},
    "Mysuru": {"district": "Mysuru", "state": "Karnataka", "keywords": ["mysore", "mysuru", "ಮೈಸೂರು", "मैसूर"]},
    
    # Maharashtra
    "Nashik": {"district": "Nashik", "state": "Maharashtra", "keywords": ["lasalgaon", "nashik", "नाशिक", "लासलगाव"]},
    "Pune": {"district": "Pune", "state": "Maharashtra", "keywords": ["pune", "पुणे", "पुण्या", "gultekdi"]},
    "Mumbai": {"district": "Mumbai Suburban", "state": "Maharashtra", "keywords": ["vashi", "mumbai", "नवी मुंबई", "वाशी", "मुंबई"]},
    "Nagpur": {"district": "Nagpur", "state": "Maharashtra", "keywords": ["nagpur", "नागपूर", "नागपुर"]},
    
    # Madhya Pradesh
    "Indore": {"district": "Indore", "state": "Madhya Pradesh", "keywords": ["indore", "इंदौर", "choithram"]},
    "Ujjain": {"district": "Ujjain", "state": "Madhya Pradesh", "keywords": ["ujjain", "उज्जैन"]},
    "Bhopal": {"district": "Bhopal", "state": "Madhya Pradesh", "keywords": ["bhopal", "भोपाल"]},
    
    # Tamil Nadu & South
    "Chennai": {"district": "Chennai", "state": "Tamil Nadu", "keywords": ["chennai", "koyambedu", "சென்னை", "கோயம்பேடு", "చెన్నై"]},
    "Coimbatore": {"district": "Coimbatore", "state": "Tamil Nadu", "keywords": ["coimbatore", "கோவை", "கோயம்புத்தூர்"]},
    "Hyderabad": {"district": "Hyderabad", "state": "Telangana", "keywords": ["hyderabad", "bowenpally", "హైదరాబాద్", "हैदराबाद"]},
    "Guntur": {"district": "Guntur", "state": "Andhra Pradesh", "keywords": ["guntur", "గుంటూరు"]},
    
    # North & East
    "Kolkata": {"district": "Kolkata", "state": "West Bengal", "keywords": ["kolkata", "calcutta", "কলকাতা", "কলিকাতা", "কোলকাতা"]},
    "Delhi": {"district": "North Delhi", "state": "Delhi", "keywords": ["delhi", "azadpur", "दिल्ली", "आजादपुर", "ଦିଲ୍ଲୀ", "ದೆಹಲಿ", "દિલ્હી", "டெல்லி", "ఢిల్లీ", "দিল্লী", "দিল্লি", "ਦਿੱਲੀ", "ഡൽഹി", "دِہلی"]},
    "Jaipur": {"district": "Jaipur", "state": "Rajasthan", "keywords": ["jaipur", "muhana", "जयपुर"]},
    "Lucknow": {"district": "Lucknow", "state": "Uttar Pradesh", "keywords": ["lucknow", "dubagga", "लखनऊ"]},
    "Khanna": {"district": "Ludhiana", "state": "Punjab", "keywords": ["khanna", "ludhiana", "ਖੰਨਾ", "ਲੁਧਿਆਣਾ", "खन्ना"]}
}

UNIVERSAL_PRICE_STOPWORDS = {
    # English
    "what", "is", "the", "rate", "of", "price", "cost", "bhav", "in", "at", "for", "near", 
    "today", "todays", "today's", "tomorrow", "yesterday", "current", "mandi", "market", 
    "apmc", "crop", "crops", "commodity", "commodities", "please", "tell", "me", "show", 
    "give", "check", "how", "much", "and", "a", "an", "daily", "rates", "prices",
    # Hindi / Marathi
    "क्या", "है", "हैं", "का", "की", "के", "में", "से", "पर", "भाव", "रेट", "दर", "दाम", 
    "आज", "कल", "यहाँ", "मंडी", "मंडियों", "बाजार", "बताएं", "बताओ", "कितना", "कितनी", "काय", "आहे",
    # Odia
    "କେତେ", "ଦର", "ରେଟ୍", "ମଣ୍ଡି", "ମଣ୍ଡିରେ", "ର", "ରେ", "ବଜାର", "ଜଣାନ୍ତୁ", "ଆଜି", "କାଲି", "କଣ", "ଅଛି",
    # Kannada
    "ಎಷ್ಟು", "ದರ", "ರೇಟ್", "ಬೆಲೆ", "ಮಾರುಕಟ್ಟೆ", "ಎಪಿಎಂಸಿ", "ಇಂದು", "ತಿಳಿಸಿ", "ಏನು", "ಇದೆ", "ನಲ್ಲಿ", "ರಲ್ಲಿ",
    # Telugu
    "ఎంత", "ధర", "రేటు", "మార్కెట్", "ఈరోజు", "తెలుపండి", "ఏమిటి", "ఉంది", "లో",
    # Tamil
    "எவ்வளவு", "விலை", "ரேட்", "சந்தை", "இன்று", "கூறுங்கள்", "என்ன", "உள்ளது", "இல்",
    # Gujarati
    "શું", "છે", "ભાવ", "રેટ", "માર્કેટ", "આજે", "જણાવો", "કેટલો", "કેટલી", "માં",
    # Bengali / Assamese
    "কত", "দাম", "দর", "মান্ডি", "মান্ডিতে", "বাজার", "আজ", "জানান", "কি", "আজি", "মণ্ডি", "মণ্ডীত", "কিমান",
    # Punjabi
    "ਕੀ", "ਹੈ", "ਭਾਅ", "ਰੇਟ", "ਮੰਡੀ", "ਅੱਜ", "ਦੱਸੋ", "ਕਿੰਨਾ",
    # Kashmiri
    "کِیٛاہ", "چُھ", "قٟمَتھ", "منڈی", "آز", "وانِو", "کۆت"
}

class AIService:
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language across 13 Indian languages based on Unicode scripts, loanwords, and colloquial markers"""
        # 1. Kashmiri Perso-Arabic or explicit markers
        if re.search(r"[؀-ۿ]", text) or any(m in text for m in KASHMIRI_MARKERS):
            return "ks"

        # 2. Odia script
        if re.search(r"[଀-୿]", text):
            return "or"

        # 3. Assamese vs Bengali (both share ঀ-৿, but Assamese has ৰ, ৱ or Assamese markers)
        if ASSAMESE_CHARS.search(text) or (re.search(r"[ঀ-৿]", text) and any(m in text for m in ASSAMESE_MARKERS)):
            return "as"
        elif re.search(r"[ঀ-৿]", text):
            return "bn"

        # 4. Other Indic scripts
        for lang, pattern in LANG_PATTERNS.items():
            if lang == "devanagari":
                if pattern.search(text):
                    # Check for Marathi markers
                    if any(m in text for m in MARATHI_MARKERS):
                        return "mr"
                    return "hi"
            elif lang not in ["perso_arabic"] and pattern.search(text):
                return lang

        # 5. Romanized / Transliterated colloquial markers detection (Hinglish, Kanglish, Odia in Latin, etc.)
        text_lower = text.lower()
        for lang, patterns in COLLOQUIAL_LANG_MARKERS.items():
            for pat in patterns:
                if re.search(pat, text_lower):
                    return lang

        return "en"

    @classmethod
    def parse_query_rule_based(cls, text: str, db: Optional[Any] = None) -> Dict[str, Any]:
        """Robust regex, multilingual keyword, and code-mixed colloquial intent parser"""
        text_lower = text.lower()
        detected_lang = AIService.detect_language(text)
        
        # 1. Detect Intent
        intent = "price" # Default
        
        list_words = ["list", "all crops", "commodities", "सूची", "목록", "ಪಟ್ಟಿ", "பட்டியல்", "यादी", "લિસ્", "ତାଲିକା", "তালিকা", "ফৰ্দ"]
        
        dealer_words = [
            "dap", "urea", "fertilizer", "fertilizers", "seed", "seeds", "pesticide", "pesticides", "खाद", "बीज", "कीटनाशक",
            "ರಸಗೊಬ್ಬರ", "ಬೀಜ", "ಕೀಟನಾಶಕ", "ખાતર", "બિયારણ", "જંતુનાશક", "खते", "बियाणे",
            "உரம்", "விதை", "பூச்சிக்கொல்லி", "ఎరువులు", "విత్తనాలు", "పురుగుమందులు", "সার", "বীজ",
            "ସାର", "ବିହନ", "সাৰ", "বীজ", "کھاد", "بیٚول", "ଡିଲର", "ଫର୍ଟିଲାଇଜର"
        ]
        buyer_words = [
            "sell", "buyer", "buyers", "purchase", "wholesaler", "wholesalers", "trader", "traders", "বেচনা", "खरीददार", "व्यापारी",
            "ಮಾರಾಟ", "ಖರೀದಿದಾರ", "ವ್ಯಾಪಾರಿ", "વેચવું", "વેપારી", "ખરીદનાર", "खरेदीदार",
            "விற்பனை", "வாங்குபவர்", "కొనుగోలుదారు", "విక్రయించడం", "বিক্রি", "ক্রেতা",
            "ବିକ୍ରି", "କ୍ରେତା", "বেচা", "ক্ৰেতা", "خٔریدار", "ویٚکُن", "ବିକ୍ରୟ"
        ]
        weather_words = [
            "weather", "rain", "monsoon", "temperature", "मौसम", "बारिश", "मಳೆ", "ಹವಾಮಾನ",
            "હવામાન", "વરસાદ", "पाऊस", "हवामान", "வானிலை", "மழை", "వాతావరణం", "వర్షం", "আবহাওয়া", "বৃষ্টি",
            "ପାଣିପାଗ", "ବର୍ଷା", "বতৰ", "বৰষুণ", "موسم", "رُد"
        ]
        msp_words = ["msp", "support price", "एमएसपी", "समर्थन मूल्य", "ಬೆಂಬಲ ಬೆಲೆ", "ટેકાના ભાવ", "हमीभाव", "குறைந்தபட்ச ஆதரவு விலை", "ସରକାରୀ ଦର", "নূন্যতম সমৰ্থন মূল্য"]
        scheme_words = ["scheme", "kisan", "yojana", "योजना", "ಯೋಜನೆ", "યોજના", "திட்டம்", "పథకం", "ଯୋଜନା", "আঁচনি", "سکیٖم"]

        advisory_words = [
            "outlook", "forecast", "advice", "advise", "advisory", "sell now", "hold", "future rate", "when to sell",
            "सलाह", "कब बेचें", "भविष्य", "पूर्वानुमान", "भाव बढ़ेगा", "भाव गिरेगा", "रिटेल भाव", "एडवाइजरी", "फोरकास्ट",
            "ಮಾರಾಟ ಮಾಡಬೇಕೆ", "ಮುನ್ಸೂಚನೆ", "ಸಲಾಹ", "ક્યારે વેચવું", "ભાવ વધશે", "ભાવ ઘટશે",
            "सल्ला", "कधी विकावे", "भाव वाढेल का", "ஆலோசனை", "எப்போது விற்க வேண்டும்",
            "సలహా", "ఎప్పుడు అమ్మాలి", "পরামর্শ", "কখন বিক্রি করব", "ପରାମର୍ଶ", "କେବେ ବିକ୍ରି କରିବି",
            "পৰামৰ্শ", "سَلاہ", "کیٚلہٕ ویٚکُن", "ଆଡଭାଇଜରୀ", "ଫୋରକାଷ୍ଟ"
        ]

        if any(w in text_lower for w in list_words):
            intent = "list_commodities"
        elif any(w in text_lower for w in advisory_words):
            intent = "advisory"
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

        # 2. Extract Candidate Tokens and Suffix-Stripped Stems
        raw_tokens = re.findall(r"[\w\u0900-\u0DFF\u0600-\u06FF]+", text)
        candidate_words = set()
        for t in raw_tokens:
            for v in strip_word_suffixes(t):
                candidate_words.add(v.lower())

        # 3. Extract Commodity (supporting inflected Indic words & Romanized colloquial loanwords)
        extracted_commodity = None
        for comm, kw_list in COMMODITY_KEYWORDS.items():
            for kw in kw_list:
                kw_lower = kw.lower()
                if re.match(r"^[a-z\s]+$", kw_lower):
                    if kw_lower in candidate_words or re.search(rf"(?:\s|^){re.escape(kw_lower)}(?:\s|$|[.,?!])", text_lower):
                        extracted_commodity = comm
                        break
                else:
                    if kw in candidate_words or kw in text:
                        extracted_commodity = comm
                        break
            if extracted_commodity:
                break
                
        # 4. Extract Location (supporting inflected Indic words & Romanized colloquial loanwords)
        extracted_district = None
        extracted_state = None
        for loc, info in LOCATION_KEYWORDS.items():
            for kw in info["keywords"]:
                kw_lower = kw.lower()
                if re.match(r"^[a-z\s]+$", kw_lower):
                    if kw_lower in candidate_words or re.search(rf"(?:\s|^){re.escape(kw_lower)}(?:\s|$|[.,?!])", text_lower):
                        extracted_district = info["district"]
                        extracted_state = info["state"]
                        break
                else:
                    if kw in candidate_words or kw in text:
                        extracted_district = info["district"]
                        extracted_state = info["state"]
                        break
            if extracted_district:
                break
                
                # 5. Dynamic DB fallback for commodity if not found in static dictionary
        if not extracted_commodity and db:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT DISTINCT commodity_name FROM commodities ORDER BY LENGTH(commodity_name) DESC")
                rows = cursor.fetchall()
                for r in rows:
                    cname = r["commodity_name"] if hasattr(r, "keys") else r[0]
                    if cname and (cname.lower() in candidate_words or re.search(rf"(?:\s|^){re.escape(cname.lower())}(?:\s|$|[.,?!])", text_lower)):
                        extracted_commodity = cname
                        break
            except Exception:
                pass

        # 6. Universal generic candidate extractor for ANY unlisted commodity, unsupported crop, or negative test case (e.g. gold, silver, petrol, dragon fruit)
        if not extracted_commodity:
            # 6A. Multi-word English Phrasings (strictly bounded non-overlapping tokens to prevent ReDoS)
            m_en = re.search(r"\b(?:rate|price|cost|bhav|market rate)\s+(?:of|for)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,3}?)(?=\s+(?:in|at|for|near|today|tomorrow|\?|$)|$)", text_lower)
            if not m_en:
                m_en = re.search(r"\b(?:what\s+is\s+(?:the\s+)?|check\s+)([a-zA-Z]+(?:\s+[a-zA-Z]+){0,3}?)\s+(?:rate|price|cost|bhav)\b", text_lower)
            if not m_en:
                m_en = re.search(r"\b([a-zA-Z]+(?:\s+[a-zA-Z]+){0,3}?)\s+(?:rate|price|cost|bhav)\s+(?:in|at|for)\b", text_lower)
                
            if m_en:
                cand = m_en.group(1).strip()
                tokens = [w for w in cand.split() if w.lower() not in UNIVERSAL_PRICE_STOPWORDS]
                if tokens:
                    cleaned_words = []
                    for w in tokens:
                        if len(w) > 4 and w.lower().endswith('s') and not w.lower().endswith('ss'):
                            cleaned_words.append(w[:-1])
                        else:
                            cleaned_words.append(w)
                    extracted_commodity = " ".join(cleaned_words).title()

            # 6B. Universal Residual Extraction (handles Indic scripts & unlisted phrases)
            if not extracted_commodity:
                # Gather matched location keywords to exclude them from commodity candidate
                loc_words = set()
                if extracted_district:
                    for loc, info in LOCATION_KEYWORDS.items():
                        if info["district"] == extracted_district or (extracted_state and info["state"] == extracted_state):
                            for kw in info["keywords"]:
                                for p in kw.lower().split():
                                    loc_words.add(p)

                cleaned = re.sub(r'[?!.,;:()\[\]"\'\-_/]', " ", text)
                tokens = cleaned.split()
                remaining_tokens = []
                for t in tokens:
                    t_lower = t.lower()
                    if t_lower in UNIVERSAL_PRICE_STOPWORDS:
                        continue
                    
                    is_loc = False
                    for kw in loc_words:
                        if kw in t_lower or t_lower in kw:
                            is_loc = True
                            break
                    if is_loc:
                        continue
                        
                    stem_variants = strip_word_suffixes(t)
                    base_token = t
                    for v in stem_variants[1:]:
                        if v.lower() in UNIVERSAL_PRICE_STOPWORDS or v.lower() in loc_words:
                            base_token = None
                            break
                        else:
                            base_token = v
                            break
                    if base_token and len(base_token) > 1:
                        remaining_tokens.append(base_token)

                if remaining_tokens:
                    res_cand = " ".join(remaining_tokens).strip()
                    if res_cand.isascii():
                        extracted_commodity = res_cand.title()
                    else:
                        extracted_commodity = res_cand

        # Dynamic DB fallback for location if not found in static dictionary
        if not extracted_district and db:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT DISTINCT state, district, mandi_name FROM mandis ORDER BY LENGTH(mandi_name) DESC")
                m_rows = cursor.fetchall()
                for r in m_rows:
                    st = r["state"] if hasattr(r, "keys") else r[0]
                    dt = r["district"] if hasattr(r, "keys") else r[1]
                    mn = r["mandi_name"] if hasattr(r, "keys") else r[2]
                    if dt and (dt.lower() in candidate_words or re.search(rf"(?:\s|^){re.escape(dt.lower())}(?:\s|$|[.,?!])", text_lower)):
                        extracted_district = dt
                        extracted_state = st
                        break
                    elif st and (st.lower() in candidate_words or re.search(rf"(?:\s|^){re.escape(st.lower())}(?:\s|$|[.,?!])", text_lower)):
                        extracted_district = st
                        extracted_state = st
                        break
                    elif mn and (mn.lower() in candidate_words or re.search(rf"(?:\s|^){re.escape(mn.lower())}(?:\s|$|[.,?!])", text_lower)):
                        extracted_district = dt or mn
                        extracted_state = st
                        break
            except Exception:
                pass

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
        """Call Gemini API for multi-lingual NLP parsing across 13 Indian languages, supporting colloquial and code-mixed speech"""
        prompt = f"""
        You are an intelligent AI agricultural assistant for Indian farmers. A farmer has asked you a query in any Indian language, English, or mixed/colloquial speech (e.g. en, hi, kn, mr, ta, te, ml, gu, pa, bn, or, as, ks).
        
        IMPORTANT INSTRUCTIONS ON CODE-MIXING & COLLOQUIAL VOCABULARY:
        Indian farmers frequently mix English loanwords (such as 'rate', 'price', 'mandi', 'market', 'advisory', 'outlook', 'forecast', 'fertilizer', 'store', 'sell') into regional languages or use Romanized transliteration (e.g., "bhubaneswar re dhanara rate kete", "shimoga dalli maize price eshtu", "pune madhye kanda rate kiti", "ଭୁବନେଶ୍ୱରରେ ଧାନର rate କେତେ", "গুৱাহাটীত আলুৰ rate কিমান").
        Always identify the underlying regional language, extract standardized crop name and location, and classify the intent correctly.

        1. Classify intent into one of:
           - "price": Asking for mandi rate/market price of crops or commodities.
           - "advisory": Asking for market outlook, selling timing (hold vs sell), production forecast, or retail margin.
           - "list_commodities": Asking what crops/commodities are available in a mandi or district.
           - "buyer": Searching for verified buyers/wholesalers to sell produce.
           - "dealer": Searching for fertilizer, seed, or pesticide input dealers.
           - "weather": Weather forecasts, rainfall, monsoon queries.
           - "msp": Minimum Support Price inquiries.
           - "scheme": Government agricultural welfare schemes (PM-Kisan, etc.).
           - "general": General farming questions, pest management, crop agronomy, or greetings.

        2. Extract details:
           - Commodity: Standard English name e.g. "Apple", "Wheat", "Paddy (Rice)", "Maize", "Onion", "Tomato", "Potato", "Cotton", "Groundnut", "Soyabean", "Gram (Chana)", "Toor Dal", "Cumin (Jeera)", "Turmeric", "Banana", "Mango", "Saffron", "Walnut", "Tea", etc.
           - State & District: Standardized Indian state & district names.
           - Language code: One of ["en", "hi", "kn", "mr", "ta", "te", "ml", "gu", "pa", "bn", "or", "as", "ks"].

        3. If intent is "general", provide a concise, expert agronomic response in the "general_answer" field in the EXACT same language/script the farmer used.

        Output format MUST be strictly JSON with no markdown tags:
        {{
            "intent": "price" | "list_commodities" | "buyer" | "dealer" | "weather" | "msp" | "scheme" | "general" | "advisory",
            "commodity": "Commodity Name" | null,
            "state": "State Name" | null,
            "district": "District Name" | null,
            "language": "en" | "hi" | "kn" | "mr" | "ta" | "te" | "ml" | "gu" | "pa" | "bn" | "or" | "as" | "ks",
            "general_answer": "Expert regional response" | null,
            "raw_query": "{text}"
        }}

        Input Query: "{text}"
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        headers = {"Content-Type": "application/json"}
        
        models = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash"
        ]
        
        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                response = requests.post(url, headers=headers, json=payload, timeout=8)
                if response.status_code == 200:
                    res_data = response.json()
                    content_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(content_text.strip())
                elif response.status_code == 429:
                    continue
            except Exception as e:
                print(f"Error calling Gemini API ({model}): {e}")
                
        return None

    @classmethod
    def parse_query(cls, text: str, db: Optional[Any] = None) -> Dict[str, Any]:
        """Entrypoint for query parsing. Falls back to rules if API key is not configured or rate-limited."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            parsed = cls.parse_query_with_llm(text, api_key)
            if parsed:
                return parsed
        return cls.parse_query_rule_based(text, db=db)

    @staticmethod
    def speech_to_text(audio_bytes: bytes, mime_type: str = "audio/ogg", language: str = "en") -> str:
        """Transcribe audio voice note using Bhashini ASR, Gemini multimodal API, or fallback defaults"""
        if audio_bytes:
            # 1. Primary: Digital India Bhashini ASR
            try:
                from app.services.bhashini_service import BhashiniService
                if BhashiniService.is_available():
                    import base64
                    encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                    fmt = "wav"
                    asr_res = BhashiniService.speech_to_text(encoded_audio, source_lang=language, audio_format=fmt)
                    if asr_res and asr_res.get("text"):
                        return asr_res["text"]
            except Exception as e:
                print(f"Bhashini ASR fallback: {e}")

            # 2. Secondary: Gemini multimodal transcription
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                try:
                    import base64
                    encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                    clean_mime = mime_type.split(";")[0].strip() if mime_type else "audio/ogg"
                    prompt = (
                        "You are an audio transcription engine for an Indian agriculture voice assistant. "
                        "Transcribe the spoken voice note accurately into text. "
                        "Support all 13 Indian languages (Hindi, Kannada, Tamil, Gujarati, Marathi, Telugu, Malayalam, Punjabi, Bengali, Odia, Assamese, Kashmiri, English). "
                        "Transcribe code-mixed, colloquial Indian speech accurately (e.g. users mixing English words like 'rate', 'price', 'mandi', 'forecast', 'today' with regional languages like Hindi, Odia, Kannada, Marathi, etc., or speaking in colloquial dialects). Preserve mixed English words as spoken. "
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
                    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
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

        return ""

    @staticmethod
    def text_to_speech_base64(text: str, lang: str = "en") -> Optional[str]:
        """Convert response text into natural voice audio Base64 string via Bhashini TTS with gTTS fallback"""
        if not text or os.environ.get("TESTING") == "1":
            return None

        # 1. Primary: Digital India Bhashini high-fidelity regional TTS
        try:
            from app.services.bhashini_service import BhashiniService
            if BhashiniService.is_available():
                audio_b64 = BhashiniService.text_to_speech(text, source_lang=lang)
                if audio_b64:
                    return audio_b64
        except Exception as e:
            print(f"Bhashini TTS fallback: {e}")

        # 2. Secondary: Fallback to gTTS
        try:
            import importlib
            gtts_module = importlib.import_module("gtts")
            gTTS = getattr(gtts_module, "gTTS")
            import io
            import base64

            clean_text = re.sub(r"[\*\_~`#•]", "", text)
            clean_text = re.sub(r"https?://\S+", "", clean_text).strip()
            clean_text = clean_text[:350]

            supported_langs = ["en", "hi", "kn", "ta", "mr", "te", "ml", "gu", "pa", "bn"]
            speak_lang = lang if lang in supported_langs else "en"

            tts = gTTS(text=clean_text, lang=speak_lang)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return base64.b64encode(fp.read()).decode("utf-8")
        except Exception as e:
            print(f"TTS audio generation error: {e}")
            return None
