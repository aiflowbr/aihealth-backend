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


class TokenDecode(BaseModel):
    token: str


class TokenDecoded(BaseModel):
    name: str
    username: str
    mail: str
    photo: str


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


class NodeBase(BaseModel):
    aetitle: str
    address: str
    port: int
    fetch_interval: int
    fetch_interval_type: str


class Node(NodeBase):
    id: int


class NodeStatus(Node):
    status: bool


class SettingsBase(BaseModel):
    key: str
    value: str


class Settings(SettingsBase):
    id: int
