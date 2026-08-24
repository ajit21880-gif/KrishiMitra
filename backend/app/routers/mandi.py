from fastapi import APIRouter, Depends, HTTPException, Query
import sqlite3
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.schemas import MandiResponse, CommodityResponse, PriceTrendResponse
from app.services.mandi_service import MandiService

router = APIRouter(prefix="/mandi", tags=["mandi"])

@router.get("/states", response_model=List[str])
def get_states(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT state FROM mandis")
    rows = cursor.fetchall()
    return [row["state"] for row in rows]

@router.get("/districts", response_model=List[str])
def get_districts(state: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT district FROM mandis WHERE state = ?", (state,))
    rows = cursor.fetchall()
    return [row["district"] for row in rows]

@router.get("/list", response_model=List[MandiResponse])
def get_mandis(state: str, district: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM mandis WHERE state = ? AND district = ?", (state, district))
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@router.get("/commodities", response_model=List[CommodityResponse])
def get_commodities(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM commodities")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@router.get("/price")
def get_mandi_price(
    state: str,
    district: str,
    mandi_name: str,
    commodity_name: str,
    db: sqlite3.Connection = Depends(get_db)
):
    try:
        return MandiService.get_mandi_price(db, state, district, mandi_name, commodity_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trend", response_model=PriceTrendResponse)
def get_price_trends(
    mandi_name: str,
    commodity_name: str,
    db: sqlite3.Connection = Depends(get_db)
):
    trend_data = MandiService.get_price_trends(db, mandi_name, commodity_name)
    if not trend_data:
        raise HTTPException(status_code=404, detail="Trend data not found for given Mandi and Commodity")
    return {
        "commodity_name": commodity_name,
        "mandi_name": mandi_name,
        "trend": trend_data
    }
