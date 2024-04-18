from database import crud
from database.database import SessionLocal
from dicom import dcm

db = SessionLocal()

# loading settings
LOCAL_AETITLE = crud.get_setting_by_key(db, "LOCAL_AETITLE").value
LOCAL_PORT = int(crud.get_setting_by_key(db, "LOCAL_PORT").value)
