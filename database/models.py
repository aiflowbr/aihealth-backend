from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # is_ad_auth = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    logons = relationship("Audit", back_populates="user")


class Audit(Base):
    __tablename__ = "audit"

    id = Column(Integer, primary_key=True)
    action = Column(String, index=True)
    ts = Column(DateTime, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="logons")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    aetitle = Column(String, index=True)
    address = Column(String, index=True)
    port = Column(Integer, index=True)
    fetch_interval = Column(Integer)
    fetch_interval_type = Column(String)
    _status = False

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    key = Column(String, index=True)
    value = Column(String)
    # owner_id = Column(Integer, ForeignKey("users.id"))
    # owner = relationship("User", back_populates="items")


class Inputs(Base):
    __tablename__ = "inputs"

    id = Column(Integer, primary_key=True)
    aetitle = Column(String, index=True)
    address = Column(String, index=True)
    port = Column(Integer, index=True)
    # owner_id = Column(Integer, ForeignKey("users.id"))
    # owner = relationship("User", back_populates="items")
