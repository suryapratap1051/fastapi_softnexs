from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ContactBase(BaseModel):
    name: str
    email: str
    company: str
    phone: str
    message: str

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: int
    created_at: datetime
    status: str
    
    class Config:
        from_attributes = True

class ContactUpdate(BaseModel):
    status: Optional[str] = None