from lxml import etree
from ..models import Transfer


def build_pacs008_xml(transfer: Transfer) -> bytes:
    ns = {
        "Doc": "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02",
    }
    root = etree.Element("Doc:Document", nsmap=ns)
    fi_to_fi = etree.SubElement(root, "Doc:FIToFICstmrCdtTrf")
    grp_hdr = etree.SubElement(fi_to_fi, "Doc:GrpHdr")
    msg_id = etree.SubElement(grp_hdr, "Doc:MsgId")
    msg_id.text = f"TRF-{transfer.id}"

    cdt_trf_tx_inf = etree.SubElement(fi_to_fi, "Doc:CdtTrfTxInf")

    amt = etree.SubElement(cdt_trf_tx_inf, "Doc:IntrBkSttlmAmt", Ccy=transfer.currency)
    amt.text = f"{transfer.amount}"

    cdtr = etree.SubElement(cdt_trf_tx_inf, "Doc:Cdtr")
    nm = etree.SubElement(cdtr, "Doc:Nm")
    nm.text = transfer.creditor_name

    cdtr_acct = etree.SubElement(cdt_trf_tx_inf, "Doc:CdtrAcct")
    id_ = etree.SubElement(cdtr_acct, "Doc:Id")
    iban = etree.SubElement(id_, "Doc:IBAN")
    iban.text = transfer.creditor_iban

    dbtr_acct = etree.SubElement(cdt_trf_tx_inf, "Doc:DbtrAcct")
    id_dbtr = etree.SubElement(dbtr_acct, "Doc:Id")
    iban_dbtr = etree.SubElement(id_dbtr, "Doc:IBAN")
    iban_dbtr.text = transfer.debtor_account.iban

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")