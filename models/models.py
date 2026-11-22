from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["asier_dev"],
    )
    first_name: str = Field(..., min_length=2, max_length=50, examples=["Asier"])
    first_surname: str = Field(..., min_length=2, max_length=50, examples=["Aldekoa"])
    second_surname: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        examples=["Bengoetxea"],
    )
    email: EmailStr = Field(..., examples=["asier@example.com"])


class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["asier_dev"],
    )
    first_name: Optional[str] = Field(default=None, min_length=2, max_length=50, examples=["Asier"])
    first_surname: Optional[str] = Field(default=None, min_length=2, max_length=50, examples=["Aldekoa"])
    second_surname: Optional[str] = Field(default=None, min_length=2, max_length=50, examples=["Bengoetxea"])
    email: Optional[EmailStr] = Field(default=None, examples=["asier@example.com"])


class FavoriteStreamerCreate(BaseModel):
    login: str = Field(
        ...,
        min_length=3,
        max_length=25,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["ibai"],
    )


class PlaylistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Mejores directos"])
    description: Optional[str] = Field(
        default=None,
        max_length=255,
        examples=["Recopilación de mis momentos favoritos"],
    )


class PlaylistItemCreate(BaseModel):
    twitch_video_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^\d+$",
        examples=["2301948572"],
    )