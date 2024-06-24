from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.crud import get_nodes_all
from database.database import SessionLocal
from fetchers import fetch_node, nodes_fetcher
from seeds import do_seeds


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing...")
    do_seeds()
    db_nodes = get_nodes_all(SessionLocal())
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


async def startup_event_handler():
    print("Backend STARTED")


async def shutdown_event_handler():
    print("Backend FINISHED")


def initialize_fastapi():
    app = FastAPI(
        lifespan=lifespan,
        swagger_ui_parameters={
            "persistAuthorization": True,
            "docExpansion": None,
        },
    )
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=origins,
        allow_headers=origins,
    )
    app.add_event_handler("startup", startup_event_handler)
    app.add_event_handler("shutdown", shutdown_event_handler)
    return app
