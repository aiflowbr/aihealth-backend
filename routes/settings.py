from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from database import crud, schemas
from database.database import get_db

router = APIRouter()
url_base = ""
# url_base_id = f"{url_base}/{{id}}"
url_base_id = "/{id}"


@router.post(url_base, response_model=schemas.Settings, tags=["Settings"])
def create_setting(setting: schemas.SettingsBase, db: Session = Depends(get_db)):
    db_setting = crud.get_setting_by_key(db, key=setting.key)
    if db_setting:
        raise HTTPException(status_code=400, detail="Setting already registered")
    return crud.create_setting(db=db, setting=setting)


@router.put(url_base_id, response_model=schemas.Settings, tags=["Settings"])
def update_setting(id: int, setting: schemas.SettingsBase, db: Session = Depends(get_db)):
    db_setting = crud.get_setting(db, id=id)
    if not db_setting:
        raise HTTPException(status_code=400, detail="Setting not found")
    try:
        ret = crud.update_setting(db=db, db_setting=db_setting, userdata=setting)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ret


@router.delete(url_base_id, response_model=schemas.Settings, tags=["Settings"])
def delete_setting(id: int, db: Session = Depends(get_db)):
    db_setting = crud.get_setting(db, id=id)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    crud.delete_setting(db, db_setting)
    return db_setting


@router.get(url_base, response_model=list[schemas.Settings], tags=["Settings"])
def read_settings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_settings(db, skip=skip, limit=limit)


@router.get(url_base_id, response_model=schemas.Settings, tags=["Settings"])
def read_setting(id: int, db: Session = Depends(get_db)):
    setting = crud.get_setting(db, id=id)
    if setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting