from pydantic import BaseModel
from typing import Optional
from datetime import date


class UserCreate(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    role: str = "customer"


class UserOut(BaseModel):
    id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    username: str
    password: str


class ServiceCreate(BaseModel):
    name: str
    category: str
    phone: str
    address: str
    pincode: str


class ServiceOut(BaseModel):
    id: int
    provider_id: Optional[int] = None
    category: Optional[str] = None
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    image: Optional[str] = None
    rating: Optional[float] = 0


class BookingCreate(BaseModel):
    service_id: int
    booking_date: date


class BookingOut(BaseModel):
    id: int
    customer_id: int
    service_id: int
    booking_date: Optional[date] = None
    service_name: Optional[str] = None
    service_phone: Optional[str] = None
    service_address: Optional[str] = None
    service_image: Optional[str] = None
    category: Optional[str] = None


class ReviewCreate(BaseModel):
    service_id: int
    rating: int
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    user_id: int
    service_id: int
    rating: int
    comment: Optional[str] = None
    username: Optional[str] = None
