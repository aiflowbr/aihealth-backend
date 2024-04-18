from pydicom.dataset import Dataset
from pydicom import datadict
from pydicom.tag import Tag, BaseTag, TagType
from pydicom.valuerep import PersonName
from dicom import dcm
from datetime import datetime, timedelta
from database import crud, models, schemas
import settings


def sort_key(item):
    study_datetime = datetime.strptime(
        item["StudyDate"] + item["StudyTime"], "%Y%m%d%H%M%S.%f"
    )
    return study_datetime


def get_value_original_string(key, obj):
    if key == "PatientName":  # and "original_string" in obj:
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


def fetch_node(new_node):
    print(
        f"FETCH NODE... {new_node.aetitle} {new_node.address}:{new_node.port} (interval: {new_node.fetch_interval}{new_node.fetch_interval_type})"
    )
    now = datetime.now()
    dateend = now
    datestart = now - timedelta(hours=1)
    ds = gen_dicom_filter(datestart, dateend)

    client = dcm.init_client(
        client_ae_title=settings.LOCAL_AETITLE,
        address=new_node.address,
        port=int(new_node.port),
        ae_title=new_node.aetitle,
    )
    if client.is_established:
        responses = client.send_c_find(
            ds, dcm.StudyRootQueryRetrieveInformationModelFind
        )
        datasets = []
        for status, dataset in responses:
            # keys = [
            #     "AccessionNumber",
            #     "ImageComments",
            #     "ModalitiesInStudy",
            #     "Modality",
            #     "NumberOfStudyRelatedInstances",
            #     "PatientBirthDate",
            #     "PatientID",
            #     "PatientName",
            #     "PatientPosition",
            #     "QueryRetrieveLevel",
            #     "ReferringPhysicianName",
            #     "RetrieveAETitle",
            #     "SeriesInstanceUID",
            #     "SpecificCharacterSet",
            #     "StudyDate",
            #     "StudyDescription",
            #     "StudyID",
            #     "StudyInstanceUID",
            #     "StudyTime",
            #     "TimezoneOffsetFromUTC"]
            # # if "PatientID" in dir(dataset):
            if "PatientID" in dir(dataset):
                obj = dataset.to_json_dict()
                nobj = {
                    z[4]: get_value_original_string(z[4], dataset[z[4]]._value)
                    for z in [datadict.get_entry(Tag(k)) for k in obj.keys()]
                }
                datasets.append(nobj)
                # taginfo = datadict.get_entry(Tag("00204000"))
                # key, desc = taginfo[4], taginfo[2]
                # datasets.append({**{k: dataset[k]._value for k in keys}, "json": obj})
            #     datasets.append({**{k: dataset[k]._value for k in keys}, "json": dataset.to_json_dict()})
            # for k in dataset:
            #     print(k)
        sorted_data = sorted(datasets, key=sort_key, reverse=True)
        print(f"RESULT: len({len(sorted_data)})")
        return sorted_data
