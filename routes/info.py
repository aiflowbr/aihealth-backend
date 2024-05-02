from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Info"])
def info():
    return {"appname": "AIHEALTH", "version": "1.0"}