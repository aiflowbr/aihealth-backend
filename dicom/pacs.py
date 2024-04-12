from pydicom.dataset import Dataset
from pynetdicom.sop_class import (
    StudyRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelMove,
    # ModalityWorklistInformationFind,
    PatientRootQueryRetrieveInformationModelFind,
    ComputedRadiographyImageStorage,
    PatientRootQueryRetrieveInformationModelMove,
)
import dcm
import time


ds = Dataset()
# ds.Modality = ""  # "DX"
ds.Modality = ""  # "DX"
# ds.ModalitiesInStudy = "DX"
ds.ModalitiesInStudy = ""
ds.AccessionNumber = ""
ds.StudyDate = "20240412-20240412"
# ds.StudyTime = "131800-132000"
ds.StudyTime = ""
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

network_parameters = {
    "server_address": "localhost",
    "server_port": 4242,
    "server_ae_title": "ORTHANC",
    "local_ae_title": "AIHEALTHMAC",
}
server = dcm.init_server(ae_title=network_parameters["local_ae_title"], listen_address="0.0.0.0", listen_port=11112)
i = 0
dcm.find_by_filter(ds, dw_studies=False, network_parameters=network_parameters)

# print("COUNTING SLEEP...")
# time.sleep(1000)