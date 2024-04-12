#!/usr/bin/env python
import netifaces as ni
import os
import shutil
import ssl
import pydicom
from pydicom.filewriter import write_file_meta_info
from pynetdicom import AE, evt, AllStoragePresentationContexts, debug_logger
from pydicom.uid import ExplicitVRLittleEndian
import pkg_resources

from pydicom.dataset import Dataset
from datetime import datetime

from pynetdicom.sop_class import (
    StudyRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelMove,
    PatientRootQueryRetrieveInformationModelFind,
    ComputedRadiographyImageStorage,
    PatientRootQueryRetrieveInformationModelMove,
    CompositeInstanceRootRetrieveMove
)


def get_network_interfaces():
    ips = []
    interfaces = ni.interfaces()
    for interface in interfaces:
        addrs = ni.ifaddresses(interface)
        for protocol in (ni.AF_INET, ni.AF_INET6):
            if protocol in addrs:
                for address in addrs[protocol]:
                    # Filtrar endereços de loopback e link-local
                    ip = address["addr"]
                    if (
                        not ip.startswith("127.")
                        and not ip.startswith("fe80:")
                        and not ip == "::1"
                    ):
                        ips.append(ip)
    return ips


CERT_DIR = pkg_resources.resource_filename("pynetdicom", "tests/cert_files")

SERVER_CERT, SERVER_KEY = (
    os.path.join(CERT_DIR, "server.crt"),
    os.path.join(CERT_DIR, "server.key"),
)
CLIENT_CERT, CLIENT_KEY = (
    os.path.join(CERT_DIR, "client.crt"),
    os.path.join(CERT_DIR, "client.key"),
)
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
context.load_verify_locations(cafile=CLIENT_CERT)
context.maximum_version = ssl.TLSVersion.TLSv1_2

ips = get_network_interfaces()
print("Endereços IP disponíveis:", ips)


def handle_store(event):
    print("RECEIVING FILE...")
    fpath = f"./storage/{event.request.AffectedSOPInstanceUID}.dcm"
    with open(fpath, "wb") as f:
        f.write(b"\x00" * 128)
        f.write(b"DICM")
        # Encode and write the File Meta Information
        write_file_meta_info(f, event.file_meta)
        # Write the encoded dataset
        f.write(event.request.DataSet.getvalue())
        f.close()
    dcm = pydicom.dcmread(fpath)
    npath = f"./storage/studies/{dcm.StudyInstanceUID}/{event.request.AffectedSOPInstanceUID}.dcm"
    os.makedirs(f"./storage/studies/{dcm.StudyInstanceUID}", exist_ok=True)
    os.rename(fpath, npath)

    # Don't store anything but respond with `Success`
    return 0x0000


handlers = [(evt.EVT_C_STORE, handle_store)]


def init_server(ae_title="AIHEALTH", listen_address="0.0.0.0", listen_port=11112):
    print(f"INITIALIZING DICOM LISTENER: AETITLE={ae_title}, PORT={listen_port}")
    ########################
    # LISTENER
    ae_server = AE(ae_title=ae_title)
    ae_server.maximum_pdu_size = 0
    ae_server.supported_contexts = AllStoragePresentationContexts
    scp = ae_server.start_server(
        (listen_address, listen_port), block=False, evt_handlers=handlers, ae_title=ae_title
    )
    return scp


