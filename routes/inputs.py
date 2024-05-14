from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from database import crud, schemas
from database.database import get_db

router = APIRouter()
url_base = ""
url_base_id = f"{url_base}/{{id}}"

# from fetchers import fetch_node, nodes_fetcher


# @router.post(url_base, response_model=schemas.Node, tags=["Inputs"])
# def create_input(node: schemas.NodeBase, db: Session = Depends(get_db)):
#     db_input = crud.get_input_by_host_port(db, address=node.address, port=node.port)
#     if db_input:
#         raise HTTPException(status_code=400, detail="Node already registered")
#     new_input = crud.create_input(db=db, node=node)
#     if node.fetch_interval_type == "s":
#         nodes_fetcher.schedule(
#             f"{node.address}:{node.port}", node, fetch_node, sec=node.fetch_interval
#         )
#     else:
#         nodes_fetcher.schedule(
#             f"{node.address}:{node.port}", node, fetch_node, min=node.fetch_interval
#         )
#     return new_input


# @router.put(url_base_id, response_model=schemas.Node, tags=["Inputs"])
# def update_input(id: int, node: schemas.NodeBase, db: Session = Depends(get_db)):
#     db_input = crud.get_input(db, id=id)
#     if not db_input:
#         raise HTTPException(status_code=400, detail="Node ID not found")
#     try:
#         ret = crud.update_input(db=db, db_input=db_input, userdata=node)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     nodes_fetcher.stop(f"{db_input.address}:{db_input.port}")
#     if db_input.fetch_interval_type == "s":
#         nodes_fetcher.schedule(
#             f"{db_input.address}:{db_input.port}",
#             node,
#             fetch_node,
#             sec=db_input.fetch_interval,
#         )
#     else:
#         nodes_fetcher.schedule(
#             f"{db_input.address}:{db_input.port}",
#             node,
#             fetch_node,
#             min=db_input.fetch_interval,
#         )
#     return ret


# @router.delete(url_base_id, response_model=schemas.Node, tags=["Inputs"])
# def delete_input(id: int, db: Session = Depends(get_db)):
#     db_input = crud.get_input(db, id=id)
#     if db_input is None:
#         raise HTTPException(status_code=404, detail="Node not found")
#     nodes_fetcher.stop(f"{db_input.address}:{db_input.port}")
#     crud.delete_input(db, db_input)
#     return db_input


@router.get(url_base, response_model=list[schemas.NodeStatus], tags=["Inputs"])
def read_inputs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    nodes = crud.get_inputs(db, skip=skip, limit=limit)
    # for node in nodes:
    #     node.status = True
    return nodes


# @router.get(url_base_id, response_model=schemas.NodeStatus, tags=["Inputs"])
# def read_input(id: int, db: Session = Depends(get_db)):
#     db_input = crud.get_input(db, id=id)
#     if db_input is None:
#         raise HTTPException(status_code=404, detail="Node not found")
#     db_input.status = True
#     return db_input
