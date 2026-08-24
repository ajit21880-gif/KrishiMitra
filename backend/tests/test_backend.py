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

if __name__ == '__main__':
    unittest.main()
