import hashlib
from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hash_object = hashlib.sha256(user.password.encode())
    hex_hash = hash_object.hexdigest()
    db_user = models.User(username=user.username, hashed_password=hex_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: models.User, userdata: schemas.UserUpdate):
    # old pwd
    old_hash_object = hashlib.sha256(userdata.old_password.encode())
    old_hex_hash = old_hash_object.hexdigest()
    if db_user.hashed_password == old_hex_hash:
        hash_object = hashlib.sha256(userdata.password.encode())
        hex_hash = hash_object.hexdigest()
        print(db_user, userdata)
        db_user.hashed_password = hex_hash
        # db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        raise Exception("Wrong old password")
    return db_user


def get_audits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Audit).offset(skip).limit(limit).all()


def create_user_item(db: Session, audit: schemas.AuditCreate, user_id: int):
    db_audit = models.Audit(**audit.model_dump(), user_id=user_id)
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)
    return db_audit


def get_nodes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Node).offset(skip).limit(limit).all()


def get_nodes_all(db: Session):
    return db.query(models.Node).all()


def get_node_by_host_port(db: Session, address: str, port: int):
    return (
        db.query(models.Node)
        .filter(models.Node.address == address, models.Node.port == port)
        .first()
    )


def create_node(db: Session, node: schemas.NodeBase):
    db_node = models.Node(
        aetitle=node.aetitle,
        address=node.address,
        port=node.port,
        fetch_interval=node.fetch_interval,
        fetch_interval_type=node.fetch_interval_type,
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node


def get_node(db: Session, id: int):
    obj = db.query(models.Node).filter(models.Node.id == id).first()
    return obj


def update_node(db: Session, db_node: models.Node, userdata: schemas.NodeBase):
    db_node.aetitle = userdata.aetitle
    db_node.address = userdata.address
    db_node.port = userdata.port
    db_node.fetch_interval = userdata.fetch_interval
    db_node.fetch_interval_type = userdata.fetch_interval_type
    db.commit()
    db.refresh(db_node)
    return db_node

def delete_node(db: Session, db_node: models.Node):
    db.delete(db_node)
    db.commit()
    return db_node

#########
# settings
def get_settings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Settings).offset(skip).limit(limit).all()


def get_setting(db: Session, id: int):
    obj = db.query(models.Settings).filter(models.Settings.id == id).first()
    return obj


def get_setting_by_key(db: Session, key: str):
    return (
        db.query(models.Settings)
        .filter(models.Settings.key == key)
        .first()
    )


def create_setting(db: Session, setting: schemas.SettingsBase):
    db_setting = models.Settings(key = setting.key, value = setting.value)
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting


def update_setting(db: Session, db_setting: models.Settings, userdata: schemas.SettingsBase):
    db_setting.key = userdata.key
    db_setting.value = userdata.value
    db.commit()
    db.refresh(db_setting)
    return db_setting


def delete_setting(db: Session, db_setting: models.Settings):
    db.delete(db_setting)
    db.commit()
    return db_setting