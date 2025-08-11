from sqlalchemy.orm import Session
from ..models import Transfer
from ..core.config import settings
from ..iso20022.pacs008 import build_pacs008_xml


def send_pacs008_via_swift(db: Session, transfer: Transfer) -> None:
    xml = build_pacs008_xml(transfer)
    if settings.swift_mode == "dry":
        return
    if settings.swift_mode == "rest":
        import httpx
        cert = None
        verify = True
        if settings.swift_rest_mtls:
            cert = (settings.swift_client_cert_path, settings.swift_client_key_path)
            verify = settings.swift_ca_cert_path or True
        with httpx.Client(base_url=settings.swift_rest_base_url or "", cert=cert, verify=verify, timeout=10) as client:
            resp = client.post("/payments", content=xml, headers={"Content-Type": "application/xml"})
            resp.raise_for_status()
    elif settings.swift_mode in ("sftp", "as4"):
        # Placeholder: implement respective transports
        pass