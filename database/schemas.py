from pydantic import BaseModel
from datetime import datetime
from typing import Optional


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
    name: str | None = None
    mail: str | None = None
    photo: str | None = None


class TokenBase(BaseModel):
    access_token: str
    token_type: str


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


class InputBase(BaseModel):
    modality: str


class NeuralNetworkBase(BaseModel):
    name: str
    description: str | None = None
    architecture: str
    modality: str
    upload_path: str
    date_created: datetime
    is_active: bool


class NeuralNetworkUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    architecture: Optional[str] = None
    modality: Optional[str] = None
    upload_path: Optional[str] = None
    date_created: Optional[datetime] = None
    is_active: Optional[bool] = None


class NeuralNetwork(NeuralNetworkBase):
    id: int
