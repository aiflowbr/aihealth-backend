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
