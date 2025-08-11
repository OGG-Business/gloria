from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime
from typing import Dict

NS = "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10"

def _tag(name: str) -> str:
    return f"{{{NS}}}{name}"


def build_pacs008(transfer: Dict) -> str:
    doc = Element(_tag("FIToFICstmrCdtTrf"))
    grp_hdr = SubElement(doc, _tag("GrpHdr"))
    SubElement(grp_hdr, _tag("MsgId")).text = transfer["id"]
    SubElement(grp_hdr, _tag("CreDtTm")).text = datetime.utcnow().isoformat()
    SubElement(grp_hdr, _tag("NbOfTxs")).text = "1"

    cdt_trf_tx_inf = SubElement(doc, _tag("CdtTrfTxInf"))
    pmt_id = SubElement(cdt_trf_tx_inf, _tag("PmtId"))
    SubElement(pmt_id, _tag("EndToEndId")).text = transfer["id"]

    intr_bk_sttlm_amt = SubElement(cdt_trf_tx_inf, _tag("IntrBkSttlmAmt"))
    intr_bk_sttlm_amt.set("Ccy", transfer["currency"]) 
    intr_bk_sttlm_amt.text = f"{transfer['amount']:.2f}"

    dbtr = SubElement(cdt_trf_tx_inf, _tag("Dbtr"))
    SubElement(dbtr, _tag("Nm")).text = transfer.get("debtor_name", "Debtor")
    dbtr_acct = SubElement(cdt_trf_tx_inf, _tag("DbtrAcct"))
    id_el = SubElement(dbtr_acct, _tag("Id"))
    SubElement(id_el, _tag("IBAN")).text = transfer["debtor_iban"]

    cdtr = SubElement(cdt_trf_tx_inf, _tag("Cdtr"))
    SubElement(cdtr, _tag("Nm")).text = transfer.get("creditor_name", "Creditor")
    cdtr_acct = SubElement(cdt_trf_tx_inf, _tag("CdtrAcct"))
    id_el2 = SubElement(cdtr_acct, _tag("Id"))
    SubElement(id_el2, _tag("IBAN")).text = transfer["creditor_iban"]

    rmt_inf = SubElement(cdt_trf_tx_inf, _tag("RmtInf"))
    if transfer.get("remittance_info"):
        SubElement(rmt_inf, _tag("Ustrd")).text = transfer["remittance_info"]

    xml_bytes = tostring(doc, encoding="utf-8")
    return xml_bytes.decode()


def map_to_mt103(transfer: Dict) -> str:
    lines = [
        "{1:F01BANKBICXXXX0000000000}",
        "{2:O1030000000000BANKBICXXXX0000000000000000N}",
        ":20:" + transfer["id"],
        ":32A:" + datetime.utcnow().strftime("%y%m%d") + transfer["currency"] + f"{transfer['amount']:.2f}",
        ":50K:/" + transfer["debtor_iban"],
        ":59:/" + transfer["creditor_iban"],
        ":70:" + (transfer.get("remittance_info") or ""),
        "-"
    ]
    return "\n".join(lines)