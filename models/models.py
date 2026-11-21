from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    first_name: str
    first_surname: str
    second_surname: Optional[str] = None
    email: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    first_surname: Optional[str] = None
    second_surname: Optional[str] = None
    email: Optional[str] = None

class FavoriteStreamerCreate(BaseModel):
    login: str