"""Validation for Login Service"""

from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, ConfigDict, StringConstraints

# ---------- Reusable type aliases ----------
NameStr = Annotated[str, StringConstraints(min_length=2, max_length=25)]
PasswordStr = Annotated[str, StringConstraints(min_length=5, max_length=50, pattern=r"[a-z]")]

class Account(BaseModel):
    """Json input vailidation for Accounts"""
    user_id: int
    name: NameStr
    email: EmailStr
    password: PasswordStr

# ---------- Accounts ----------
class AccountCreate(BaseModel):
    name: NameStr
    email: EmailStr
    password: PasswordStr

class AccountLogin(BaseModel):
    email: EmailStr
    password: PasswordStr

class AccountPartialUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[NameStr] = None
    email: Optional[EmailStr] = None
    password: Optional[PasswordStr] = None

class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: NameStr
    email: EmailStr
    password: PasswordStr
