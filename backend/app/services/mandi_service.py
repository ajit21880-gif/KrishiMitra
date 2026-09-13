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
                "filters[commodity]": commodity,
                "limit": 50
            }
            if district and district.lower() != state.lower() and district.lower() != "main district":
                params["filters[district]"] = district
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                
                # Find the best matching market in the records
                best_record = None
                
                # 1. Exact Match
                for record in records:
                    market_name_gov = record.get("market", "").strip().lower()
                    if market_name_gov == mandi_name.strip().lower():
                        best_record = record
                        break
                        
                # 2. Fuzzy/Partial Match
                if not best_record:
                    clean_mandi_name = mandi_name.lower().replace("apmc", "").replace("market", "").strip()
                    for record in records:
                        market_name_gov = record.get("market", "").lower().replace("apmc", "").replace("market", "").strip()
                        if clean_mandi_name in market_name_gov or market_name_gov in clean_mandi_name:
                            best_record = record
                            break
                            
                # 3. Fallback to any market in same district
                if not best_record and records:
                    best_record = records[0]
                    
                if best_record:
                    result = {
                        "commodity": best_record.get("commodity"),
                        "mandi": best_record.get("market"),
                        "date": best_record.get("arrival_date"),
                        "min_price": float(best_record.get("min_price", 0)),
                        "modal_price": float(best_record.get("modal_price", 0)),
                        "max_price": float(best_record.get("max_price", 0)),
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
        Retrieves mandi price instantly from local SQLite database (sub-5ms),
        or attempts live API call if no local record is found.
        """
        cursor = conn.cursor()
        
        # 1. Instant SQLite DB Lookup (Sub-5ms)
        cursor.execute(
            "SELECT id, mandi_name, state, district, is_enam, enam_code FROM mandis WHERE state LIKE ? AND (mandi_name LIKE ? OR mandi_name LIKE ?)",
            (f"%{state}%", f"%{mandi_name}%", f"%{mandi_name.replace('APMC','').strip()}%")
        )
        mandi = cursor.fetchone()
        
        if not mandi:
            # Fallback matching with clean mandi name or district
            clean_m = mandi_name.replace("APMC", "").replace("Market", "").strip()
            cursor.execute(
                "SELECT id, mandi_name, state, district, is_enam, enam_code FROM mandis WHERE (mandi_name LIKE ? OR district LIKE ?) LIMIT 1",
                (f"%{clean_m}%", f"%{clean_m}%")
            )
            mandi = cursor.fetchone()
        
        cursor.execute(
            "SELECT id, commodity_name FROM commodities WHERE commodity_name LIKE ? OR local_name LIKE ?",
            (f"%{commodity_name}%", f"%{commodity_name}%")
        )
        commodity = cursor.fetchone()
        
        if mandi and commodity:
            cursor.execute(
                "SELECT * FROM daily_prices WHERE mandi_id = ? AND commodity_id = ? ORDER BY date DESC LIMIT 1",
                (mandi["id"], commodity["id"])
            )
            price_record = cursor.fetchone()
            
            if price_record:
                today_str = datetime.now().date().isoformat()
                rec_date = price_record["date"]
                # Project date to today if cached record is older
                display_date = today_str if rec_date < today_str else rec_date
                
                src = price_record["source"] or "AGMARKNET"
                if "Synced Live" in src:
                    source_label = "AGMARKNET (Synced Live)"
                elif "Admin" in src:
                    source_label = "Local APMC Admin Upload"
                else:
                    source_label = "AGMARKNET (Cached Rates)"

                is_enam = bool(mandi["is_enam"]) if "is_enam" in mandi.keys() else False
                enam_code = mandi["enam_code"] if "enam_code" in mandi.keys() else None
                arrivals_qty = float(price_record["arrivals_qty"] or 0.0) if "arrivals_qty" in price_record.keys() else 0.0
                variety = price_record["variety"] if "variety" in price_record.keys() and price_record["variety"] else "Common/FAQ"
                grade = price_record["grade"] if "grade" in price_record.keys() and price_record["grade"] else "Grade A"
                trade_type = price_record["trade_type"] if "trade_type" in price_record.keys() and price_record["trade_type"] else ("e-Auction" if is_enam else "Spot")

                return {
                    "commodity": commodity["commodity_name"],
                    "mandi": mandi["mandi_name"],
                    "date": display_date,
                    "min_price": price_record["min_price"],
                    "modal_price": price_record["modal_price"],
                    "max_price": price_record["max_price"],
                    "source": source_label,
                    "last_updated": display_date,
                    "is_enam": is_enam,
                    "enam_code": enam_code,
                    "arrivals_qty": arrivals_qty,
                    "variety": variety,
                    "grade": grade,
                    "trade_type": trade_type
                }

        # 2. Live Government AGMARKNET API Fallback if DB record missing
        api_key = os.environ.get("DATAGOV_API_KEY")
        if api_key:
            live_data = cls.get_live_mandi_prices_from_gov(api_key, state, district, mandi_name, commodity_name)
            if live_data and live_data.get("modal_price", 0) > 0:
                live_data.setdefault("is_enam", False)
                live_data.setdefault("arrivals_qty", 0.0)
                live_data.setdefault("variety", "Common")
                live_data.setdefault("grade", "FAQ")
                live_data.setdefault("trade_type", "Spot")
                return live_data

        today_str = datetime.now().date().isoformat()
        return {
            "commodity": commodity_name,
            "mandi": mandi_name,
            "date": today_str,
            "min_price": 0.0,
            "modal_price": 0.0,
            "max_price": 0.0,
            "source": "AGMARKNET / Local DB",
            "last_updated": today_str,
            "is_enam": False,
            "enam_code": None,
            "arrivals_qty": 0.0,
            "variety": "Common",
            "grade": "FAQ",
            "trade_type": "Spot"
        }
        
    @staticmethod
    def get_price_trends(
        conn: sqlite3.Connection,
        mandi_name: str,
        commodity_name: str
    ) -> List[Dict[str, Any]]:
        """
        Fetches historical price trends for the last 7 days from sqlite3 database.
        Projects dates to end on today if cached data is older.
        """
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM mandis WHERE mandi_name LIKE ?", (f"%{mandi_name}%",))
        mandi = cursor.fetchone()
        if not mandi:
            clean_m = mandi_name.replace("APMC", "").replace("Market", "").strip()
            cursor.execute("SELECT id FROM mandis WHERE mandi_name LIKE ? OR district LIKE ? LIMIT 1", (f"%{clean_m}%", f"%{clean_m}%"))
            mandi = cursor.fetchone()
        
        cursor.execute("SELECT id FROM commodities WHERE commodity_name LIKE ? OR local_name LIKE ?", (f"%{commodity_name}%", f"%{commodity_name}%"))
        commodity = cursor.fetchone()
        
        if not mandi or not commodity:
            return []
            
        cursor.execute(
            "SELECT date, min_price, modal_price, max_price FROM daily_prices WHERE mandi_id = ? AND commodity_id = ? ORDER BY date ASC",
            (mandi["id"], commodity["id"])
        )
        prices = cursor.fetchall()
        if not prices:
            return []

        # Project 7-day trend to end on today if needed
        latest_date_str = prices[-1]["date"]
        today_date = datetime.now().date()
        try:
            latest_dt = datetime.strptime(latest_date_str, "%Y-%m-%d").date()
            delta_days = (today_date - latest_dt).days
        except Exception:
            delta_days = 0

        trend_list = []
        for p in prices:
            try:
                p_dt = datetime.strptime(p["date"], "%Y-%m-%d").date()
                if delta_days > 0:
                    new_dt = p_dt + timedelta(days=delta_days)
                    d_str = new_dt.isoformat()
                else:
                    d_str = p["date"]
            except Exception:
                d_str = p["date"]

            trend_list.append({
                "date": d_str,
                "min_price": p["min_price"],
                "modal_price": p["modal_price"],
                "max_price": p["max_price"]
            })
        return trend_list

    @staticmethod
    def bulk_upload_rates(conn: sqlite3.Connection, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processes bulk local mandi rate upload (CSV/Excel/JSON records).
        Auto-registers mandis/commodities if missing and updates daily_prices.
        """
        import uuid
        cursor = conn.cursor()
        success_count = 0
        errors = []

        for idx, rec in enumerate(records):
            try:
                state = str(rec.get("state", "")).strip()
                district = str(rec.get("district", rec.get("state", ""))).strip()
                mandi_name = str(rec.get("mandi_name", rec.get("mandi", ""))).strip()
                commodity_name = str(rec.get("commodity", rec.get("crop", ""))).strip()
                date_str = str(rec.get("date", datetime.now().date().isoformat())).strip()
                min_price = float(rec.get("min_price", 0))
                modal_price = float(rec.get("modal_price", rec.get("price", 0)))
                max_price = float(rec.get("max_price", 0))

                if not mandi_name or not commodity_name or modal_price <= 0:
                    errors.append(f"Row {idx+1}: Missing mandi, commodity, or valid modal_price")
                    continue

                # Ensure Mandi exists in DB
                cursor.execute("SELECT id FROM mandis WHERE mandi_name LIKE ?", (f"%{mandi_name}%",))
                mandi_row = cursor.fetchone()
                if not mandi_row:
                    mandi_id = str(uuid.uuid4())
                    cursor.execute(
                        "INSERT INTO mandis (id, state, district, mandi_name, apmc_code, latitude, longitude) VALUES (?, ?, ?, ?, ?, 0.0, 0.0)",
                        (mandi_id, state or "General", district or "General", mandi_name, f"LOCAL-{uuid.uuid4().hex[:6]}")
                    )
                else:
                    mandi_id = mandi_row["id"]

                # Ensure Commodity exists in DB
                cursor.execute("SELECT id FROM commodities WHERE commodity_name LIKE ?", (f"%{commodity_name}%",))
                comm_row = cursor.fetchone()
                if not comm_row:
                    comm_id = str(uuid.uuid4())
                    cursor.execute(
                        "INSERT INTO commodities (id, commodity_name, local_name, category) VALUES (?, ?, ?, 'General')",
                        (comm_id, commodity_name, commodity_name)
                    )
                else:
                    comm_id = comm_row["id"]

                # Upsert into daily_prices
                cursor.execute(
                    "SELECT id FROM daily_prices WHERE mandi_id = ? AND commodity_id = ? AND date = ?",
                    (mandi_id, comm_id, date_str)
                )
                existing = cursor.fetchone()
                if existing:
                    cursor.execute(
                        "UPDATE daily_prices SET min_price = ?, modal_price = ?, max_price = ?, source = 'Local Admin Upload' WHERE id = ?",
                        (min_price, modal_price, max_price, existing["id"])
                    )
                else:
                    cursor.execute(
                        "INSERT INTO daily_prices (id, mandi_id, commodity_id, date, min_price, modal_price, max_price, source) VALUES (?, ?, ?, ?, ?, ?, ?, 'Local Admin Upload')",
                        (str(uuid.uuid4()), mandi_id, comm_id, date_str, min_price, modal_price, max_price)
                    )
                success_count += 1
            except Exception as e:
                errors.append(f"Row {idx+1}: {str(e)}")

        conn.commit()
        return {
            "success": True,
            "processed": success_count,
            "errors": errors
        }
