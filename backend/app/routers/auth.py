from fastapi import APIRouter, Depends, HTTPException, status
import sqlite3
from pydantic import BaseModel
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional
from app.core.database import get_db
from app.schemas.schemas import UserResponse, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "krishimitra_super_secret_key"
ALGORITHM = "HS256"

# Mock storage for sent OTPs: phone -> OTP
_otp_store = {}

class OTPRequest(BaseModel):
    mobile: str

class OTPVerifyRequest(BaseModel):
    mobile: str
    otp: str
    name: Optional[str] = None
    preferred_language: Optional[str] = "en"

@router.post("/send_otp")
def send_otp(request: OTPRequest):
    mobile = request.mobile.strip()
    if not mobile:
        raise HTTPException(status_code=400, detail="Mobile number is required")
    
    # Generate mock OTP
    otp = "123456" # For testing/mocking
    _otp_store[mobile] = otp
    print(f"[OTP SMS SIMULATED] To: {mobile} | Code: {otp}")
    
    return {"message": "OTP sent successfully (Simulated 123456)"}

@router.post("/verify_otp")
def verify_otp(request: OTPVerifyRequest, db: sqlite3.Connection = Depends(get_db)):
    mobile = request.mobile.strip()
    otp = request.otp.strip()
    
    if _otp_store.get(mobile) != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
        
    # Validated. Clear OTP
    if mobile in _otp_store:
        del _otp_store[mobile]
        
    cursor = db.cursor()
    
    # Check if user exists, otherwise create
    cursor.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
    user = cursor.fetchone()
    
    if not user:
        user_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        name = request.name or "Farmer"
        preferred_language = request.preferred_language or "en"
        
        cursor.execute(
            "INSERT INTO users (id, name, mobile, preferred_language, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, mobile, preferred_language, created_at)
        )
        db.commit()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
    # Generate JWT
    token_data = {
        "sub": user["id"],
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "mobile": user["mobile"],
            "preferred_language": user["preferred_language"]
        }
    }
