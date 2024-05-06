from fastapi import APIRouter
from fetchers import nodes_fetcher

router = APIRouter()

@router.get("", tags=["Fetchers"])
def schedules():
    return nodes_fetcher.list()