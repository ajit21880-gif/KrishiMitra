import os
import sys
import unittest
import json

# Add backend/ to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

    def test_mandi_prices_indore(self):
        response = self.app.get("/api/mandi/price?state=Madhya%20Pradesh&district=Indore&mandi_name=Indore%20APMC%20(Choithram)&commodity_name=Wheat")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["commodity"], "Wheat")
        self.assertTrue(data["modal_price"] > 0)

    def test_process_query(self):
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

    def test_whatsapp_twilio_webhook(self):
        payload = {
            "From": "whatsapp:+919876543210",
            "Body": "ಕನ್ನಡದಲ್ಲಿ ಶಿವಮೊಗ್ಗ ಜೋಳದ ಬೆಲೆ",
            "NumMedia": "0"
        }
        response = self.app.post("/api/whatsapp/twilio", data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("xml", response.headers["Content-Type"].lower())

    def test_activation_triggers_multilingual(self):
        # 1. Test "Hi KrishiMitra" activation in English
        r_en = self.app.post("/api/query", json={"text": "Hi KrishiMitra"})
        self.assertIn("Welcome to KrishiMitra AI", r_en.get_json()["text"])

        # 2. Test "नमस्ते कृषिमित्र" in Hindi
        r_hi = self.app.post("/api/query", json={"text": "नमस्ते कृषिमित्र"})
        self.assertIn("कृषिमित्र एआई में आपका स्वागत है", r_hi.get_json()["text"])

        # 3. Test "ನಮಸ್ಕಾರ ಕೃಷಿಮಿತ್ರ" in Kannada
        r_kn = self.app.post("/api/query", json={"text": "ನಮಸ್ಕಾರ ಕೃಷಿಮಿತ್ರ"})
        self.assertIn("ಕೃಷಿಮಿತ್ರ AI ಗೆ ಸ್ವಾಗತ", r_kn.get_json()["text"])

        # 4. Test "வணக்கம் கிருஷிமித்ரா" in Tamil
        r_ta = self.app.post("/api/query", json={"text": "வணக்கம் கிருஷிமித்ரா"})
        self.assertIn("கிருஷிமித்ரா AI க்கு நல்வரவு", r_ta.get_json()["text"])

    def test_sugar_delhi_query(self):
        r = self.app.post("/api/query", json={"text": "What's the price of sugar in delhi?"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("Sugar", r.json["text"])
        self.assertTrue("Azadpur" in r.json["text"] or "Delhi" in r.json["text"])

    def test_rice_jharkhand_query(self):
        r = self.app.post("/api/query", json={"text": "What is price of rice in jharkhand"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue("Rice" in r.json["text"] or "Paddy" in r.json["text"])

if __name__ == '__main__':
    unittest.main()
