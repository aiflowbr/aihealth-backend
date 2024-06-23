from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
from sqlalchemy_serializer import SerializerMixin
from fetchers import nodes_fetcher
from datetime import datetime, UTC


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


class NeuralNetworks(Base, SerializerMixin):
    __tablename__ = "neural_networks"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    architecture = Column(String, nullable=False)  # e.g., VGG16, ResNet50
    modality = Column(String, index=True)  # e.g., DX, CT.
    upload_path = Column(
        String, nullable=False
    )  # Path to the uploaded TensorFlow model file
    date_created = Column(DateTime, default=datetime.now(UTC))
    is_active = Column(Boolean, default=True)

    # def __init__(self, name, architecture, upload_path, description=None):
    #     self.name = name
    #     self.architecture = architecture
    #     self.upload_path = upload_path
    #     self.description = description


# # Optional: Associating NeuralNetwork with an existing Workflow or Input
# class Workflow(Base, SerializerMixin):
#     __tablename__ = "workflows"

#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#     neural_network_id = Column(Integer, ForeignKey('neural_networks.id'))
#     neural_network = relationship("NeuralNetwork", back_populates="workflows")

# NeuralNetwork.workflows = relationship("Workflow", order_by=Workflow.id, back_populates="neural_network")
