import sqlite3
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

class ENAMService:
    """
    Service for National Agriculture Market (e-NAM) integration.
    Provides terminal market depth, arrival volumes, commodity varieties,
    assaying quality grades, and electronic auction bidding data.
    """
    
    # Official e-NAM portal and API endpoints
    BASE_URL = "https://enam.gov.in/web"
    
    @classmethod
    def get_enam_mandi_status(cls, conn: sqlite3.Connection, mandi_name: str) -> Dict[str, Any]:
        """
        Verifies whether a given mandi is integrated with the national e-NAM platform.
        """
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, mandi_name, state, district, apmc_code, is_enam, enam_code FROM mandis WHERE mandi_name LIKE ? LIMIT 1",
            (f"%{mandi_name}%",)
        )
        row = cursor.fetchone()
        if row and row["is_enam"]:
            return {
                "is_enam": True,
                "mandi_name": row["mandi_name"],
                "enam_code": row["enam_code"] or f"ENAM-{row['apmc_code']}",
                "status": "Connected & Active",
                "features": ["Electronic Bidding", "Assaying & Grading", "Online Payment", "Inter-State Trade"]
            }
        return {
            "is_enam": False,
            "mandi_name": mandi_name,
            "enam_code": None,
            "status": "Physical Mandi (AGMARKNET)",
            "features": ["Physical Open Auction"]
        }

    @classmethod
    def get_commodity_trade_depth(
        cls, 
        conn: sqlite3.Connection, 
        mandi_id: str, 
        commodity_id: str
    ) -> Dict[str, Any]:
        """
        Fetches e-NAM arrival volume, variety, assaying grade, and auction status
        for a mandi/commodity pair.
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT dp.*, m.is_enam, m.enam_code, m.mandi_name, c.commodity_name
            FROM daily_prices dp
            JOIN mandis m ON dp.mandi_id = m.id
            JOIN commodities c ON dp.commodity_id = c.id
            WHERE dp.mandi_id = ? AND dp.commodity_id = ?
            ORDER BY dp.date DESC LIMIT 1
            """,
            (mandi_id, commodity_id)
        )
        row = cursor.fetchone()
        
        if not row:
            return {
                "is_enam": False,
                "arrivals_qty": 0.0,
                "variety": "Common",
                "grade": "FAQ",
                "trade_type": "Spot",
                "auction_status": "Closed"
            }
            
        is_enam = bool(row["is_enam"])
        arrivals = float(row["arrivals_qty"] or 0.0)
        variety = row["variety"] or "Standard"
        grade = row["grade"] or "FAQ"
        trade_type = row["trade_type"] or ("e-Auction" if is_enam else "Spot")
        
        return {
            "is_enam": is_enam,
            "enam_code": row["enam_code"],
            "arrivals_qty": arrivals,
            "variety": variety,
            "grade": grade,
            "trade_type": trade_type,
            "auction_status": "Active Bidding" if is_enam else "Physical Trade",
            "date": row["date"],
            "min_price": row["min_price"],
            "modal_price": row["modal_price"],
            "max_price": row["max_price"]
        }

    @classmethod
    def get_live_enam_auctions(
        cls, 
        conn: sqlite3.Connection, 
        state: str, 
        commodity: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves active e-NAM lots and trade summaries across connected mandis in the state.
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT dp.*, m.mandi_name, m.district, m.is_enam, m.enam_code, c.commodity_name
            FROM daily_prices dp
            JOIN mandis m ON dp.mandi_id = m.id
            JOIN commodities c ON dp.commodity_id = c.id
            WHERE m.state LIKE ? AND c.commodity_name LIKE ? AND m.is_enam = 1
            ORDER BY dp.modal_price DESC LIMIT 5
            """,
            (f"%{state}%", f"%{commodity}%")
        )
        rows = cursor.fetchall()
        
        results = []
        for r in rows:
            results.append({
                "mandi": r["mandi_name"],
                "district": r["district"],
                "enam_code": r["enam_code"],
                "commodity": r["commodity_name"],
                "variety": r["variety"] or "Standard",
                "grade": r["grade"] or "Grade A",
                "arrivals_qty": float(r["arrivals_qty"] or 0.0),
                "modal_price": float(r["modal_price"]),
                "min_price": float(r["min_price"]),
                "max_price": float(r["max_price"]),
                "trade_type": r["trade_type"] or "e-Auction",
                "date": r["date"]
            })
        return results
