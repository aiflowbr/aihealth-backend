from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from database import crud, schemas
from database.database import get_db


router = APIRouter()
url_base = "/nodes"


from fetchers import fetch_node, nodes_fetcher


@router.post(url_base, response_model=schemas.Node, tags=["Nodes"])
def create_node(node: schemas.NodeBase, db: Session = Depends(get_db)):
    db_node = crud.get_node_by_host_port(db, address=node.address, port=node.port)
    if db_node:
        raise HTTPException(status_code=400, detail="Node already registered")
    new_node = crud.create_node(db=db, node=node)
    if node.fetch_interval_type == "s":
        nodes_fetcher.schedule(f"{node.address}:{node.port}", node, fetch_node, sec=node.fetch_interval)
    else:
        nodes_fetcher.schedule(f"{node.address}:{node.port}", node, fetch_node, min=node.fetch_interval)
    return new_node


@router.put("/nodes/{id}", response_model=schemas.Node, tags=["Nodes"])
def update_node(id: int, node: schemas.NodeBase, db: Session = Depends(get_db)):
    db_node = crud.get_node(db, id=id)
    if not db_node:
        raise HTTPException(status_code=400, detail="Node not found")
    try:
        db_node_mod = crud.get_node_by_host_port(db, address=node.address, port=node.port)
        # mudou host ou porta e o novo ja existe
        if (node.address != db_node.address or node.port != db_node.port) and db_node_mod:
            raise HTTPException(status_code=400, detail=f"Node {node.address}:{node.port} already registered")
        ret = crud.update_node(db=db, db_node=db_node, userdata=node)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    nodes_fetcher.stop(f"{db_node.address}:{db_node.port}")
    if db_node.fetch_interval_type == "s":
        nodes_fetcher.schedule(f"{db_node.address}:{db_node.port}", node, fetch_node, sec=db_node.fetch_interval)
    else:
        nodes_fetcher.schedule(f"{db_node.address}:{db_node.port}", node, fetch_node, min=db_node.fetch_interval)
    return ret


@router.delete(f"{url_base}/{{id}}", response_model=schemas.Node, tags=["Nodes"])
def delete_node(id: int, db: Session = Depends(get_db)):
    db_node = crud.get_node(db, id=id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    nodes_fetcher.stop(f"{db_node.address}:{db_node.port}")
    crud.delete_node(db, db_node)
    return db_node


@router.get(url_base, response_model=list[schemas.NodeStatus], tags=["Nodes"])
def read_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    nodes = crud.get_nodes(db, skip=skip, limit=limit)
    return nodes


@router.get(f"{url_base}/{{id}}", response_model=schemas.NodeStatus, tags=["Nodes"])
def read_node(id: int, db: Session = Depends(get_db)):
    db_node = crud.get_node(db, id=id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    db_node.status = True
    return db_node