from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from database import crud, schemas
from database.database import get_db

router = APIRouter()
url_base = ""
# url_base_id = f"{url_base}/{{id}}"
url_base_id = "/{id}"


@router.post(url_base, response_model=schemas.NeuralNetwork, tags=["NeuralNetworks"])
def create_neural_network(
    neural_network: schemas.NeuralNetworkBase, db: Session = Depends(get_db)
):
    db_neural_network = crud.get_neural_network_by_name(db, name=neural_network.name)
    if db_neural_network:
        raise HTTPException(
            status_code=400, detail="Neural network model already registered"
        )
    return crud.create_neural_network(db=db, neural_network=neural_network)


@router.put(url_base_id, response_model=schemas.NeuralNetwork, tags=["NeuralNetworks"])
def update_neural_network(
    id: int, neural_network: schemas.NeuralNetworkUpdate, db: Session = Depends(get_db)
):
    db_neural_network = crud.get_neural_network(db, id=id)
    if not db_neural_network:
        raise HTTPException(status_code=400, detail="Neural network model not found")
    try:
        ret = crud.update_neural_network(
            db=db, db_neural_network=db_neural_network, userdata=neural_network
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ret


@router.delete(
    url_base_id, response_model=schemas.NeuralNetwork, tags=["NeuralNetworks"]
)
def delete_neural_network(id: int, db: Session = Depends(get_db)):
    db_neural_network = crud.get_neural_network(db, id=id)
    if db_neural_network is None:
        raise HTTPException(status_code=404, detail="Neural network model not found")
    crud.delete_neural_network(db, db_neural_network)
    return db_neural_network


@router.get(
    url_base, response_model=list[schemas.NeuralNetwork], tags=["NeuralNetworks"]
)
def read_neural_networks(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_neural_networks(db, skip=skip, limit=limit)


@router.get(url_base_id, response_model=schemas.NeuralNetwork, tags=["NeuralNetworks"])
def read_neural_network(id: int, db: Session = Depends(get_db)):
    neural_network = crud.get_neural_network(db, id=id)
    if neural_network is None:
        raise HTTPException(status_code=404, detail="Neural network model not found")
    return neural_network
