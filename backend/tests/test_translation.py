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

from app.services.translation_service import TranslationService
from app.core.database import get_db_connection
from app.main import app

class TestTranslationService(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_state_translations(self):
        """Verify State translations for Odisha, Karnataka, Gujarat, Maharashtra"""
        self.assertEqual(TranslationService.get_state_translation("Odisha", "or"), "ଓଡ଼ିଶା")
        self.assertEqual(TranslationService.get_state_translation("Karnataka", "kn"), "ಕರ್ನಾಟಕ")
        self.assertEqual(TranslationService.get_state_translation("Gujarat", "gu"), "ગુજરાત")
        self.assertEqual(TranslationService.get_state_translation("Maharashtra", "mr"), "महाराष्ट्र")
        self.assertEqual(TranslationService.get_state_translation("Karnataka", "en"), "Karnataka")

    def test_district_translations(self):
        """Verify District translations for key agricultural districts"""
        self.assertEqual(TranslationService.get_district_translation("Shivamogga", "kn"), "ಶಿವಮೊಗ್ಗ")
        self.assertEqual(TranslationService.get_district_translation("Davanagere", "kn"), "ದಾವಣಗೆರೆ")
        self.assertEqual(TranslationService.get_district_translation("Bengaluru", "kn"), "ಬೆಂಗಳೂರು")
        self.assertEqual(TranslationService.get_district_translation("Kantabaji", "or"), "କଣ୍ଟାବାଞ୍ଜି")

    def test_commodity_translations_known(self):
        """Verify commodity translations for Pumpkin, Brinjal, Snakeguard, Kutki, Bhindi"""
        p_trans = TranslationService.get_or_create_commodity_translations("Pumpkin")
        self.assertEqual(p_trans["kn"], "ಕುಂಬಳಕಾಯಿ")
        self.assertTrue("ବୋଇତାଳୁ" in p_trans["or"] or "କଖାରୁ" in p_trans["or"])
        self.assertEqual(p_trans["hi"], "कद्दू")

        b_trans = TranslationService.get_or_create_commodity_translations("Brinjal")
        self.assertEqual(b_trans["kn"], "ಬದನೆಕಾಯಿ")
        self.assertEqual(b_trans["or"], "ବାଇଗଣ")

        s_trans = TranslationService.get_or_create_commodity_translations("Snakeguard")
        self.assertEqual(s_trans["kn"], "ಪಡವಲಕಾಯಿ")
        self.assertEqual(s_trans["or"], "ଛଚିନ୍ଦ୍ରା")

        k_trans = TranslationService.get_or_create_commodity_translations("Kutki")
        self.assertEqual(k_trans["kn"], "ಸಾಮೆ")

    def test_locations_endpoint(self):
        """Verify GET /api/translations/locations returns states and districts"""
        res = self.app.get("/api/translations/locations")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("states", data)
        self.assertIn("districts", data)
        self.assertIn("Odisha", data["states"])
        self.assertEqual(data["states"]["Odisha"]["or"], "ଓଡ଼ିଶା")

    def test_database_commodities_enriched(self):
        """Verify all commodities in the database have valid 13-language JSON in local_name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT commodity_name, local_name FROM commodities")
        rows = cursor.fetchall()
        conn.close()

        for r in rows:
            name = r["commodity_name"]
            local = r["local_name"]
            self.assertTrue(local.startswith("{"), f"Commodity '{name}' should have JSON local_name")
            data = json.loads(local)
            self.assertTrue("kn" in data, f"Commodity '{name}' should have Kannada translation")
            self.assertTrue("or" in data, f"Commodity '{name}' should have Odia translation")

if __name__ == "__main__":
    unittest.main()
