from pydantic import BaseModel
from datetime import datetime


class AuditBase(BaseModel):
    action: str
    ts: datetime | None = None


class AuditCreate(AuditBase):
    pass


class Audit(AuditBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    old_password: str
    password: str


class User(UserBase):
    id: int
    is_active: bool
    # is_ad_auth: bool
    logons: list[Audit] = []

    class Config:
        from_attributes = True
