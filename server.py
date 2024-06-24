# from contextlib import asynccontextmanager

# import os
from fastapi import WebSocket  # , HTTPException, Response, Depends, FastAPI,

from database.crud import get_nodes_all_status  # get_nodes_all,
from database.database import Base, engine, SessionLocal  # , get_db
from routes.nodes import router as nodes_routes
from routes.inputs import router as inputs_routes
from routes.settings import router as settings_routes
from routes.info import router as info_router
from routes.users import router as users_router
from routes.fetchers import router as fetchers_router
from routes.neural_networks import router as neural_networks_router
from ws import ws_clients
from config.initializing import initialize_fastapi

# DICOM
from dicom import listener

# DICOM server listener
listener.start_listener()

app = initialize_fastapi()


# ..... ROUTES
# cria banco de dados
Base.metadata.create_all(bind=engine)


app.include_router(router=info_router)
app.include_router(prefix="/fetchers", router=fetchers_router)
app.include_router(
    prefix="/nodes",
    router=nodes_routes,
)
app.include_router(prefix="/inputs", router=inputs_routes)
app.include_router(prefix="/settings", router=settings_routes)
app.include_router(prefix="/users", router=users_router)
app.include_router(prefix="/neural_networks", router=neural_networks_router)


# @app.get("/inputs", tags=["Inputs list"])
# def pacs_images():
#     return []


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
    ws_clients.append(websocket)
    print(f"WS Client Connected... TOTAL: {len(ws_clients)}")
    await websocket.send_json({"compute_nodes": compute_nodes})

    # send current nodes
    await websocket.send_json({"input_nodes": get_nodes_all_status(db=SessionLocal())})

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
        ws_clients.remove(websocket)
        print(f"WS Client CLOSED... TOTAL: {len(ws_clients)}")
