from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from database import crud, schemas
from database.database import get_db

router = APIRouter()

url_base = "/nodes"


@router.post(url_base, response_model=schemas.User, tags=["Nodes"])
def create_node(node: schemas.NodeBase, db: Session = Depends(get_db)):
    db_node = crud.get_node_by_host_port(db, address=node.address, port=node.port)
    if db_node:
        raise HTTPException(status_code=400, detail="Node already registered")
    return crud.create_node(db=db, node=node)


@router.put("/nodes/{node_id}", response_model=schemas.Node, tags=["Nodes"])
def update_node(node_id: int, node: schemas.NodeBase, db: Session = Depends(get_db)):
    db_node = crud.get_node(db, node_id=node_id)
    if not db_node:
        raise HTTPException(status_code=400, detail="Node ID not found")
    try:
        ret = crud.update_node(db=db, db_node=db_node, userdata=node)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ret


@router.get(url_base, response_model=list[schemas.Node], tags=["Nodes"])
def read_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    nodes = crud.get_nodes(db, skip=skip, limit=limit)
    return nodes


@router.get("/nodes/{node_id}", response_model=schemas.NodeStatus, tags=["Nodes"])
def read_node(node_id: int, db: Session = Depends(get_db)):
    db_node = crud.get_node(db, node_id=node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    db_node.status = True
    return db_node
