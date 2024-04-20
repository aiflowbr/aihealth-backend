from pydicom.dataset import Dataset
from pydicom import datadict
from pydicom.tag import Tag
from pydicom.valuerep import PersonName
from dicom import dcm
from datetime import datetime, timedelta
from settings import get_settings
from cron import CronManager
from database.database import SessionLocal
from ws import send_to_all, ws_clients
from database import crud

last_data = {}

nodes_fetcher = CronManager(debug=False)


def sort_key(item):
    study_datetime = datetime.strptime(
        item["StudyDate"] + item["StudyTime"], "%Y%m%d%H%M%S.%f"
    )
    return study_datetime


def get_value_original_string(key, obj):
    # if key == "PatientName" or key == "ReferringPhysicianName":  # and "original_string" in obj:
    if isinstance(obj, PersonName):
        return f"{obj}"
    return obj


def gen_dicom_filter(datestart, dateend):
    ds = Dataset()
    # ds.Modality = ""  # "DX"
    ds.Modality = ""  # "DX"
    # ds.ModalitiesInStudy = "DX"
    ds.ModalitiesInStudy = ""
    ds.AccessionNumber = ""
    ds.StudyDate = f"{datestart.strftime('%Y%m%d')}-{dateend.strftime('%Y%m%d')}"
    ds.StudyTime = f"{datestart.strftime('%H%M%S')}-{dateend.strftime('%H%M%S')}"  # "170000-173000"
    print(f"Date: {ds.StudyDate}, Time: {ds.StudyTime}")
    # ds.StudyTime = ""
    ds.TimezoneOffsetFromUTC = ""
    # ds.PatientID = ""  # "1795017"
    ds.PatientID = ""
    # ds.PatientPosition = "PA\\AP"
    ds.PatientPosition = ""
    ds.PatientName = ""
    ds.PatientBirthDate = ""
    ds.SeriesInstanceUID = ""
    ds.StudyInstanceUID = ""
    ds.InstanceNumber = ""
    ds.StudyID = ""
    # ds.StudyDescription = "TORAX"
    ds.StudyDescription = ""
    ds.FileSetID = ""
    ds.ModalitiesInStudy = ""
    ds.NumberOfStudyRelatedInstances = ""
    ds.ReferringPhysicianName = ""
    ds.QueryRetrieveLevel = "STUDY"
    ds.ImageComments = ""
    return ds


async def check_alive(node):
    client = dcm.init_client(
        client_ae_title=get_settings()["LOCAL_AETITLE"],
        address=node.address,
        port=int(node.port),
        ae_title=node.aetitle,
    )
    connected = client.is_established
    client.kill()
    return connected


async def fetch_node(new_node):
    global last_data
    node_key = f"{new_node.address}:{new_node.port}"
    if new_node.id not in last_data:
        last_data[new_node.id] = []
    db = SessionLocal()
    print(
        f"FETCH NODE... {new_node.aetitle} {new_node.address}:{new_node.port} (interval: {new_node.fetch_interval}{new_node.fetch_interval_type})"
    )
    now = datetime.now()
    dateend = now
    datestart = now - timedelta(hours=1)
    ds = gen_dicom_filter(datestart, dateend)
    client = dcm.init_client(
        client_ae_title=get_settings()["LOCAL_AETITLE"],
        address=new_node.address,
        port=int(new_node.port),
        ae_title=new_node.aetitle,
    )
    sorted_data = []
    next_last_data = []
    server_state = False
    if client.is_established:
        server_state = True
        responses = client.send_c_find(
            ds, dcm.StudyRootQueryRetrieveInformationModelFind
        )
        datasets = []
        for status, dataset in responses:
            if "PatientID" in dir(dataset):
                obj = dataset.to_json_dict()
                nobj = {
                    z[4]: get_value_original_string(z[4], dataset[z[4]]._value)
                    for z in [datadict.get_entry(Tag(k)) for k in obj.keys()]
                }
                key_last_check = f"{nobj['SeriesInstanceUID']}_{nobj['InstanceNumber']}"
                try:
                    last_data[new_node.id].index(key_last_check)
                except Exception:
                    datasets.append(nobj)
                next_last_data.append(key_last_check)
        sorted_data = sorted(datasets, key=sort_key, reverse=True)
        await send_to_all({"new_data": {"node_id": new_node.id, "data": sorted_data}})

    last_data[new_node.id] = next_last_data
    # notify state changed
    if nodes_fetcher.get_alive(node_key) != server_state:
        nodes_fetcher.set_alive(node_key, server_state)
        print(f"SENDING TO WS: {len(ws_clients)}")
        await send_to_all({"input_nodes": crud.get_nodes_all_status(db)})

    print(
        f"NODE RESPONSE... {new_node.aetitle} {new_node.address}:{new_node.port} len({len(sorted_data)})"
    )

    return sorted_data
