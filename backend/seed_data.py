import os
import sys
import uuid
import sqlite3
import json
import random
from datetime import datetime, timedelta

# Add the backend/ directory to Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app.core.database import get_db_connection, init_db

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("Clearing old tables for fresh comprehensive Phase 4 & 5 re-seeding...")
        cursor.execute("DELETE FROM daily_prices")
        cursor.execute("DELETE FROM commodities")
        cursor.execute("DELETE FROM mandis")
        cursor.execute("DELETE FROM buyers")
        cursor.execute("DELETE FROM dealers")
        cursor.execute("DELETE FROM dealer_inventory")
        cursor.execute("DELETE FROM reservations")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM upag_macro_intelligence")
        conn.commit()
            
        print("Seeding Pan-India Mandis (with e-NAM Unified Electronic Market flags)...")
        mandis_raw = [
            # (state, district, mandi_name, apmc_code, lat, lon, is_enam, enam_code)
            # Gujarat Mandis (Major Fruit, Grain, Oilseed, Spice Markets)
            ("Gujarat", "Ahmedabad", "Ahmedabad APMC (Chimanbhai Patel)", "GJ-AMD-01", 23.0225, 72.5714, 1, "ENAM-GJ-AMD-01"),
            ("Gujarat", "Surat", "Surat APMC", "GJ-SUR-02", 21.1702, 72.8311, 1, "ENAM-GJ-SUR-02"),
            ("Gujarat", "Rajkot", "Rajkot APMC", "GJ-RJK-03", 22.3039, 70.8022, 1, "ENAM-GJ-RJK-03"),
            ("Gujarat", "Rajkot", "Gondal APMC", "GJ-GDL-04", 21.9619, 70.7937, 1, "ENAM-GJ-GDL-04"),
            ("Gujarat", "Vadodara", "Vadodara APMC", "GJ-BRD-05", 22.3072, 73.1812, 0, None),
            ("Gujarat", "Anand", "Anand APMC", "GJ-AND-06", 22.5645, 72.9289, 0, None),
            ("Gujarat", "Mehsana", "Unjha APMC (Spices)", "GJ-UNJ-07", 23.8039, 72.3922, 1, "ENAM-GJ-UNJ-07"),
            
            # Jammu & Kashmir Mandis (Famous Apple, Saffron, Dry Fruit Centers)
            ("Jammu and Kashmir", "Baramulla", "Sopore Fruit Mandi (Apple Hub)", "JK-SOP-01", 34.2980, 74.4690, 1, "ENAM-JK-SOP-01"),
            ("Jammu and Kashmir", "Srinagar", "Srinagar APMC (Parimpora)", "JK-SGR-02", 34.0837, 74.7973, 1, "ENAM-JK-SGR-02"),
            ("Jammu and Kashmir", "Jammu", "Jammu APMC (Narwal)", "JK-JMU-03", 32.7266, 74.8570, 0, None),
            
            # Odisha Mandis
            ("Odisha", "Khordha", "Bhubaneswar APMC", "OR-BBS-01", 20.2961, 85.8245, 1, "ENAM-OR-BBS-01"),
            ("Odisha", "Cuttack", "Cuttack APMC (Chhatrabazar)", "OR-CTC-02", 20.4625, 85.8828, 0, None),
            ("Odisha", "Sambalpur", "Sambalpur APMC (Khetrajpur)", "OR-SBP-03", 21.4669, 83.9812, 1, "ENAM-OR-SBP-03"),
            
            # Assam Mandis
            ("Assam", "Kamrup Metropolitan", "Guwahati APMC (Pamohi)", "AS-GHY-01", 26.1445, 91.7362, 1, "ENAM-AS-GHY-01"),
            ("Assam", "Cachar", "Silchar APMC", "AS-SLC-02", 24.8333, 92.7789, 0, None),
            ("Assam", "Jorhat", "Jorhat APMC", "AS-JRH-03", 26.7509, 94.2037, 0, None),
            
            # Karnataka Mandis
            ("Karnataka", "Shivamogga", "Shimoga APMC", "KN-SHM-01", 13.9299, 75.5681, 1, "ENAM-KN-SHM-01"),
            ("Karnataka", "Davanagere", "Davanagere APMC", "KN-DVG-02", 14.4644, 75.9218, 0, None),
            ("Karnataka", "Bengaluru", "Yeshwanthpur APMC", "KN-BLR-03", 13.0279, 77.5409, 1, "ENAM-KN-BLR-03"),
            ("Karnataka", "Dharwad", "Hubballi (Hubli) APMC", "KN-HBL-04", 15.3647, 75.1240, 1, "ENAM-KN-HBL-04"),
            ("Karnataka", "Mysuru", "Mysore APMC (Bandipalya)", "KN-MYS-05", 12.2958, 76.6394, 0, None),
            
            # Maharashtra Mandis
            ("Maharashtra", "Nashik", "Lasalgaon APMC", "MH-NSK-01", 20.1444, 74.2250, 1, "ENAM-MH-NSK-01"),
            ("Maharashtra", "Pune", "Pune APMC (Gultekdi)", "MH-PUN-02", 18.5204, 73.8567, 1, "ENAM-MH-PUN-02"),
            ("Maharashtra", "Mumbai Suburban", "Vashi APMC (Navi Mumbai)", "MH-MUM-03", 19.0771, 73.0034, 1, "ENAM-MH-MUM-03"),
            ("Maharashtra", "Nagpur", "Nagpur APMC (Kalamna)", "MH-NGP-04", 21.1458, 79.0882, 0, None),
            ("Maharashtra", "Kolhapur", "Kolhapur APMC", "MH-KLP-05", 16.7050, 74.2433, 0, None),
            
            # Madhya Pradesh Mandis
            ("Madhya Pradesh", "Indore", "Indore APMC (Choithram)", "MP-IND-01", 22.7196, 75.8577, 1, "ENAM-MP-IND-01"),
            ("Madhya Pradesh", "Ujjain", "Ujjain APMC", "MP-UJN-02", 23.1760, 75.7885, 1, "ENAM-MP-UJN-02"),
            ("Madhya Pradesh", "Bhopal", "Bhopal APMC (Karond)", "MP-BHP-03", 23.2599, 77.4126, 0, None),
            ("Madhya Pradesh", "Neemuch", "Neemuch APMC", "MP-NMC-04", 24.4600, 74.8700, 1, "ENAM-MP-NMC-04"),
            
            # Tamil Nadu Mandis
            ("Tamil Nadu", "Chennai", "Koyambedu Wholesale APMC", "TN-CHN-01", 13.0694, 80.1948, 1, "ENAM-TN-CHN-01"),
            ("Tamil Nadu", "Coimbatore", "Coimbatore APMC", "TN-CBE-02", 11.0168, 76.9558, 0, None),
            ("Tamil Nadu", "Madurai", "Madurai APMC (Mattuthavani)", "TN-MDU-03", 9.9252, 78.1198, 0, None),
            
            # Andhra Pradesh & Telangana Mandis
            ("Andhra Pradesh", "Guntur", "Guntur Mirchi APMC", "AP-GNT-01", 16.3067, 80.4365, 1, "ENAM-AP-GNT-01"),
            ("Telangana", "Hyderabad", "Bowenpally APMC", "TS-HYD-01", 17.4728, 78.4862, 1, "ENAM-TS-HYD-01"),
            
            # Punjab & Haryana Mandis
            ("Punjab", "Ludhiana", "Khanna APMC (Asia's Largest Grain Market)", "PB-KHN-01", 30.7067, 76.2198, 1, "ENAM-PB-KHN-01"),
            ("Haryana", "Karnal", "Karnal Grain APMC", "HR-KRN-01", 29.6857, 76.9905, 1, "ENAM-HR-KRN-01"),
            
            # Rajasthan & Uttar Pradesh & Delhi Mandis
            ("Delhi", "North Delhi", "Azadpur APMC (Asia's Largest Fruit & Veg Market)", "DL-AZD-01", 28.7107, 77.1770, 1, "ENAM-DL-AZD-01"),
            ("Rajasthan", "Jaipur", "Jaipur APMC (Muhana Mandi)", "RJ-JPR-01", 26.9124, 75.7873, 1, "ENAM-RJ-JPR-01"),
            ("Uttar Pradesh", "Lucknow", "Lucknow APMC (Dubagga)", "UP-LKO-01", 26.8467, 80.9462, 0, None),
            ("West Bengal", "Kolkata", "Koley Wholesale Market", "WB-KOL-01", 22.5726, 88.3639, 0, None)
        ]
        
        mandis_data = [
            (str(uuid.uuid4()), m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7])
            for m in mandis_raw
        ]
        
        cursor.executemany("""
        INSERT INTO mandis (id, state, district, mandi_name, apmc_code, latitude, longitude, is_enam, enam_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, mandis_data)
        
        print("Seeding 48+ Pan-India Commodities across 13 Regional Languages...")
        commodities_data = [
            # Fruits (including Apple, Walnut, Saffron for Kashmir/Pan-India)
            (str(uuid.uuid4()), "Apple", json.dumps({"en":"Apple","hi":"सेब","kn":"ಸೇಬು","mr":"सफरचंद","ta":"ஆப்பிள்","te":"ఆపిల్","ml":"ആപ്പിൾ","gu":"સફરજન","pa":"ਸੇਬ","bn":"আপেল","or":"ସେଓ","as":"আপেল","ks":"ژوٗنٛٹھ (Tsoonth)"}), "Fruit"),
            (str(uuid.uuid4()), "Banana", json.dumps({"en":"Banana","hi":"केला","kn":"ಬಾಳೆಹಣ್ಣು","mr":"केळी","ta":"வாழைப்பழம்","te":"అరటిపండు","ml":"വാഴപ്പഴം","gu":"કેળાં","pa":"ਕੇਲਾ","bn":"কলা","or":"କଦଳୀ","as":"কল","ks":"کیٚل (Kael)"}), "Fruit"),
            (str(uuid.uuid4()), "Mango", json.dumps({"en":"Mango","hi":"आम","kn":"ಮಾವಿನಹಣ್ಣು","mr":"आंबा","ta":"மாம்பழம்","te":"మామిడిపండు","ml":"മാമ്പഴം","gu":"કેરી","pa":"ਅੰਬ","bn":"আম","or":"ଆମ୍ବ","as":"আম","ks":"آم (Aam)"}), "Fruit"),
            (str(uuid.uuid4()), "Orange", json.dumps({"en":"Orange","hi":"संतरा","kn":"ಕಿತ್ತಳೆ","mr":"संत्री","ta":"ஆரஞ்சு","te":"నారింజ","ml":"ഓറഞ്ച്","gu":"સંતરા","pa":"ਸੰਤਰਾ","bn":"কমলালেবু","or":"କମଳା","as":"কমলা","ks":"سَنگتَرٕ (Sangtara)"}), "Fruit"),
            (str(uuid.uuid4()), "Pomegranate", json.dumps({"en":"Pomegranate","hi":"अनार","kn":"ದಾಳಿಂಬೆ","mr":"डाळिंब","ta":"மாதுளை","te":"దానిమ్మ","ml":"മാതளനാരങ്ങ","gu":"દાડમ","pa":"ਅਨਾਰ","bn":"বেদানা","or":"ଡାଳିମ୍ବ","as":"ডালিম","ks":"دانَہ (Daana)"}), "Fruit"),
            (str(uuid.uuid4()), "Grapes", json.dumps({"en":"Grapes","hi":"अंगूर","kn":"ದ್ರಾಕ್ಷಿ","mr":"द्राक्षे","ta":"திராட்சை","te":"ద్రాక్ష","ml":"മുന്തിരി","gu":"દ્રાક્ષ","pa":"ਅੰਗੂਰ","bn":"আঙুর","or":"ଅଙ୍ଗୁର","as":"আঙুৰ","ks":"دَچھ (Dachh)"}), "Fruit"),
            (str(uuid.uuid4()), "Papaya", json.dumps({"en":"Papaya","hi":"पपीता","kn":"ಪಪ್ಪಾಯಿ","mr":"पपई","ta":"பப்பாளி","te":"బొప్పాయి","ml":"പപ്പായ","gu":"પપૈયું","pa":"ਪਪੀਤਾ","bn":"পেঁপে","or":"ଅମୃତଭଣ୍ଡା","as":"অমিতা","ks":"پَپیٖتَہ (Papeeta)"}), "Fruit"),
            (str(uuid.uuid4()), "Guava", json.dumps({"en":"Guava","hi":"अमरूद","kn":"ಸೀಬೆಹಣ್ಣು","mr":"पेरू","ta":"கொய்யா","te":"జామపండు","ml":"പേരയ്ക്ക","gu":"જામફળ","pa":"ਅਮਰੂਦ","bn":"পেয়ারা","or":"ପିଜୁଳି","as":"মধুৰিআম","ks":"اَمرۄد (Amrod)"}), "Fruit"),
            (str(uuid.uuid4()), "Watermelon", json.dumps({"en":"Watermelon","hi":"तरबूज","kn":"ಕಲ್ಲಂಗಡಿ","mr":"कलिंगड","ta":"தர்பூசணி","te":"పుచ్చకాయ","ml":"തണ്ണിമത്തൻ","gu":"તરબૂચ","pa":"ਤਰਬੂਜ਼","bn":"তরমুজ","or":"ତରଭୁଜ","as":"তৰমুজ","ks":"ہِندᱣանդ (Hindwand)"}), "Fruit"),
            (str(uuid.uuid4()), "Walnut", json.dumps({"en":"Walnut","hi":"अखरोट","kn":"ಅಕ್ರೋಟ","mr":"अक्रोड","ta":"அக்ரூட் பருப்பு","te":"అక్రోట్లను","ml":"അക്രോട്ട്","gu":"અખરોટ","pa":"ਅਖਰੋਟ","bn":"আখরোট","or":"ଅଖରୋଟ","as":"আখৰোট","ks":"ڈوٗن (Doon)"}), "Fruit"),
            (str(uuid.uuid4()), "Saffron", json.dumps({"en":"Saffron","hi":"केसर","kn":"ಕೇಸರಿ","mr":"केशर","ta":"குங்குமப்பூ","te":"కుంకుమపువ్వు","ml":"കുങ്കുമപ്പൂവ്","gu":"કેસર","pa":"ਕੇਸਰ","bn":"জাফরান","or":"କେଶର","as":"জাফৰান","ks":"کونٛگ (Kong)"}), "Spice"),
            
            # Cereals & Grains
            (str(uuid.uuid4()), "Wheat", json.dumps({"en":"Wheat","hi":"गेहूं","kn":"ಗೋಧಿ","mr":"गहू","ta":"கோதுமை","te":"గోధుమలు","ml":"ഗോതമ്പ്","gu":"ઘઉં","pa":"ਕਣਕ","bn":"গম","or":"ଗହମ","as":"গম","ks":"گَنَم (Ganam)"}), "Cereal"),
            (str(uuid.uuid4()), "Paddy (Rice)", json.dumps({"en":"Paddy (Rice)","hi":"धान (चावल)","kn":"ಭತ್ತ","mr":"भात (धान)","ta":"நெல்","te":"వరి ధాన్యం","ml":"നെല്ല്","gu":"ડાંગર (ચોખા)","pa":"ਝੋਨਾ","bn":"ধান","or":"ଧାନ","as":"ধান","ks":"دانۍ (Daani)"}), "Cereal"),
            (str(uuid.uuid4()), "Maize", json.dumps({"en":"Maize","hi":"मक्का","kn":"ಮೆಕ್ಕೆಜೋಳ","mr":"मका","ta":"மக்காச்சோளம்","te":"మొక్కజొన్న","ml":"ചോളം","gu":"મકાઈ","pa":"ਮੱਕੀ","bn":"ভুট্টা","or":"ମକା","as":"মাকৈ","ks":"مکٲئی (Makaai)"}), "Cereal"),
            (str(uuid.uuid4()), "Barley", json.dumps({"en":"Barley","hi":"जौ","kn":"ಬಾರ್ಲಿ","mr":"जव","ta":"பார்லி","te":"బార్లీ","ml":"ബാർലി","gu":"જવ","pa":"ਜੌਂ","bn":"যব","or":"ଯବ","as":"বাৰ্লি","ks":"واشُک (Washuk)"}), "Cereal"),
            (str(uuid.uuid4()), "Bajra (Pearl Millet)", json.dumps({"en":"Bajra","hi":"बाजरा","kn":"ಸಜ್ಜೆ","mr":"बाजरी","ta":"கம்பு","te":"సజ్జలు","ml":"കമ്പം","gu":"બાજરી","pa":"ਬਾਜਰਾ","bn":"বাজরা","or":"ବାଜରା","as":"বাজৰা","ks":"باجرٕ (Bajra)"}), "Cereal"),
            (str(uuid.uuid4()), "Jowar (Sorghum)", json.dumps({"en":"Jowar","hi":"ज्वार","kn":"ಜೋಳ","mr":"ज्वारी","ta":"சோளம்","te":"జొన్నలు","ml":"യവം","gu":"જુવાર","pa":"ਜਵਾਰ","bn":"জোয়ার","or":"ଜୁଆର","as":"জোৱাৰ","ks":"جوار (Jowar)"}), "Cereal"),
            (str(uuid.uuid4()), "Ragi (Finger Millet)", json.dumps({"en":"Ragi","hi":"रागी","kn":"ರಾಗಿ","mr":"नाचणी","ta":"கேழ்வரகு","te":"రాగులు","ml":"പഞ്ഞപ്പുല്ല്","gu":"નાગલી","pa":"ਰਾਗੀ","bn":"মারুয়া","or":"ମାଣ୍ଡିଆ","as":"মৰুৱা","ks":"راگی (Ragi)"}), "Cereal"),

            # Pulses
            (str(uuid.uuid4()), "Gram (Chana)", json.dumps({"en":"Gram (Chana)","hi":"चना","kn":"ಕಡಲೆ","mr":"हरभरा","ta":"கொண்டைக்கடலை","te":"శనగలు","ml":"കടല","gu":"ચણા","pa":"ਛੋਲੇ","bn":"ছোলা","or":"ବୁଟ","as":"বুট","ks":"چَنہٕ (Chana)"}), "Pulse"),
            (str(uuid.uuid4()), "Toor Dal", json.dumps({"en":"Toor Dal","hi":"अरहर / तुअर","kn":"ತೊಗರಿ ಬೇಳೆ","mr":"तूर डाळ","ta":"துவரம் பருப்பு","te":"కందిపప్పు","ml":"തുവരപ്പരിപ്പ്","gu":"તૂર દાળ","pa":"ਤੂਰ ਦਾਲ","bn":"অরহর ডাল","or":"ହରଡ ଡାଲି","as":"ৰহৰ দাইল","ks":"تُوٗر دال (Toor Dal)"}), "Pulse"),
            (str(uuid.uuid4()), "Moong Dal", json.dumps({"en":"Moong Dal","hi":"मूंग","kn":"ಹೆಸರು ಕಾಳು","mr":"मूग","ta":"பாசிப்பருப்பு","te":"పెసలు","ml":"ചെറുപയർ","gu":"મગ","pa":"ਮੂੰਗੀ","bn":"মুগ ডাল","or":"ମୁଗ ଡାଲି","as":"মুগ দাইল","ks":"مۄنٛگ (Moong)"}), "Pulse"),
            (str(uuid.uuid4()), "Urad Dal", json.dumps({"en":"Urad Dal","hi":"उड़द","kn":"ಉದ್ದಿನ ಬೇಳೆ","mr":"उडीद","ta":"உளுத்தம் பருப்பு","te":"మినుములు","ml":"உഴുന്ന്","gu":"અડદ","pa":"ਮਾਂਹ","bn":"মাষকলাই","or":"ବିରି ଡାଲି","as":"মাটিমাহ","ks":"ماش (Maash)"}), "Pulse"),
            (str(uuid.uuid4()), "Masoor Dal", json.dumps({"en":"Masoor Dal","hi":"मसूर","kn":"ಮಸೂರ್ ಬೇಳೆ","mr":"मसूर","ta":"மைசூர் பருப்பு","te":"మైసూర్ పప్పు","ml":"മസൂർ പരിപ്പ്","gu":"મસૂર","pa":"ਮਸਰ","bn":"মসুর ডাল","or":"ମସୁର ଡାଲି","as":"মচুৰ দাইল","ks":"مَسُر (Masoor)"}), "Pulse"),

            # Vegetables
            (str(uuid.uuid4()), "Onion", json.dumps({"en":"Onion","hi":"प्याज","kn":"ಈರುಳ್ಳಿ","mr":"कांदा","ta":"வெங்காயம்","te":"ఉల్లిపాయ","ml":"സவாള","gu":"ડુંગળી","pa":"ਪਿਆਜ਼","bn":"পেঁয়াজ","or":"ପିଆଜ","as":"পিয়াঁজ","ks":"گنڈٕ (Gandeh)"}), "Vegetable"),
            (str(uuid.uuid4()), "Potato", json.dumps({"en":"Potato","hi":"आलू","kn":"ಆಲೂಗಡ್ಡೆ","mr":"बटाटा","ta":"உருளைக்கிழங்கு","te":"బంగాళాదుంప","ml":"ഉരുളക്കിഴങ്ങ്","gu":"બટાટા","pa":"ਆਲੂ","bn":"আলু","or":"ଆଳୁ","as":"আলু","ks":"آلوٚو (Aaloo)"}), "Vegetable"),
            (str(uuid.uuid4()), "Tomato", json.dumps({"en":"Tomato","hi":"टमाटर","kn":"ಟೊಮೆಟೊ","mr":"टोमॅटो","ta":"தக்காளி","te":"టమోటా","ml":"തക്കാളി","gu":"ટામેટાં","pa":"ਟਮਾਟਰ","bn":"টমেটো","or":"ବିଲାତି ବାଇଗଣ","as":"বিলাহী","ks":"ٹماٹَر (Tamatar)"}), "Vegetable"),
            (str(uuid.uuid4()), "Green Chilli", json.dumps({"en":"Green Chilli","hi":"हरी मिर्च","kn":"ಹಸಿರು ಮೆಣಸಿನಕಾಯಿ","mr":"हिरवी मिरची","ta":"பச்சை மிளகாய்","te":"పచ్చిమిర్చి","ml":"പച്ചമുളക്","gu":"લીલાં મરચાં","pa":"ਹਰੀ ਮਿਰਚ","bn":"কাঁচা লঙ্কা","or":"କଞ୍ଚା ଲଙ୍କା","as":"কেঁচা জলকীয়া","ks":"مۄرژھ (Marchh)"}), "Vegetable"),
            (str(uuid.uuid4()), "Garlic", json.dumps({"en":"Garlic","hi":"लहसुन","kn":"ಬೆಳ್ಳುಳ್ಳಿ","mr":"लसूण","ta":"பூண்டு","te":"వెల్లుల్లి","ml":"വെളുത്തുള്ളി","gu":"લસણ","pa":"ਲਸਣ","bn":"রসুন","or":"ରସୁଣ","as":"নহৰু","ks":"روہُن (Rohan)"}), "Vegetable"),
            (str(uuid.uuid4()), "Ginger", json.dumps({"en":"Ginger","hi":"अदरक","kn":"ಶುಂಠಿ","mr":"आले","ta":"இஞ்சி","te":"అల్లం","ml":"ഇഞ്ചി","gu":"આદુ","pa":"ਅਦਰਕ","bn":"আদা","or":"ଅଦା","as":"আদা","ks":"اَدرَکھ (Adrakh)"}), "Vegetable"),
            (str(uuid.uuid4()), "Cabbage", json.dumps({"en":"Cabbage","hi":"पत्ता गोभी","kn":"ಎಲೆಕೋಸು","mr":"कोबी","ta":"முட்டைக்கோஸ்","te":"క్యాబేజీ","ml":"കാബേജ്","gu":"કોબીજ","pa":"ਬੰਦ ਗੋਭੀ","bn":"বাঁধাকপি","or":"ବନ୍ଧାକୋବି","as":"বন্ধাকবি","ks":"بَند گوبھی (Band Gobhi)"}), "Vegetable"),
            (str(uuid.uuid4()), "Cauliflower", json.dumps({"en":"Cauliflower","hi":"फूल गोभी","kn":"ಹೂಕೋಸು","mr":"फ्लॉवर","ta":"காலிஃபிளவர்","te":"కాలీఫ్లవర్","ml":"കോളിഫ്ലവർ","gu":"ફૂલેવર","pa":"ਫੁੱਲ ਗੋਭੀ","bn":"ফুলকপি","or":"ଫୁଲକୋବି","as":"ফুলকবি","ks":"پھوٗل گوبھی (Phool Gobhi)"}), "Vegetable"),

            # Commercial, Spices & Plantation Crops
            (str(uuid.uuid4()), "Cotton", json.dumps({"en":"Cotton","hi":"कपास","kn":"ಹತ್ತಿ","mr":"कापूस","ta":"பருத்தி","te":"పత్తి","ml":"പരുത്തി","gu":"કપાસ","pa":"ਕਪਾਹ","bn":"তুলা","or":"କପା","as":"কপাহ","ks":"کَپَس (Kapas)"}), "Commercial"),
            (str(uuid.uuid4()), "Sugarcane", json.dumps({"en":"Sugarcane","hi":"गन्ना","kn":"ಕಬ್ಬು","mr":"ऊस","ta":"கரும்பு","te":"చెరకు","ml":"കരിമ്പ്","gu":"શેરડી","pa":"ਗੰਨਾ","bn":"আখ","or":"ଆଖୁ","as":"কুঁহিয়াৰ","ks":"گَنَہ (Ganna)"}), "Commercial"),
            (str(uuid.uuid4()), "Soyabean", json.dumps({"en":"Soyabean","hi":"सोयाबीन","kn":"ಸೋಯಾಬೀನ್","mr":"सोयाबीन","ta":"சோயாபீன்","te":"సోయాబీన్","ml":"സോയാബീൻ","gu":"સોયાબીન","pa":"ਸੋਇਆਬੀਨ","bn":"সয়াবিন","or":"ସୋୟାବିନ","as":"ছয়াবিন","ks":"سویا بین (Soyabean)"}), "Oilseed"),
            (str(uuid.uuid4()), "Groundnut", json.dumps({"en":"Groundnut","hi":"मूंगफली","kn":"ಕಡಲೆಕಾಯಿ","mr":"भुईमूग","ta":"வேர்க்கடலை","te":"వేరుశనగ","ml":"നിലക്കടല","gu":"મગફળી","pa":"ਮੂੰਗਫਲੀ","bn":"চীনাবাদাম","or":"ଚିନାବାଦାମ","as":"বাদাম","ks":"موٗنٛگ پھَلی (Moongphali)"}), "Oilseed"),
            (str(uuid.uuid4()), "Mustard", json.dumps({"en":"Mustard","hi":"सरसों","kn":"ಸಾಸಿವೆ","mr":"मोहरी","ta":"கடுகு","te":"ఆవాలు","ml":"കടുക്","gu":"રાઈ / સરસવ","pa":"ਸਰ੍ਹੋਂ","bn":"সরিষা","or":"ସୋରିଷ","as":"সৰিয়হ","ks":"آسُر (Asur)"}), "Oilseed"),
            (str(uuid.uuid4()), "Cumin (Jeera)", json.dumps({"en":"Cumin (Jeera)","hi":"जीरा","kn":"ಜೀರಿಗೆ","mr":"जिरे","ta":"சீரகம்","te":"జీలకర్ర","ml":"ജീരകം","gu":"જીરું","pa":"ਜੀਰਾ","bn":"জিরে","or":"ଜିରା","as":"জীৰা","ks":"زیوٗر (Zyur)"}), "Spice"),
            (str(uuid.uuid4()), "Turmeric", json.dumps({"en":"Turmeric","hi":"हल्दी","kn":"ಅರಿಶಿನ","mr":"हळद","ta":"மஞ்சள்","te":"పసుపు","ml":"മഞ്ഞൾ","gu":"હળદર","pa":"ਹਲਦੀ","bn":"হলুদ","or":"ହଳଦୀ","as":"হালধি","ks":"لَدٕر (Lader)"}), "Spice"),
            (str(uuid.uuid4()), "Tea", json.dumps({"en":"Tea","hi":"चाय","kn":"ಟೀ","mr":"चहा","ta":"தேநீர்","te":"తేయాకు","ml":"ചായ","gu":"ચા","pa":"ਚਾਹ","bn":"চা","or":"ଚା","as":"চাহ","ks":"چائے (Chaye)"}), "Plantation"),
            (str(uuid.uuid4()), "Coffee", json.dumps({"en":"Coffee","hi":"कॉफ़ी","kn":"ಕಾಫಿ","mr":"कॉफी","ta":"காபி","te":"కాఫీ","ml":"കാപ്പി","gu":"કોફી","pa":"ਕੌਫੀ","bn":"কফি","or":"କଫି","as":"কফি","ks":"کافی (Coffee)"}), "Plantation")
        ]
        
        cursor.executemany("""
        INSERT INTO commodities (id, commodity_name, local_name, category)
        VALUES (?, ?, ?, ?)
        """, commodities_data)
        
        # Benchmark price base rates
        base_prices = {
            "Apple": 8500.0, "Walnut": 32000.0, "Saffron": 220000.0, "Banana": 2200.0, "Mango": 6500.0,
            "Orange": 4200.0, "Pomegranate": 9500.0, "Grapes": 7200.0, "Papaya": 1800.0, "Guava": 2600.0,
            "Watermelon": 1200.0, "Wheat": 2550.0, "Paddy (Rice)": 3100.0, "Maize": 2350.0, "Barley": 2100.0,
            "Bajra (Pearl Millet)": 2250.0, "Jowar (Sorghum)": 3300.0, "Ragi (Finger Millet)": 3800.0,
            "Gram (Chana)": 5900.0, "Toor Dal": 9800.0, "Moong Dal": 8400.0, "Urad Dal": 8900.0,
            "Masoor Dal": 6400.0, "Onion": 2400.0, "Potato": 1850.0, "Tomato": 1800.0, "Green Chilli": 4500.0,
            "Garlic": 12500.0, "Ginger": 7800.0, "Cabbage": 1400.0, "Cauliflower": 1600.0, "Cotton": 7200.0,
            "Sugarcane": 380.0, "Soyabean": 4650.0, "Groundnut": 6800.0, "Mustard": 5600.0,
            "Cumin (Jeera)": 26500.0, "Turmeric": 14200.0, "Tea": 19500.0, "Coffee": 31000.0
        }

        # Specific Varieties by Commodity
        commodity_varieties = {
            "Apple": ("Kashmiri Delicious", "Grade A"),
            "Walnut": ("Kashmiri Kagzi", "Super"),
            "Saffron": ("Mongra Pure", "Grade 1 (ISO 3632)"),
            "Wheat": ("Sharbati", "FAQ"),
            "Paddy (Rice)": ("Basmati 1121", "Super A"),
            "Maize": ("Hybrid Yellow", "FAQ"),
            "Onion": ("Nashik Red Garva", "FAQ"),
            "Potato": ("Jyoti / Kufri", "Grade A"),
            "Tomato": ("Hybrid-6", "Grade A"),
            "Cotton": ("Shankar-6", "Super"),
            "Groundnut": ("GG-20", "Grade A"),
            "Soyabean": ("JS-335", "FAQ"),
            "Cumin (Jeera)": ("Gujarat-4", "Premium Machine Clean"),
            "Turmeric": ("Salem / Nizamabad", "Finger Grade 1"),
            "Tea": ("Assam Orthodox", "BOP Premium")
        }

        print("Seeding Realistic 7-Day Market Prices with e-NAM Arrivals & Assaying...")
        prices_data = []
        today = datetime.now().date()
        
        for mandi in mandis_data:
            m_id = mandi[0]
            m_name = mandi[3]
            is_enam_mandi = mandi[7]
            
            for comm in commodities_data:
                c_id = comm[0]
                c_name = comm[1]
                
                base_p = base_prices.get(c_name, 2500.0)
                # Regional variance
                if "Gujarat" in mandi[1] and c_name in ["Cumin (Jeera)", "Cotton", "Groundnut"]:
                    base_p *= 1.05
                elif "Jammu and Kashmir" in mandi[1] and c_name in ["Apple", "Walnut", "Saffron"]:
                    base_p *= 0.90 # Origin production market
                elif "Assam" in mandi[1] and c_name in ["Tea"]:
                    base_p *= 0.88 # Origin market
                    
                var_tuple = commodity_varieties.get(c_name, ("Standard", "Grade A"))
                variety_name = var_tuple[0]
                grade_name = var_tuple[1]
                
                for days_ago in range(7):
                    day_date = (today - timedelta(days=days_ago)).isoformat()
                    fluctuation = (random.random() - 0.5) * 0.08
                    day_modal = round(base_p * (1.0 + fluctuation), 0)
                    day_min = round(day_modal * 0.93, 0)
                    day_max = round(day_modal * 1.07, 0)
                    
                    # Realistic daily arrival quantities (in Quintals)
                    if c_name in ["Wheat", "Paddy (Rice)", "Onion", "Potato"]:
                        arrivals = round(random.uniform(400.0, 1800.0), 1)
                    elif c_name in ["Apple", "Banana", "Tomato", "Cotton"]:
                        arrivals = round(random.uniform(250.0, 950.0), 1)
                    elif c_name in ["Saffron"]:
                        arrivals = round(random.uniform(2.5, 12.0), 1)
                    else:
                        arrivals = round(random.uniform(80.0, 450.0), 1)

                    trade_type = "e-Auction" if is_enam_mandi else "Spot"
                    source_label = "e-NAM Unified Trade" if is_enam_mandi else "AGMARKNET Live"

                    prices_data.append((
                        str(uuid.uuid4()), m_id, c_id, day_date, 
                        day_min, day_modal, day_max, source_label,
                        arrivals, variety_name, grade_name, trade_type
                    ))

        cursor.executemany("""
        INSERT INTO daily_prices (id, mandi_id, commodity_id, date, min_price, modal_price, max_price, source, arrivals_qty, variety, grade, trade_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, prices_data)
        
        print(f"Seeded {len(prices_data)} daily price records with e-NAM trade depths!")

        print("Seeding UPAg Macro-Statistical Intelligence (Phase 5)...")
        upag_records = [
            # (state, commodity, season, prod_mt, trend_pct, supply_outlook, retail, wholesale, spread_pct, rain_pct, res_pct, adv)
            ("Gujarat", "Apple", "Season 2026", 145000.0, 6.4, "Bumper Harvest / Healthy Demand", 132.0, 85.0, 55.3, 3.1, 79.0, "High consumer demand in Ahmedabad & Surat. Terminal market rates are firm for Grade A Kashmiri apples."),
            ("Jammu and Kashmir", "Apple", "Kharif-Autumn 2026", 1850000.0, 8.2, "Bumper Harvest / Peak Picking", 125.0, 78.0, 60.2, -1.2, 82.0, "Peak arrivals at Sopore & Parimpora. Gradual dispatch to Western & Southern mandis recommended."),
            ("Gujarat", "Cotton", "Kharif 2026", 8800000.0, 4.5, "Strong Textile Mill Demand", 92.0, 72.0, 27.8, 2.8, 77.0, "Good export inquiry. Stagger ginning sales over the next 3 weeks for premium realization."),
            ("Gujarat", "Groundnut", "Kharif 2026", 4200000.0, 5.1, "Active Oil Crushing Demand", 112.0, 68.0, 64.7, 4.0, 81.0, "Crushing mill inquiries strong in Rajkot & Gondal. Favorable selling window for dry pods."),
            ("Gujarat", "Cumin (Jeera)", "Rabi 2026", 460000.0, -3.8, "Tight Global Supply / High Exports", 340.0, 265.0, 28.3, -2.1, 75.0, "Global export demand firm at Unjha. Strong price outlook; avoid panic sales."),
            ("Maharashtra", "Onion", "Late Kharif 2026", 9200000.0, -6.8, "Tight Supply / Firm Price Outlook", 44.0, 24.0, 83.3, -4.5, 71.0, "Export demand active at Lasalgaon. Consumer retail spread is high; hold quality stock for better returns."),
            ("Maharashtra", "Soyabean", "Kharif 2026", 5100000.0, 3.2, "Steady Domestic Crushing", 62.0, 46.5, 33.3, 1.5, 76.0, "Feed industry demand steady. Gradual selling advised."),
            ("Madhya Pradesh", "Wheat", "Rabi 2026", 14200000.0, 3.8, "Robust Government Procurement & Buffer Stocks", 38.0, 25.5, 49.0, 1.8, 80.0, "MSP procurement centers operating at full capacity. Register lots on e-NAM for quick settlement."),
            ("Madhya Pradesh", "Soyabean", "Kharif 2026", 6400000.0, 4.1, "Steady Plant Inquiries", 64.0, 46.0, 39.1, 2.2, 78.0, "Processing demand stable at Indore & Ujjain. Quality bean prices holding steady."),
            ("Karnataka", "Maize", "Kharif 2026", 4800000.0, 2.9, "Strong Poultry Feed Offtake", 34.0, 23.5, 44.7, 3.5, 83.0, "Starch and feed mills actively purchasing at Shimoga & Davanagere. Favorable market window."),
            ("Karnataka", "Paddy (Rice)", "Kharif 2026", 3900000.0, 4.2, "Steady Mill Procurement", 48.0, 31.0, 54.8, 4.2, 85.0, "Sona Masoori quality fetching premium over MSP. Recommended to sell moisture-tested grain."),
            ("Odisha", "Paddy (Rice)", "Kharif 2026", 8200000.0, 5.5, "Active Government Mandi Procurement", 44.0, 29.5, 49.2, 5.8, 88.0, "Procurement tokens active in Khordha & Sambalpur. Direct e-NAM payment to bank account."),
            ("Assam", "Tea", "Flush 2026", 680000.0, 3.5, "Strong Export & CTC Auction Demand", 280.0, 195.0, 43.6, 6.2, 90.0, "Good export inquiry for Orthodox teas in Guwahati auction. High leaf quality fetching top bids."),
            ("Punjab", "Wheat", "Rabi 2026", 17500000.0, 2.1, "Peak FCI Procurement", 36.0, 25.5, 41.2, 0.5, 79.0, "Khanna mandi operating 24/7 digital pass system. Guaranteed MSP settlement."),
            ("Delhi", "Tomato", "Autumn 2026", 750000.0, 9.5, "Heavy Inflow from Surrounding States", 35.0, 18.0, 94.4, 1.0, 74.0, "High arrivals at Azadpur terminal market. Perishable crop; prompt daily clearing recommended.")
        ]

        upag_data = [
            (
                str(uuid.uuid4()), u[0], u[1], u[2], u[3], u[4], u[5],
                u[6], u[7], u[8], u[9], u[10], u[11], today.isoformat()
            )
            for u in upag_records
        ]

        cursor.executemany("""
        INSERT INTO upag_macro_intelligence (
            id, state, commodity, season, estimated_production_mt, 
            production_trend_pct, supply_outlook, retail_price_avg, 
            wholesale_price_avg, retail_spread_pct, rainfall_departure_pct, 
            reservoir_storage_pct, advisory_recommendation, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, upag_data)

        print(f"Seeded {len(upag_data)} UPAg Macro Intelligence records!")

        print("Seeding Verified Wholesalers & Buyers...")
        buyers_data = [
            (str(uuid.uuid4()), "Gujarat Agro Commodities Ltd", "24AAACG1234A1Z5", "Ahmedabad", "Apple", "+91 98250 11223", 1, 4.8),
            (str(uuid.uuid4()), "Kashmir Valley Orchards", "01AAACK9988B1Z2", "Baramulla", "Apple", "+91 94190 33445", 1, 4.9),
            (str(uuid.uuid4()), "Surat Fresh Produce Co", "24BBBCC4567D1Z8", "Surat", "Banana", "+91 98251 22334", 1, 4.7),
            (str(uuid.uuid4()), "Saurashtra Oil Mills", "24AAACS9988B1Z2", "Rajkot", "Groundnut", "+91 98252 33445", 1, 4.9),
            (str(uuid.uuid4()), "Odisha Grains & Rice Corp", "21AAACR1122E1Z3", "Khordha", "Paddy (Rice)", "+91 94370 12345", 1, 4.8),
            (str(uuid.uuid4()), "Brahmaputra Tea Traders", "18AAACT3344F1Z9", "Kamrup Metropolitan", "Tea", "+91 94350 56789", 1, 4.9),
            (str(uuid.uuid4()), "Karnataka Agro Exports", "29AAACK1234C1Z6", "Shivamogga", "Maize", "+91 98450 12345", 1, 4.8),
            (str(uuid.uuid4()), "Sahyadri Farmers Producer Co", "27AAACS5678D1Z4", "Nashik", "Onion", "+91 98220 54321", 1, 4.7),
            (str(uuid.uuid4()), "Malwa Soya Processing Ltd", "23AAACM9012E1Z2", "Indore", "Soyabean", "+91 98930 67890", 1, 4.9)
        ]
        cursor.executemany("""
        INSERT INTO buyers (id, company, gst_number, district, commodity, phone, verified, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, buyers_data)
        
        print("Seeding Input Dealers & Inventory...")
        dealers_data = [
            (str(uuid.uuid4()), "Kisan Suvidha Kendra", 1, 1, 1, "Ahmedabad", 1),
            (str(uuid.uuid4()), "Sopore Agri Input Center", 1, 1, 1, "Baramulla", 1),
            (str(uuid.uuid4()), "Bhubaneswar Krushi Seva Kendra", 1, 1, 1, "Khordha", 1),
            (str(uuid.uuid4()), "Guwahati Farm Supplies", 1, 1, 1, "Kamrup Metropolitan", 1),
            (str(uuid.uuid4()), "Shimoga Agro Center", 1, 1, 1, "Shivamogga", 1),
            (str(uuid.uuid4()), "Indore Agro Agency", 1, 1, 1, "Indore", 1),
            (str(uuid.uuid4()), "Lasalgaon Shetkari Seva", 1, 1, 1, "Nashik", 1)
        ]
        cursor.executemany("""
        INSERT INTO dealers (id, shop_name, fertilizer, seed, pesticide, location, verified)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, dealers_data)
        
        # Seed Inventory
        cursor.execute("SELECT id FROM dealers")
        all_dealer_ids = [r[0] for r in cursor.fetchall()]
        
        inventory_items = [
            ("IFFCO Urea (45kg)", "Fertilizer", 266.5, 120, "bag"),
            ("IFFCO DAP (50kg)", "Fertilizer", 1350.0, 85, "bag"),
            ("NPK 19-19-19 (1kg)", "Fertilizer", 140.0, 200, "pack"),
            ("Hybrid Apple Grafting Rootstock", "Seed", 350.0, 50, "plant"),
            ("Paddy Hybrid Seed DRR-45 (10kg)", "Seed", 850.0, 75, "bag"),
            ("Maize Pioneer Hybrid P3396 (4kg)", "Seed", 980.0, 60, "packet"),
            ("Coragen Insecticide (60ml)", "Pesticide", 480.0, 45, "bottle"),
            ("Neem Oil Organic Spray (1L)", "Pesticide", 320.0, 90, "bottle")
        ]
        
        inv_data = []
        for d_id in all_dealer_ids:
            for item in inventory_items:
                inv_data.append((
                    str(uuid.uuid4()), d_id, item[0], item[1], item[2], item[3], item[4]
                ))
                
        cursor.executemany("""
        INSERT INTO dealer_inventory (id, dealer_id, item_name, category, price, stock_quantity, unit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, inv_data)

        conn.commit()
        print("Database successfully seeded with Phase 4 (e-NAM) and Phase 5 (UPAg) models!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
