import os
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Local cache for Government API responses: key -> (timestamp, data)
_api_cache: Dict[str, Any] = {}
CACHE_EXPIRY = timedelta(minutes=30)

class MandiService:
    @staticmethod
    def get_live_mandi_prices_from_gov(
        api_key: str, 
        state: str, 
        district: str, 
        mandi_name: str, 
        commodity: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetches live mandi prices from the official data.gov.in / AGMARKNET API.
        """
        cache_key = f"{state}:{district}:{mandi_name}:{commodity}"
        
        # Check cache
        if cache_key in _api_cache:
            cached_time, cached_data = _api_cache[cache_key]
            if datetime.now() - cached_time < CACHE_EXPIRY:
                print("Returning cached government data.")
                return cached_data
                
        # Call Official API
        try:
            url = "https://api.data.gov.in/resource/9ef84281-22f3-497d-aa5d-8c6c52d77290"
            params = {
                "api-key": api_key,
                "format": "json",
                "filters[state]": state,
                "filters[district]": district,
                "filters[market]": mandi_name,
                "filters[commodity]": commodity,
                "limit": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                if records:
                    record = records[0]
                    result = {
                        "commodity": record.get("commodity"),
                        "mandi": record.get("market"),
                        "date": record.get("arrival_date"),
                        "min_price": float(record.get("min_price", 0)),
                        "modal_price": float(record.get("modal_price", 0)),
                        "max_price": float(record.get("max_price", 0)),
                        "source": "AGMARKNET (data.gov.in Live API)",
                        "last_updated": datetime.now().isoformat()
                    }
                    _api_cache[cache_key] = (datetime.now(), result)
                    return result
            else:
                print(f"data.gov.in API returned error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Error calling data.gov.in API: {e}")
            
        return None

    @classmethod
    def get_mandi_price(
        cls, 
        conn: sqlite3.Connection, 
        state: str, 
        district: str, 
        mandi_name: str, 
        commodity_name: str
    ) -> Dict[str, Any]:
        """
        Retrieves mandi price from live government API or falls back to sqlite3 database.
        """
        api_key = os.environ.get("DATAGOV_API_KEY")
        if api_key:
            live_data = cls.get_live_mandi_prices_from_gov(api_key, state, district, mandi_name, commodity_name)
            if live_data:
                return live_data
                
        cursor = conn.cursor()
        
        # Fallback to local DB seeded daily_prices
        cursor.execute(
            "SELECT id, mandi_name, state, district FROM mandis WHERE state LIKE ? AND district LIKE ? AND mandi_name LIKE ?",
            (state, district, mandi_name)
        )
        mandi = cursor.fetchone()
        
        cursor.execute(
            "SELECT id, commodity_name FROM commodities WHERE commodity_name LIKE ?",
            (commodity_name,)
        )
        commodity = cursor.fetchone()
        
        if mandi and commodity:
            cursor.execute(
                "SELECT * FROM daily_prices WHERE mandi_id = ? AND commodity_id = ? ORDER BY date DESC LIMIT 1",
                (mandi["id"], commodity["id"])
            )
            price_record = cursor.fetchone()
            
            if price_record:
                return {
                    "commodity": commodity["commodity_name"],
                    "mandi": mandi["mandi_name"],
                    "date": price_record["date"],
                    "min_price": price_record["min_price"],
                    "modal_price": price_record["modal_price"],
                    "max_price": price_record["max_price"],
                    "source": price_record["source"] + " (Seeded Database)",
                    "last_updated": price_record["date"]
                }
                
        return {
            "commodity": commodity_name,
            "mandi": mandi_name,
            "date": datetime.now().date().isoformat(),
            "min_price": 0.0,
            "modal_price": 0.0,
            "max_price": 0.0,
            "source": "No price record found in source APIs/DB",
            "last_updated": datetime.now().date().isoformat()
        }
        
    @staticmethod
    def get_price_trends(
        conn: sqlite3.Connection,
        mandi_name: str,
        commodity_name: str
    ) -> List[Dict[str, Any]]:
        """
        Fetches historical price trends for the last 7 days from sqlite3 database.
        """
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM mandis WHERE mandi_name LIKE ?", (mandi_name,))
        mandi = cursor.fetchone()
        
        cursor.execute("SELECT id FROM commodities WHERE commodity_name LIKE ?", (commodity_name,))
        commodity = cursor.fetchone()
        
        if not mandi or not commodity:
            return []
            
        cursor.execute(
            "SELECT date, min_price, modal_price, max_price FROM daily_prices WHERE mandi_id = ? AND commodity_id = ? ORDER BY date ASC",
            (mandi["id"], commodity["id"])
        )
        prices = cursor.fetchall()
        
        return [
            {
                "date": p["date"],
                "min_price": p["min_price"],
                "modal_price": p["modal_price"],
                "max_price": p["max_price"]
            } for p in prices
        ]
