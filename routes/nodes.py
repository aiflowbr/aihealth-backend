from fastapi import Depends
from sqlalchemy.orm import Session

def routes(app, url_base, crud, models, schemas, get_db):
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


    @app.get(url_base, response_model=list[schemas.Node], tags=["Nodes"])
    def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        users = crud.get_nodes(db, skip=skip, limit=limit)
        return users


    # @app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
    # def read_user(user_id: int, db: Session = Depends(get_db)):
    #     db_user = crud.get_user(db, user_id=user_id)
    #     if db_user is None:
    #         raise HTTPException(status_code=404, detail="User not found")
    #     return db_user