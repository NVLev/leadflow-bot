from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class LeadCreate(BaseModel):
    user_id: int
    name: str
    phone: str
    email: Optional[EmailStr] = None
    service: Optional[str] = None
    message: Optional[str] = None


class LeadRead(BaseModel):
    id: int
    user_id: int
    name: str
    phone: str
    email: Optional[str]
    service: Optional[str]
    message: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
