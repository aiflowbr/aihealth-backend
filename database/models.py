from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
from sqlalchemy_serializer import SerializerMixin
from fetchers import nodes_fetcher


class User(Base, SerializerMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    mail = Column(String)
    photo = Column(String)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # is_ad_auth = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    logons = relationship("Audit", back_populates="user")


class Audit(Base, SerializerMixin):
    __tablename__ = "audit"

    id = Column(Integer, primary_key=True)
    action = Column(String, index=True)
    ts = Column(DateTime, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="logons")


class Node(Base, SerializerMixin):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    aetitle = Column(String, index=True)
    address = Column(String, index=True)
    port = Column(Integer, index=True)
    fetch_interval = Column(Integer)
    fetch_interval_type = Column(String)
    # _status = False

    @property
    def status(self):
        return nodes_fetcher.get_alive(f"{self.address}:{self.port}")

    # @status.setter
    # def status(self, value):
    #     self._status = value


class Settings(Base, SerializerMixin):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    key = Column(String, index=True)
    value = Column(String)
    # owner_id = Column(Integer, ForeignKey("users.id"))
    # owner = relationship("User", back_populates="items")


class Inputs(Base, SerializerMixin):
    __tablename__ = "inputs"

    id = Column(Integer, primary_key=True)
    aetitle = Column(String, index=True)
    address = Column(String, index=True)
    port = Column(Integer, index=True)
    # owner_id = Column(Integer, ForeignKey("users.id"))
    # owner = relationship("User", back_populates="items")


# class NeuralNetworks(Base, SerializerMixin):
#     __tablename__ = "neural_networks"

#     id = Column(Integer, primary_key=True)
#     model = Column(String, index=True)
#     modality = Column(String, index=True)
