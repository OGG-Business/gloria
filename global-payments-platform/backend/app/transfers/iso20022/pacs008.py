from lxml import etree
from decimal import Decimal
import os
from app.config import get_settings

NS = {"doc": "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10"}
settings = get_settings()
_schema = None

def _get_schema():
    global _schema
    if _schema is not None:
        return _schema
    xsd_dir = settings.iso20022_xsd_dir
    if not xsd_dir:
        _schema = None
        return None
    # Expect the official XSDs to be placed in this directory
    main_xsd = os.path.join(xsd_dir, "pacs.008.001.10.xsd")
    if not os.path.exists(main_xsd):
        _schema = None
        return None
    with open(main_xsd, 'rb') as f:
        xmlschema_doc = etree.parse(f)
    _schema = etree.XMLSchema(xmlschema_doc)
    return _schema


def build_pacs008_xml(debtor_iban: str, creditor_iban: str, creditor_bic: str, amount: Decimal, currency: str, reference: str | None) -> str:
    root = etree.Element("Document", nsmap={None: NS["doc"]})
    cdt = etree.SubElement(root, "FIToFICstmrCdtTrf")
    grp = etree.SubElement(cdt, "GrpHdr")
    etree.SubElement(grp, "MsgId").text = reference or "MSG-REF"
    etree.SubElement(grp, "NbOfTxs").text = "1"

    cdtinf = etree.SubElement(cdt, "CdtTrfTxInf")
    amt = etree.SubElement(cdtinf, "IntrBkSttlmAmt", Ccy=currency)
    amt.text = f"{amount:.2f}"
    cdtr = etree.SubElement(cdtinf, "Cdtr")
    nm = etree.SubElement(cdtr, "Nm"); nm.text = "Beneficiary"
    cdtracct = etree.SubElement(cdtinf, "CdtrAcct")
    idn = etree.SubElement(cdtracct, "Id"); iban = etree.SubElement(idn, "IBAN"); iban.text = creditor_iban
    cdtragt = etree.SubElement(cdtinf, "CdtrAgt"); fin = etree.SubElement(cdtragt, "FinInstnId"); bic = etree.SubElement(fin, "BICFI"); bic.text = creditor_bic

    dbtracct = etree.SubElement(cdtinf, "DbtrAcct")
    idd = etree.SubElement(dbtracct, "Id"); diban = etree.SubElement(idd, "IBAN"); diban.text = debtor_iban

    if reference:
        rmt = etree.SubElement(cdtinf, "RmtInf"); ustrd = etree.SubElement(rmt, "Ustrd"); ustrd.text = reference

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8").decode()


def validate_pacs008(xml_str: str) -> tuple[bool, str | None]:
    try:
        doc = etree.fromstring(xml_str.encode())
        schema = _get_schema()
        if schema is not None:
            schema.assertValid(doc)
        return True, None
    except Exception as exc:
        return False, str(exc)