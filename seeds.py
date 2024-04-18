from database import schemas
from database.database import SessionLocal 
from routes import nodes, settings

def do_seeds():
    db = SessionLocal()
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
        nodes.create_node(
            schemas.NodeBase(
                **{
                    "aetitle": "PACS2",
                    "address": "localhost",
                    "port": 4243,
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