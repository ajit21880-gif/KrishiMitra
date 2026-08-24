from fastapi import APIRouter, Depends, Query
import sqlite3
from typing import List, Optional
from app.core.database import get_db
from app.schemas.schemas import BuyerResponse, DealerResponse

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

@router.get("/buyers", response_model=List[BuyerResponse])
def get_buyers(
    commodity: Optional[str] = Query(None, description="Filter by commodity"),
    district: Optional[str] = Query(None, description="Filter by district"),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM buyers WHERE 1=1"
    params = []
    
    if commodity:
        query += " AND commodity LIKE ?"
        params.append(f"%{commodity}%")
    if district:
        query += " AND district LIKE ?"
        params.append(f"%{district}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@router.get("/dealers", response_model=List[DealerResponse])
def get_dealers(
    location: Optional[str] = Query(None, description="Filter by district/city"),
    fertilizer: Optional[bool] = Query(None, description="Available fertilizer stock"),
    seed: Optional[bool] = Query(None, description="Available seeds stock"),
    pesticide: Optional[bool] = Query(None, description="Available pesticide stock"),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM dealers WHERE 1=1"
    params = []
    
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if fertilizer is not None:
        query += " AND fertilizer = ?"
        params.append(1 if fertilizer else 0)
    if seed is not None:
        query += " AND seed = ?"
        params.append(1 if seed else 0)
    if pesticide is not None:
        query += " AND pesticide = ?"
        params.append(1 if pesticide else 0)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]
