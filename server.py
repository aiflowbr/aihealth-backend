from contextlib import asynccontextmanager

# import os
from fastapi import Depends, FastAPI, WebSocket  # , HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

# from sqlalchemy.orm import Session

# import asyncio

# from queue import Queue
import json

# from time import sleep
from cron import nodes_fetcher

from database import crud, models, schemas
from database.database import engine, SessionLocal  # , get_db

# from keras_visualizer import visualizer
import tempfile
import deep

from routes import nodes, inputs, settings
from fetchers import fetch_node

## DICOM
from dicom import listener

db = SessionLocal()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing...")
    try:
        nodes.create_node(
            schemas.NodeBase(
                **{
                    "aetitle": "ORTHANC",
                    "address": "localhost",
                    "port": 4242,
                    "fetch_interval": 10,
                    "fetch_interval_type": "s",
                }
            ),
            db,
        )
    except Exception:
        pass
    try:
        settings.create_setting(
            schemas.SettingsBase(**{"key": "LOCAL_AETITLE", "value": "AIHEALTHMAC"}),
            db,
        )
    except Exception:
        pass
    try:
        settings.create_setting(
            schemas.SettingsBase(**{"key": "LOCAL_PORT", "value": "11112"}),
            db,
        )
    except Exception:
        pass
    db_nodes = crud.get_nodes_all(db)
    for node in db_nodes:
        if node.fetch_interval_type == "s":
            nodes_fetcher.schedule(
                f"{node.address}:{node.port}", node, fetch_node, sec=node.fetch_interval
            )
        else:
            nodes_fetcher.schedule(
                f"{node.address}:{node.port}", node, fetch_node, min=node.fetch_interval
            )
    yield
    print("Finishing...")
    nodes_fetcher.stop_all()


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def startup_event_handler():
    print("Backend STARTED")


async def shutdown_event_handler():
    print("Backend FINISHED")


app.add_event_handler("startup", startup_event_handler)
app.add_event_handler("shutdown", shutdown_event_handler)


########### ROUTES

# browser ws clients
clients = []

# compute servers
compute_sockets = []

# cria banco de dados
models.Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Info"])
def info():
    return {"appname": "AIHEALTH", "version": "1.0"}


@app.get("/fetchers", tags=["Fetchers list"])
def schedules():
    return nodes_fetcher.list()


app.include_router(nodes.router)
app.include_router(inputs.router)
app.include_router(settings.router)


listener.start_listener()


# @app.get("/inputs", tags=["Inputs list"])
# def pacs_images():

#     return []


# @app.post("/users/", response_model=schemas.User, tags=["Users"])
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_username(db, username=user.username)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
#     return crud.create_user(db=db, user=user)


# @app.put("/users/{user_id}", response_model=schemas.User, tags=["Users"])
# def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
#     print(user_id)
#     db_user = crud.get_user(db, user_id=user_id)
#     if not db_user:
#         raise HTTPException(status_code=400, detail="User ID not found")
#     try:
#         ret = crud.update_user(db=db, db_user=db_user, userdata=user)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     return ret


# @app.get("/users/", response_model=list[schemas.User], tags=["Users"])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users


# @app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.get("/model_image")
# def model_image(response: Response):
#     # model = deep.model_from_json(
#     #     "/Users/anderson/Dev/MDCC/xray-pacs/output/my_model.json"
#     # )
#     # model.load_weights(
#     #     "/Users/anderson/Dev/MDCC/xray-pacs/output/xray_class_my_model.best.hdf5"
#     # )
#     model = deep.vgg16()
#     with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
#         visualizer(model, file_name=tmp_file.name, file_format="png")
#         with open(f"{tmp_file.name}.png", "rb") as f:
#             file_bytes = f.read()
#             os.remove(f.name)
#     response.headers["Content-Type"] = "image/png"
#     return Response(content=file_bytes, media_type="image/png")


# # @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# # def create_item_for_user(
# #     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# # ):
# #     return crud.create_user_item(db=db, item=item, user_id=user_id)


# # @app.get("/items/", response_model=list[schemas.Item])
# # def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
# #     items = crud.get_items(db, skip=skip, limit=limit)
# #     return items

compute_nodes = [
    {"server": "localhost:8098", "status": True},
    {"server": "localhost:8099", "status": True},
]


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
