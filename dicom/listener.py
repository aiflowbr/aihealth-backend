from dicom import dcm
from settings import get_settings

dicom_listener = None


def start_listener():
    dicom_listener = dcm.init_server(
        ae_title=get_settings()["LOCAL_AETITLE"],
        listen_address="0.0.0.0",
        listen_port=get_settings()["LOCAL_PORT"],
    )
    return dicom_listener


def stop_listener():
    if dicom_listener is not None:
        dicom_listener.shutdown()
