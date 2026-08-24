from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class UserBase(BaseModel):
    name: Optional[str] = None
    mobile: str
    preferred_language: Optional[str] = "en"
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

class MandiBase(BaseModel):
    state: str
    district: str
    mandi_name: str
    apmc_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class MandiResponse(MandiBase):
    id: str

    class Config:
        orm_mode = True

class CommodityBase(BaseModel):
    commodity_name: str
    local_name: Optional[str] = None
    category: Optional[str] = None

class CommodityResponse(CommodityBase):
    id: str

    class Config:
        orm_mode = True

class DailyPriceBase(BaseModel):
    mandi_id: str
    commodity_id: str
    date: date
    min_price: float
    modal_price: float
    max_price: float
    source: str = "AGMARKNET"

class DailyPriceResponse(DailyPriceBase):
    id: str
    mandi: MandiResponse
    commodity: CommodityResponse

    class Config:
        orm_mode = True

class PriceTrendPoint(BaseModel):
    date: date
    min_price: float
    modal_price: float
    max_price: float

class PriceTrendResponse(BaseModel):
    commodity_name: str
    mandi_name: str
    trend: List[PriceTrendPoint]

class BuyerBase(BaseModel):
    company: str
    gst_number: Optional[str] = None
    district: str
    commodity: str
    phone: str
    verified: bool = False
    rating: float = 0.0

class BuyerResponse(BuyerBase):
    id: str

    class Config:
        orm_mode = True

class DealerBase(BaseModel):
    shop_name: str
    fertilizer: bool = False
    seed: bool = False
    pesticide: bool = False
    location: str
    verified: bool = False

class DealerResponse(DealerBase):
    id: str

    class Config:
        orm_mode = True

# AI recognition schema
class AIQueryParse(BaseModel):
    intent: str
    commodity: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    language: str = "en"
    raw_query: str

class TextQueryRequest(BaseModel):
    text: str
    mobile: Optional[str] = None
    language: Optional[str] = "en"
