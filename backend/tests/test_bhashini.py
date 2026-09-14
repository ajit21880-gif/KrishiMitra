import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Reconfigure stdout for Indic UTF-8 characters if running on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend/ to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["TESTING"] = "1"

from app.services.bhashini_service import BhashiniService
from app.services.ai_service import AIService
from app.main import app

class TestBhashiniIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_bhashini_credentials_configured(self):
        """Verify Bhashini credentials are present and service is reported available"""
        creds = BhashiniService.get_credentials()
        self.assertTrue(bool(creds["userID"]), "Bhashini User ID should be set")
        self.assertTrue(bool(creds["ulcaApiKey"]), "Bhashini ULCA API key should be set")
        self.assertTrue(bool(creds["inferenceKey"]), "Bhashini Inference key should be set")
        self.assertTrue(BhashiniService.is_available(), "BhashiniService should be available")

    @patch("requests.post")
    def test_pipeline_config_discovery(self, mock_post):
        """Verify pipeline config discovery parses callback URL and service ID"""
        # Clear cache for isolated test
        BhashiniService._config_cache.clear()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "pipelineInferenceAPIEndPoint": {
                "callbackUrl": "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
                "inferenceApiKey": {"name": "Authorization", "value": "mock_token"}
            },
            "pipelineResponseConfig": [{
                "taskType": "translation",
                "config": [{"serviceId": "ai4bharat/indictrans-v2-all-gpu--fairseq"}]
            }]
        }
        mock_post.return_value = mock_resp

        cfg = BhashiniService._fetch_pipeline_config("translation", "en", "hi")
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg["service_id"], "ai4bharat/indictrans-v2-all-gpu--fairseq")
        self.assertEqual(cfg["compute_url"], "https://dhruva-api.bhashini.gov.in/services/inference/pipeline")

    @patch.object(BhashiniService, "_fetch_pipeline_config")
    @patch("requests.post")
    def test_translate_text(self, mock_post, mock_cfg):
        """Verify NMT translation correctly returns translated target text"""
        mock_cfg.return_value = {
            "service_id": "test_nmt",
            "compute_url": "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
            "auth_header": {"name": "Authorization", "value": "test_key"}
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "pipelineResponse": [{
                "output": [{"source": "Tomato", "target": "टमाटर"}]
            }]
        }
        mock_post.return_value = mock_resp

        translated = BhashiniService.translate_text("Tomato", "en", "hi")
        self.assertEqual(translated, "टमाटर")

    @patch.object(BhashiniService, "_fetch_pipeline_config")
    @patch("requests.post")
    def test_text_to_speech(self, mock_post, mock_cfg):
        """Verify TTS returns base64 audio string"""
        mock_cfg.return_value = {
            "service_id": "test_tts",
            "compute_url": "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
            "auth_header": {"name": "Authorization", "value": "test_key"}
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "pipelineResponse": [{
                "audio": [{"audioContent": "UklGRi4AAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="}]
            }]
        }
        mock_post.return_value = mock_resp

        audio_b64 = BhashiniService.text_to_speech("टमाटर का भाव ₹2000 प्रति क्विंटल है", source_lang="hi")
        self.assertIsNotNone(audio_b64)
        self.assertTrue(len(audio_b64) > 10)

    @patch.object(BhashiniService, "_fetch_pipeline_config")
    @patch("requests.post")
    def test_speech_to_text(self, mock_post, mock_cfg):
        """Verify ASR transcription parses audio content to text"""
        mock_cfg.return_value = {
            "service_id": "test_asr",
            "compute_url": "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
            "auth_header": {"name": "Authorization", "value": "test_key"}
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "pipelineResponse": [{
                "output": [{"source": "इंदौर में गेहूं का भाव क्या है"}]
            }]
        }
        mock_post.return_value = mock_resp

        res = BhashiniService.speech_to_text("UklGRi4AAABXQVZFZm10IBAAAAABAAEA", source_lang="hi")
        self.assertIsNotNone(res)
        self.assertEqual(res["text"], "इंदौर में गेहूं का भाव क्या है")
        self.assertEqual(res["language"], "hi")

    @patch.object(BhashiniService, "speech_to_text")
    def test_voice_transcribe_endpoint(self, mock_stt):
        """Verify POST /api/voice/transcribe endpoint returns transcribed text"""
        mock_stt.return_value = {"text": "पुण्यात कांद्याचा भाव काय आहे", "language": "mr"}

        resp = self.app.post("/api/voice/transcribe", json={
            "audio": "UklGRi4AAABXQVZFZm10IBAAAAABAAEA",
            "language": "mr"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["text"], "पुण्यात कांद्याचा भाव काय आहे")
        self.assertEqual(data["language"], "mr")

    @patch.object(BhashiniService, "text_to_speech")
    def test_voice_synthesize_endpoint(self, mock_tts):
        """Verify POST /api/voice/synthesize endpoint returns audio base64"""
        mock_tts.return_value = "UklGRi4AAABXQVZFZm10IBAAAAABAAEA"

        resp = self.app.post("/api/voice/synthesize", json={
            "text": "धान का भाव ₹2300 है",
            "language": "hi"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["audio_base64"], "UklGRi4AAABXQVZFZm10IBAAAAABAAEA")
        self.assertEqual(data["mime_type"], "audio/wav")

    @patch.object(BhashiniService, "translate_text")
    def test_voice_translate_endpoint(self, mock_translate):
        """Verify POST /api/voice/translate endpoint returns translated text"""
        mock_translate.return_value = "Wheat"

        resp = self.app.post("/api/voice/translate", json={
            "text": "गेहूं",
            "source_language": "hi",
            "target_language": "en"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["translated_text"], "Wheat")

    def test_debug_endpoint_reports_bhashini(self):
        """Verify GET /api/debug reports bhashini_configured as True"""
        resp = self.app.get("/api/debug")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("bhashini_configured", data)
        self.assertTrue(data["bhashini_configured"])

if __name__ == "__main__":
    unittest.main()
