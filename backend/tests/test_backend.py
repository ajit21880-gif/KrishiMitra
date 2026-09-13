import os
import sys
import unittest
import json

# Reconfigure stdout for Indic UTF-8 characters if running on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend/ to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["TESTING"] = "1"

from app.main import app

class KrishiMitraTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_read_root(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["app"], "KrishiMitra AI Backend")

    def test_get_states(self):
        response = self.app.get("/api/mandi/states")
        self.assertEqual(response.status_code, 200)
        states = json.loads(response.data)
        self.assertTrue(isinstance(states, list))
        self.assertIn("Karnataka", states)
        self.assertIn("Gujarat", states)
        self.assertIn("Maharashtra", states)
        self.assertIn("Madhya Pradesh", states)
        self.assertIn("Odisha", states)
        self.assertIn("Assam", states)
        self.assertIn("Jammu and Kashmir", states)

    def test_mandi_prices_indore(self):
        response = self.app.get("/api/mandi/price?state=Madhya%20Pradesh&district=Indore&mandi_name=Indore%20APMC%20(Choithram)&commodity_name=Wheat")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["commodity"], "Wheat")
        self.assertTrue(data["modal_price"] > 0)

    def test_gujarat_apple_rates(self):
        """Phase 1 Verification: Apple rates in Gujarat mandis (Ahmedabad & Surat)"""
        url = "/api/mandi/price?state=Gujarat&district=Ahmedabad&mandi_name=Ahmedabad%20APMC%20(Chimanbhai%20Patel)&commodity_name=Apple"
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["commodity"], "Apple")
        self.assertIn("Ahmedabad", data["mandi"])
        self.assertTrue(data["modal_price"] > 0)
        self.assertTrue(data["min_price"] <= data["modal_price"] <= data["max_price"])

    def test_kashmir_apple_rates(self):
        """Verification: Apple rates in Sopore Fruit Mandi, Jammu & Kashmir"""
        url = "/api/mandi/price?state=Jammu%20and%20Kashmir&district=Baramulla&mandi_name=Sopore%20Fruit%20Mandi%20(Apple%20Hub)&commodity_name=Apple"
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["commodity"], "Apple")
        self.assertIn("Sopore", data["mandi"])
        self.assertTrue(data["modal_price"] > 0)

    def test_odisha_paddy_rates(self):
        """Verification: Paddy rates in Bhubaneswar APMC, Odisha"""
        url = "/api/mandi/price?state=Odisha&district=Khordha&mandi_name=Bhubaneswar%20APMC&commodity_name=Paddy%20(Rice)"
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["commodity"], "Paddy (Rice)")
        self.assertIn("Bhubaneswar", data["mandi"])
        self.assertTrue(data["modal_price"] > 0)

    def test_assam_tea_rates(self):
        """Verification: Tea rates in Guwahati APMC, Assam"""
        url = "/api/mandi/price?state=Assam&district=Kamrup%20Metropolitan&mandi_name=Guwahati%20APMC%20(Pamohi)&commodity_name=Tea"
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["commodity"], "Tea")
        self.assertIn("Guwahati", data["mandi"])
        self.assertTrue(data["modal_price"] > 0)

    def test_gujarat_apple_trends(self):
        """Phase 1 Verification: 7-day trend for Apple in Ahmedabad"""
        url = "/api/mandi/trend?mandi_name=Ahmedabad%20APMC%20(Chimanbhai%20Patel)&commodity_name=Apple"
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("trend", data)
        self.assertTrue(len(data["trend"]) >= 5)

    def test_process_query_english(self):
        payload = {
            "text": "What is the Maize rate in Shimoga?",
            "language": "en"
        }
        response = self.app.post("/api/query", 
                                 data=json.dumps(payload),
                                 content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("Maize", data["text"])
        self.assertIn("Shimoga", data["text"])

    def test_process_query_gujarati(self):
        """Gujarati query with inflected suffixes (સફરજનનો, અમદાવાદમાં)"""
        payload = {
            "text": "અમદાવાદમાં સફરજનનો ભાવ શું છે?",
            "language": "gu"
        }
        response = self.app.post("/api/query",
                                 data=json.dumps(payload),
                                 content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue("સફરજન" in data["text"] or "Apple" in data["text"])
        self.assertTrue("ભાવ" in data["text"] or "₹" in data["text"])

    def test_process_query_marathi(self):
        """Marathi query disambiguation and inflected suffixes (कांद्याचा, पुण्यात)"""
        payload = {
            "text": "पुण्यात कांद्याचा भाव काय आहे?",
            "language": "mr"
        }
        response = self.app.post("/api/query",
                                 data=json.dumps(payload),
                                 content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue("कांदा" in data["text"] or "Onion" in data["text"])
        self.assertTrue("दर" in data["text"] or "₹" in data["text"])

    def test_process_query_odia(self):
        """Odia language query verification (ଭୁବନେଶ୍ୱରରେ ଧାନର ଦର କେତେ?)"""
        payload = {
            "text": "ଭୁବନେଶ୍ୱରରେ ଧାନର ଦର କେତେ?",
            "language": "or"
        }
        response = self.app.post("/api/query",
                                 data=json.dumps(payload),
                                 content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue("ଧାନ" in data["text"] or "Paddy" in data["text"])
        self.assertTrue("ଦର" in data["text"] or "₹" in data["text"])

    def test_process_query_assamese(self):
        """Assamese language query verification (গুৱাহাটীত আলুৰ দাম কিমান?)"""
        payload = {
            "text": "গুৱাহাটীত আলুৰ দাম কিমান?",
            "language": "as"
        }
        response = self.app.post("/api/query",
                                 data=json.dumps(payload),
                                 content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue("আলু" in data["text"] or "Potato" in data["text"])
        self.assertTrue("দৰ" in data["text"] or "দাম" in data["text"] or "₹" in data["text"])

    def test_process_query_kashmiri(self):
        """Kashmiri language query verification (سوپور مَنٛز ژوٗنٛٹھ ہُنٛد قٟمَتھ کِیٛاہ چُھ؟)"""
        payload = {
            "text": "سوپور مَنٛز ژوٗنٛٹھ ہُنٛد قٟمَتھ کِیٛاہ چُھ؟",
            "language": "ks"
        }
        response = self.app.post("/api/query",
                                 data=json.dumps(payload),
                                 content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue("ژوٗنٛٹھ" in data["text"] or "Apple" in data["text"])
        self.assertTrue("قٟمَتھ" in data["text"] or "₹" in data["text"])

    def test_commodity_localization_bundles_13_languages(self):
        """Phase 2 Extended Verification: Check that commodities have all 13 language translations"""
        response = self.app.get("/api/mandi/commodities")
        self.assertEqual(response.status_code, 200)
        commodities = json.loads(response.data)
        self.assertTrue(len(commodities) >= 20)
        
        # Check Apple
        apple = next((c for c in commodities if c["commodity_name"] == "Apple"), None)
        self.assertIsNotNone(apple)
        apple_locals = json.loads(apple["local_name"])
        required_langs = ["en", "hi", "gu", "mr", "kn", "ta", "te", "ml", "pa", "bn", "or", "as", "ks"]
        for l in required_langs:
            self.assertIn(l, apple_locals)
        self.assertEqual(apple_locals["or"], "ସେଓ")
        self.assertEqual(apple_locals["as"], "আপেল")
        self.assertIn("ژوٗنٛٹھ", apple_locals["ks"])

    def test_whatsapp_twilio_webhook(self):
        payload = {
            "From": "whatsapp:+919876543210",
            "Body": "କନ୍ନଡ଼ରେ ଶିବମୋଗା ଯୋଳର ଦର",
            "NumMedia": "0"
        }
        response = self.app.post("/api/whatsapp/twilio", data=payload)
        self.assertEqual(response.status_code, 200)
    def test_enam_mandi_trade_attributes(self):
        """Phase 4 Verification: Verify e-NAM flag, arrivals, variety, and grade"""
        response = self.app.get("/api/mandi/price?state=Gujarat&district=Ahmedabad&mandi_name=Ahmedabad%20APMC%20(Chimanbhai%20Patel)&commodity_name=Apple")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get("is_enam"))
        self.assertTrue(data.get("arrivals_qty", 0) > 0)
        self.assertEqual(data.get("variety"), "Kashmiri Delicious")
        self.assertEqual(data.get("grade"), "Grade A")
        self.assertEqual(data.get("trade_type"), "e-Auction")

    def test_upag_market_outlook_endpoint(self):
        """Phase 5 Verification: Verify UPAg production, retail spread, and advisory"""
        response = self.app.get("/api/advisory/market-outlook?state=Gujarat&commodity=Apple")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("commodity"), "Apple")
        self.assertTrue("supply_outlook" in data)
        self.assertTrue(data.get("retail_price_avg", 0) > data.get("wholesale_price_avg", 0))
        self.assertTrue(data.get("retail_spread_pct", 0) > 0)
        self.assertTrue(len(data.get("advisory_recommendation", "")) > 10)

    def test_advisory_query_multilingual(self):
        """Phase 5 Verification: Query AI for selling advice / market outlook"""
        payload = {
            "text": "અમદાવાદમાં સફરજન ક્યારે વેચવું સલાહ આપો",
            "language": "gu"
        }
        response = self.app.post("/api/query",
                                 data=json.dumps(payload),
                                 content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("intent"), "advisory")
        self.assertTrue("UPAg" in data["text"] or "સલાહ" in data["text"] or "બજાર" in data["text"])

    def test_mixed_colloquial_odia_query(self):
        """Verify handling of mixed English words ('rate') within Odia queries"""
        from app.services.ai_service import AIService
        
        # 1. Native Odia with English 'rate'
        q1 = "ଭୁବନେଶ୍ୱରରେ ଧାନର rate କେତେ"
        p1 = AIService.parse_query_rule_based(q1)
        self.assertEqual(p1["language"], "or")
        self.assertEqual(p1["intent"], "price")
        self.assertEqual(p1["commodity"], "Paddy (Rice)")
        self.assertEqual(p1["district"], "Khordha")

        # 2. Native Odia with phonetic loanword 'ରେଟ୍'
        q2 = "ଭୁବନେଶ୍ୱରରେ ଧାନର ରେଟ୍ କେତେ"
        p2 = AIService.parse_query_rule_based(q2)
        self.assertEqual(p2["language"], "or")
        self.assertEqual(p2["commodity"], "Paddy (Rice)")

        # 3. Native Odia with English 'price'
        q3 = "ଭୁବନେଶ୍ୱରରେ ଧାନର price କେତେ"
        p3 = AIService.parse_query_rule_based(q3)
        self.assertEqual(p3["language"], "or")
        self.assertEqual(p3["commodity"], "Paddy (Rice)")

        # 4. Native Odia with mixed 'advisory'
        q4 = "ଭୁବନେଶ୍ୱରରେ ଧାନର advisory କଣ"
        p4 = AIService.parse_query_rule_based(q4)
        self.assertEqual(p4["language"], "or")
        self.assertEqual(p4["intent"], "advisory")

    def test_transliterated_mixed_queries(self):
        """Verify Romanized colloquial queries with regional postpositions and suffixes"""
        from app.services.ai_service import AIService

        # Odia in Latin script with attached suffix 'dhanara' and marker 're' / 'kete'
        p_odia = AIService.parse_query_rule_based("bhubaneswar re dhanara rate kete")
        self.assertEqual(p_odia["language"], "or")
        self.assertEqual(p_odia["commodity"], "Paddy (Rice)")
        self.assertEqual(p_odia["district"], "Khordha")

        # Kannada in Latin script with marker 'dalli' / 'eshtu'
        p_kn = AIService.parse_query_rule_based("shivamogga dalli maize rate eshtu")
        self.assertEqual(p_kn["language"], "kn")
        self.assertEqual(p_kn["commodity"], "Maize")
        self.assertEqual(p_kn["district"], "Shivamogga")

        # Marathi in Latin script with marker 'madhye' / 'kiti'
        p_mr = AIService.parse_query_rule_based("pune madhye kanda rate kiti ahe")
        self.assertEqual(p_mr["language"], "mr")
        self.assertEqual(p_mr["commodity"], "Onion")
        self.assertEqual(p_mr["district"], "Pune")

    def test_chatbot_response_for_mixed_query(self):
        """Test end-to-end API response for mixed Odia query with English 'rate'"""
        payload = {"text": "ଭୁବନେଶ୍ୱରରେ ଧାନର rate କେତେ"}
        response = self.app.post("/api/query",
                                 data=json.dumps(payload),
                                 content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("detected_language"), "or")
        self.assertEqual(data.get("commodity"), "Paddy (Rice)")
        # Response should be formulated in Odia with e-NAM details
        self.assertIn("ମଣ୍ଡିରେ", data["text"])
        self.assertIn("e-NAM", data["text"])

    def test_negative_response_when_commodity_not_found(self):
        """Verify negative response in all languages when price asked is not found"""
        from app.services.ai_service import AIService

        # 1. English query for sunflower in Delhi mandi
        p_en = AIService.parse_query_rule_based("what is the rate of sunflowers in delhi mandi")
        self.assertEqual(p_en["intent"], "price")
        self.assertEqual(p_en["commodity"], "Sunflower")
        self.assertEqual(p_en["district"], "North Delhi")

        res_en = self.app.post("/api/query",
                               data=json.dumps({"text": "what is the rate of sunflowers in delhi mandi"}),
                               content_type="application/json")
        self.assertEqual(res_en.status_code, 200)
        data_en = json.loads(res_en.data)
        self.assertIn("could not find any price records for Sunflower in Azadpur APMC", data_en["text"])
        self.assertIn("Would you like to check prices for other crops", data_en["text"])

        # 2. Hindi query for sunflower in Delhi mandi
        res_hi = self.app.post("/api/query",
                               data=json.dumps({"text": "दिल्ली मंडी में सूरजमुखी का भाव क्या है"}),
                               content_type="application/json")
        self.assertEqual(res_hi.status_code, 200)
        data_hi = json.loads(res_hi.data)
        self.assertIn("कोई भाव नहीं मिला", data_hi["text"])
        self.assertIn("क्या आप अन्य फसलों", data_hi["text"])

        # 3. Odia query for sunflower in Delhi mandi
        res_or = self.app.post("/api/query",
                               data=json.dumps({"text": "ଦିଲ୍ଲୀ ମଣ୍ଡିରେ ସୂର୍ଯ୍ୟମୁଖୀ ଦର କେତେ"}),
                               content_type="application/json")
        self.assertEqual(res_or.status_code, 200)
        data_or = json.loads(res_or.data)
        self.assertIn("କୌଣସି ଦର ରେକର୍ଡ ମିଳିଲା ନାହିଁ", data_or["text"])
        self.assertIn("ଆପଣ ଅନ୍ୟ କୌଣସି ଫସଲ", data_or["text"])

        # 4. Universal negative test case: Non-agricultural commodity 'Gold' in Delhi
        p_gold = AIService.parse_query_rule_based("what is the rate of gold in delhi mandi")
        self.assertEqual(p_gold["intent"], "price")
        self.assertEqual(p_gold["commodity"], "Gold")
        self.assertEqual(p_gold["district"], "North Delhi")

        res_gold = self.app.post("/api/query",
                                 data=json.dumps({"text": "what is the rate of gold in delhi mandi"}),
                                 content_type="application/json")
        self.assertEqual(res_gold.status_code, 200)
        data_gold = json.loads(res_gold.data)
        self.assertIn("could not find any price records for Gold", data_gold["text"])
        self.assertIn("Would you like to check prices for other crops", data_gold["text"])

        # 5. Universal negative test case: Arbitrary multi-word crop 'Dragon Fruit' in Shimoga
        p_df = AIService.parse_query_rule_based("what is the price of dragon fruit in shimoga")
        self.assertEqual(p_df["intent"], "price")
        self.assertEqual(p_df["commodity"], "Dragon Fruit")

        res_df = self.app.post("/api/query",
                               data=json.dumps({"text": "what is the price of dragon fruit in shimoga"}),
                               content_type="application/json")
        self.assertEqual(res_df.status_code, 200)
        data_df = json.loads(res_df.data)
        self.assertIn("could not find any price records for Dragon Fruit in Shimoga APMC", data_df["text"])

        # 6. Indic arbitrary non-mandi commodity: 'सोने' (Gold) in Hindi
        p_hi_gold = AIService.parse_query_rule_based("दिल्ली मंडी में सोने का भाव क्या है")
        self.assertEqual(p_hi_gold["commodity"], "सोने")
        res_hi_gold = self.app.post("/api/query",
                                    data=json.dumps({"text": "दिल्ली मंडी में सोने का भाव क्या है"}),
                                    content_type="application/json")
        self.assertEqual(res_hi_gold.status_code, 200)
        data_hi_gold = json.loads(res_hi_gold.data)
        self.assertIn("सोने के लिए कोई भाव नहीं मिला", data_hi_gold["text"])

        # 7. Indic arbitrary non-mandi commodity: 'ସୁନା' (Gold) in Odia
        p_or_gold = AIService.parse_query_rule_based("ଦିଲ୍ଲୀ ମଣ୍ଡିରେ ସୁନା ଦର କେତେ")
        self.assertEqual(p_or_gold["commodity"], "ସୁନା")
        res_or_gold = self.app.post("/api/query",
                                    data=json.dumps({"text": "ଦିଲ୍ଲୀ ମଣ୍ଡିରେ ସୁନା ଦର କେତେ"}),
                                    content_type="application/json")
        self.assertEqual(res_or_gold.status_code, 200)
        data_or_gold = json.loads(res_or_gold.data)
        self.assertIn("ସୁନା ପାଇଁ କୌଣସି ଦର ରେକର୍ଡ ମିଳିଲା ନାହିଁ", data_or_gold["text"])

    def test_price_template_hyperlinks_and_in_place_links(self):
        """Verify that price responses use [Click Here] markdown hyperlink syntax to prevent plain text URL overflows and support in-place navigation"""
        # 1. English query
        res_en = self.app.post("/api/query",
                               data=json.dumps({"text": "what is the wheat rate in shimoga today?", "language": "en"}),
                               content_type="application/json")
        self.assertEqual(res_en.status_code, 200)
        text_en = json.loads(res_en.data)["text"]
        self.assertIn("📊 To view 7-day price trends and compare nearby mandis, [Click Here]", text_en)
        self.assertIn("?tab=mandi&mandi=Shimoga%20APMC&commodity=Wheat", text_en)

        # 2. Hindi query
        res_hi = self.app.post("/api/query",
                               data=json.dumps({"text": "शिमोगा में गेहूं का भाव क्या है?", "language": "hi"}),
                               content_type="application/json")
        self.assertEqual(res_hi.status_code, 200)
        text_hi = json.loads(res_hi.data)["text"]
        self.assertIn("📊 7 दिनों के भाव के रुझान और मंडियों की तुलना देखने के लिए, [यहाँ क्लिक करें]", text_hi)
        self.assertIn("?tab=mandi&mandi=Shimoga%20APMC&commodity=Wheat", text_hi)

        # 3. Odia query
        res_or = self.app.post("/api/query",
                               data=json.dumps({"text": "ଭୁବନେଶ୍ୱରରେ ଧାନର ଦର କେତେ?", "language": "or"}),
                               content_type="application/json")
        self.assertEqual(res_or.status_code, 200)
        text_or = json.loads(res_or.data)["text"]
        self.assertIn("📊 ବିଗତ ୭ ଦିନର ଦର ଏବଂ ତୁଳନା ଦେଖିବା ପାଇଁ, [ଏଠାରେ କ୍ଲିକ୍ କରନ୍ତୁ]", text_or)
        self.assertIn("?tab=mandi&mandi=Bhubaneswar%20APMC", text_or)

if __name__ == '__main__':
    unittest.main()

