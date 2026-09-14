import os
import time
import json
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BhashiniService:
    """
    Digital India Bhashini AI Integration Service.
    Provides Automated Speech Recognition (ASR), Neural Machine Translation (NMT),
    and Text-to-Speech (TTS) for Indian languages using ULCA & Dhruva Pipeline APIs.
    """
    CONFIG_URL = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
    DEFAULT_PIPELINE_ID = "64392f96daac500b55c543cd"

    # In-memory cache for pipeline configurations: key -> (timestamp, data)
    _config_cache: Dict[str, Any] = {}
    _CACHE_TTL = 3600 # 1 hour

    @classmethod
    def get_credentials(cls) -> Dict[str, str]:
        user_id = os.environ.get("BHASHINI_USER_ID", "b98e075db1cb4d6f864ba5aa1e4ac37f")
        ulca_key = os.environ.get("BHASHINI_ULCA_API_KEY", "525a9b9f9d-0fb4-4c9e-81d1-c6af47fba143")
        inference_key = os.environ.get("BHASHINI_INFERENCE_KEY", "i2xBmwcC7aRA5ezAA6UlDz5lVYGlbco1YFITOPCDmblR1mf8r5XTXoYntaEd0iXP")
        pipeline_id = os.environ.get("BHASHINI_PIPELINE_ID", cls.DEFAULT_PIPELINE_ID)
        return {
            "userID": user_id,
            "ulcaApiKey": ulca_key,
            "inferenceKey": inference_key,
            "pipelineId": pipeline_id
        }

    @classmethod
    def is_available(cls) -> bool:
        creds = cls.get_credentials()
        return bool(creds["userID"] and creds["ulcaApiKey"] and creds["inferenceKey"])

    @classmethod
    def _fetch_pipeline_config(cls, task_type: str, source_lang: str, target_lang: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch and cache pipeline config (serviceId, compute URL, auth headers) for specific task"""
        cache_key = f"{task_type}:{source_lang}:{target_lang or ''}"
        now = time.time()

        if cache_key in cls._config_cache:
            cached_time, cached_data = cls._config_cache[cache_key]
            if now - cached_time < cls._CACHE_TTL:
                return cached_data

        creds = cls.get_credentials()
        headers = {
            "userID": creds["userID"],
            "ulcaApiKey": creds["ulcaApiKey"],
            "Content-Type": "application/json"
        }

        task_config: Dict[str, Any] = {"taskType": task_type}
        if task_type == "translation":
            task_config["config"] = {
                "language": {
                    "sourceLanguage": source_lang,
                    "targetLanguage": target_lang or "en"
                }
            }
        else:
            task_config["config"] = {
                "language": {
                    "sourceLanguage": source_lang
                }
            }

        payload = {
            "pipelineTasks": [task_config],
            "pipelineRequestConfig": {
                "pipelineId": creds["pipelineId"]
            }
        }

        try:
            resp = requests.post(cls.CONFIG_URL, json=payload, headers=headers, timeout=12)
            if resp.status_code != 200:
                logger.warning(f"Bhashini config error {resp.status_code}: {resp.text[:200]}")
                return None

            data = resp.json()
            endpoint_info = data.get("pipelineInferenceAPIEndPoint", {})
            compute_url = endpoint_info.get("callbackUrl")
            auth_info = endpoint_info.get("inferenceApiKey", {})

            # Fallback to direct inference key if returned empty
            auth_header_name = auth_info.get("name") or "Authorization"
            auth_header_val = auth_info.get("value") or creds["inferenceKey"]

            task_configs = data.get("pipelineResponseConfig", [])
            if not task_configs:
                return None

            configs = task_configs[0].get("config", [])
            if not configs:
                return None

            service_id = configs[0].get("serviceId")
            if not service_id or not compute_url:
                return None

            result = {
                "service_id": service_id,
                "compute_url": compute_url,
                "auth_header": {
                    "name": auth_header_name,
                    "value": auth_header_val
                },
                "raw_config": configs[0]
            }

            cls._config_cache[cache_key] = (now, result)
            return result
        except Exception as e:
            logger.exception(f"Error fetching Bhashini pipeline config: {e}")
            return None

    @classmethod
    def speech_to_text(cls, audio_base64: str, source_lang: str = "hi", audio_format: str = "wav", sampling_rate: int = 16000) -> Optional[Dict[str, Any]]:
        """
        Transcribe Indian speech audio using Bhashini ASR.
        Accepts base64-encoded audio. Returns dict with 'text' and 'language'.
        """
        if not audio_base64:
            return None

        # Clean base64 header if present (e.g. data:audio/wav;base64,...)
        if "," in audio_base64:
            audio_base64 = audio_base64.split(",", 1)[1]

        cfg = cls._fetch_pipeline_config("asr", source_lang)
        if not cfg:
            logger.warning(f"No Bhashini ASR config found for lang: {source_lang}")
            return None

        headers = {
            cfg["auth_header"]["name"]: cfg["auth_header"]["value"],
            "Content-Type": "application/json"
        }

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang
                        },
                        "serviceId": cfg["service_id"],
                        "audioFormat": audio_format.lower(),
                        "samplingRate": sampling_rate
                    }
                }
            ],
            "inputData": {
                "audio": [
                    {
                        "audioContent": audio_base64
                    }
                ]
            }
        }

        try:
            resp = requests.post(cfg["compute_url"], json=payload, headers=headers, timeout=20)
            if resp.status_code != 200:
                logger.warning(f"Bhashini ASR compute error {resp.status_code}: {resp.text[:200]}")
                return None

            data = resp.json()
            pipeline_resp = data.get("pipelineResponse", [])
            if not pipeline_resp:
                return None

            output = pipeline_resp[0].get("output", [])
            if output and "source" in output[0]:
                transcribed_text = output[0]["source"].strip()
                return {
                    "text": transcribed_text,
                    "language": source_lang
                }
        except Exception as e:
            logger.exception(f"Bhashini ASR transcription error: {e}")

        return None

    @classmethod
    def translate_text(cls, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate text from source_lang to target_lang using Bhashini NMT.
        """
        if not text or not text.strip():
            return text

        if source_lang == target_lang:
            return text

        cfg = cls._fetch_pipeline_config("translation", source_lang, target_lang)
        if not cfg:
            logger.warning(f"No Bhashini translation config for {source_lang} -> {target_lang}")
            return None

        headers = {
            cfg["auth_header"]["name"]: cfg["auth_header"]["value"],
            "Content-Type": "application/json"
        }

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            "targetLanguage": target_lang
                        },
                        "serviceId": cfg["service_id"]
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": text
                    }
                ]
            }
        }

        try:
            resp = requests.post(cfg["compute_url"], json=payload, headers=headers, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"Bhashini NMT compute error {resp.status_code}: {resp.text[:200]}")
                return None

            data = resp.json()
            pipeline_resp = data.get("pipelineResponse", [])
            if not pipeline_resp:
                return None

            output = pipeline_resp[0].get("output", [])
            if output and "target" in output[0]:
                return output[0]["target"].strip()
        except Exception as e:
            logger.exception(f"Bhashini NMT error: {e}")

        return None

    @classmethod
    def text_to_speech(cls, text: str, source_lang: str, gender: str = "female") -> Optional[str]:
        """
        Synthesize natural speech audio for Indian language text using Bhashini TTS.
        Returns base64 encoded audio string (WAV format, playable directly).
        """
        if not text or not text.strip():
            return None

        # Clean text: remove markdown links and formatting symbols for natural speech
        clean_text = text
        import re
        clean_text = re.sub(r'\[([^\[\]()]{1,300})\]\(([^\[\]()]{1,500})\)', r'\1', clean_text)
        clean_text = re.sub(r'[\*\_#`]', '', clean_text)
        clean_text = clean_text.strip()
        if not clean_text:
            return None

        cfg = cls._fetch_pipeline_config("tts", source_lang)
        if not cfg:
            logger.warning("No Bhashini TTS config for requested language")
            return None

        headers = {
            cfg["auth_header"]["name"]: cfg["auth_header"]["value"],
            "Content-Type": "application/json"
        }

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang
                        },
                        "serviceId": cfg["service_id"],
                        "gender": gender
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": clean_text
                    }
                ]
            }
        }

        try:
            resp = requests.post(cfg["compute_url"], json=payload, headers=headers, timeout=20)
            if resp.status_code != 200:
                logger.warning(f"Bhashini TTS compute error {resp.status_code}: {resp.text[:200]}")
                return None

            data = resp.json()
            pipeline_resp = data.get("pipelineResponse", [])
            if not pipeline_resp:
                return None

            audio_data = pipeline_resp[0].get("audio", [])
            if audio_data and "audioContent" in audio_data[0]:
                audio_base64 = audio_data[0]["audioContent"]
                if audio_base64:
                    return audio_base64.strip()
        except Exception as e:
            logger.exception(f"Bhashini TTS error: {e}")

        return None
