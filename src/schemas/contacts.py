from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

"""
Example
{
"first_name": "Maksym",
"last_name": "Klym",
"phone": "+380936644885",
"email": "test@example.com",
"birthday": "1990-10-01"
}
"""


class ContactModel(BaseModel):
    first_name: str
    last_name: str
    phone: PhoneNumber
    email: Optional[EmailStr] = None
    birthday: Optional[date] = None


class ResponseContact(ContactModel):
    id: int

    class Config:
        from_attributes: bool = True

