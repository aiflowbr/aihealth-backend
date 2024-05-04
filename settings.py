from database.database import SessionLocal
from database import crud

db = SessionLocal()


def get_settings():
    # loading settings
    LOCAL_AETITLE = crud.get_setting_by_key(db, "LOCAL_AETITLE").value
    LOCAL_PORT = int(crud.get_setting_by_key(db, "LOCAL_PORT").value)
    return {"LOCAL_AETITLE": LOCAL_AETITLE, "LOCAL_PORT": LOCAL_PORT}