def init_client(
    client_ae_title="AIHEALTH", address=None, port=None, ae_title=None, debug=False
):
    if debug:
        debug_logger()
    ae = AE(ae_title=client_ae_title)
    ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)
    ae.add_requested_context(
        StudyRootQueryRetrieveInformationModelMove,
        transfer_syntax=ExplicitVRLittleEndian,
    )
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
    ae.add_requested_context(ComputedRadiographyImageStorage)
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelMove)

    # # Create our Identifier (query) dataset
    # # ds = Dataset()
    # # ds.PatientName = "CITIZEN^Jan"
    # # ds.QueryRetrieveLevel = "PATIENT"
    # ds = Dataset()
    # # ds.SOPClassesInStudy = ""
    # ds.Modality = "DX"
    # ds.AccessionNumber = ""
    # # ds.StudyDate = datetime.now().strftime(
    # #     "%Y%m%d"
    # # )  # Define a data de hoje no formato AAAAMMDD
    # # ds.StudyDate = "20240125-20240125"
    # ds.StudyDate = "20240125-20240125"
    # ds.StudyTime = ""
    # # ds.PatientID = "1771635"
    # ds.PatientID = "1795017"  # "1160248"  # 1771635
    # ds.PatientName = ""
    # ds.PatientBirthDate = ""
    # ds.SeriesInstanceUID = ""
    # ds.StudyInstanceUID = ""
    # ds.StudyID = ""
    # # ds.StudyDescription = "%TORAX%"
    # ds.StudyDescription = "TORAX"
    # ds.FileSetID = ""
    # ds.ModalitiesInStudy = ""
    # ds.NumberOfStudyRelatedInstances = ""
    # # ds.SeriesNumber = ''
    # # ds.QueryRetrieveLevel = "STUDY"  # Nível da consulta
    # # ds.PatientID = ""
    # # ds.StudyInstanceUID = ""
    # # ds.QueryRetrieveLevel = "STUDY"
    # ds.ReferringPhysicianName = ""
    # ds.QueryRetrieveLevel = "STUDY"

    # Associate with the peer AE at IP 127.0.0.1 and port 11112
    assoc = ae.associate(address, port, ae_title=ae_title)
    assoc.connection_timeout = None
    assoc = ae.associate(address, port, ae_title=ae_title)
    return assoc


def find_by_filter(ds, dw_studies=False, network_parameters=None):
    if network_parameters is None:
        raise "Error: network parameters"

    client = init_client(
        client_ae_title=network_parameters["local_ae_title"],
        address=network_parameters["server_address"],
        port=network_parameters["server_port"],
        ae_title=network_parameters["server_ae_title"],
    )
    if client.is_established:
        responses = client.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)
        datasets = []
        for status, dataset in responses:
            datasets.append(dataset)
        print(f"LEN: {len(datasets)}")
        print(datasets[0])
    # if client.is_established:
    #     responses = client.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)
    #     # Processar as respostas
    #     to_download = []
    #     for status, dataset in responses:
    #         if status:
    #             if dataset:
    #                 print(dataset)
    #                 if dw_studies:
    #                     study_path = f"./storage/studies/{dataset.StudyInstanceUID}"
    #                     if not os.path.isdir(study_path):
    #                         to_download.append(dataset.StudyInstanceUID)
    #             # else:
    #             #     print(f"Status recebido sem dataset correspondente. {status}")
    #         else:
    #             print("Nenhuma resposta ou ocorreu um erro.")
    #     client.release()

    #     if dw_studies:
    #         for k, v in enumerate(to_download):
    #             study_path = f"./storage/studies/{v}"

    #             n_client = init_client(
    #                 client_ae_title=network_parameters["local_ae_title"],
    #                 address=network_parameters["server_address"],
    #                 port=network_parameters["server_port"],
    #                 ae_title=network_parameters["server_ae_title"],
    #             )
    #             if n_client.is_established:
    #                 # REQUEST STUDY TO PACS SEND TO LOCAL SERVER
    #                 ds = Dataset()
    #                 ds.QueryRetrieveLevel = "STUDY"
    #                 ds.StudyInstanceUID = v

    #                 if not os.path.isdir(study_path):
    #                     print(f"REQUESTING Study to DOWNLOAD: {v}...")
    #                     responses = n_client.send_c_move(
    #                         ds,
    #                         network_parameters["local_ae_title"],
    #                         StudyRootQueryRetrieveInformationModelMove,
    #                     )
    #                     for status, identifier in responses:
    #                         if status:
    #                             print(
    #                                 "C-MOVE query status: 0x{0:04x}".format(
    #                                     status.Status
    #                                 )
    #                             )
    #                         else:
    #                             shutil.rmtree(study_path)
    #                             print(
    #                                 "Connection timed out, was aborted or received invalid response"
    #                             )
    #                             print(status, identifier)

    #                 n_client.release()
    # else:
    #     print("Association rejected, aborted or never connected")
