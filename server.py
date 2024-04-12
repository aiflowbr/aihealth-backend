import os
from fastapi import Depends, FastAPI, HTTPException, Response, WebSocket
from sqlalchemy.orm import Session
import asyncio
from queue import Queue
import json
from time import sleep

from database import crud, models, schemas
from database.database import SessionLocal, engine
# from keras_visualizer import visualizer
import tempfile
import deep

## DICOM
from pydicom.dataset import Dataset
from pydicom import datadict
from pydicom.tag import Tag, BaseTag, TagType
from pydicom.valuerep import (PersonName)
from dicom import dcm

def gen_dicom_filter():
    ds = Dataset()
    # ds.Modality = ""  # "DX"
    ds.Modality = ""  # "DX"
    # ds.ModalitiesInStudy = "DX"
    ds.ModalitiesInStudy = ""
    ds.AccessionNumber = ""
    ds.StudyDate = "20240412-20240412"
    ds.StudyTime = "170000-173000"
    # ds.StudyTime = ""
    ds.TimezoneOffsetFromUTC = ""
    # ds.PatientID = ""  # "1795017"
    ds.PatientID = ""
    # ds.PatientPosition = "PA\\AP"
    ds.PatientPosition = ""
    ds.PatientName = ""
    ds.PatientBirthDate = ""
    ds.SeriesInstanceUID = ""
    ds.StudyInstanceUID = ""
    ds.StudyID = ""
    # ds.StudyDescription = "TORAX"
    ds.StudyDescription = ""
    ds.FileSetID = ""
    ds.ModalitiesInStudy = ""
    ds.NumberOfStudyRelatedInstances = ""
    ds.ReferringPhysicianName = ""
    ds.QueryRetrieveLevel = "STUDY"
    ds.ImageComments = ""
    return ds

network_parameters = {
    "server_address": "localhost",
    "server_port": 4242,
    "server_ae_title": "ORTHANC",
    "local_ae_title": "AIHEALTHMAC",
}
dicom_listener = dcm.init_server(ae_title="AIHEALTHMAC", listen_address="0.0.0.0", listen_port=11112)

# browser ws clients
clients = []

# compute servers
compute_sockets = []

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

compute_nodes = [
    {"server": "localhost:8098", "status": True},
    {"server": "localhost:8099", "status": True},
]


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", tags=["Info"])
def info():
    return {"appname": "AIHEALTH", "version": "1.0"}

def get_value_original_string(key, obj):
    if key == "PatientName": # and "original_string" in obj:
        if isinstance(obj, PersonName):
            return f"{obj}"
    return obj

@app.get("/inputs/list", tags=["Inputs list"])
def pacs_images():
    ds = gen_dicom_filter()
    if network_parameters is None:
        raise "Error: network parameters"

    client = dcm.init_client(
        client_ae_title=network_parameters["local_ae_title"],
        address=network_parameters["server_address"],
        port=network_parameters["server_port"],
        ae_title=network_parameters["server_ae_title"],
    )
    if client.is_established:
        responses = client.send_c_find(ds, dcm.StudyRootQueryRetrieveInformationModelFind)
        datasets = []
        for status, dataset in responses:
            # keys = [
            #     "AccessionNumber",
            #     "ImageComments",
            #     "ModalitiesInStudy",
            #     "Modality",
            #     "NumberOfStudyRelatedInstances",
            #     "PatientBirthDate",
            #     "PatientID",
            #     "PatientName",
            #     "PatientPosition",
            #     "QueryRetrieveLevel",
            #     "ReferringPhysicianName",
            #     "RetrieveAETitle",
            #     "SeriesInstanceUID",
            #     "SpecificCharacterSet",
            #     "StudyDate",
            #     "StudyDescription",
            #     "StudyID",
            #     "StudyInstanceUID",
            #     "StudyTime",
            #     "TimezoneOffsetFromUTC"]
            # # if "PatientID" in dir(dataset):
            if "PatientID" in dir(dataset):
                obj = dataset.to_json_dict()
                nobj = {z[4]: get_value_original_string(z[4], dataset[z[4]]._value) for z in [datadict.get_entry(Tag(k)) for k in obj.keys()]}
                datasets.append(nobj)
                # taginfo = datadict.get_entry(Tag("00204000"))
                # key, desc = taginfo[4], taginfo[2]
                # datasets.append({**{k: dataset[k]._value for k in keys}, "json": obj})
            #     datasets.append({**{k: dataset[k]._value for k in keys}, "json": dataset.to_json_dict()})
            # for k in dataset:
            #     print(k)
        return datasets
    return []


@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.put("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    print(user_id)
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail="User ID not found")
    try:
        ret = crud.update_user(db=db, db_user=db_user, userdata=user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ret


@app.get("/users/", response_model=list[schemas.User], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/model_image")
def model_image(response: Response):
    # model = deep.model_from_json(
    #     "/Users/anderson/Dev/MDCC/xray-pacs/output/my_model.json"
    # )
    # model.load_weights(
    #     "/Users/anderson/Dev/MDCC/xray-pacs/output/xray_class_my_model.best.hdf5"
    # )
    model = deep.vgg16()
    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        visualizer(model, file_name=tmp_file.name, file_format="png")
        with open(f"{tmp_file.name}.png", "rb") as f:
            file_bytes = f.read()
            os.remove(f.name)
    response.headers["Content-Type"] = "image/png"
    return Response(content=file_bytes, media_type="image/png")


# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items


# Rota WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    print("WS Client Connected...")
    await websocket.send_json(json.dumps({"compute_nodes": compute_nodes}))

    # async de logs
    # asyncio.create_task(send_logs(websocket))

    try:
        while True:
            data = await websocket.receive_json()
            # Enviar mensagem para todos os clientes
            # await asyncio.gather(*[client.send_json(data) for client in clients])
            print(f"Recebido: {data}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        clients.remove(websocket)
