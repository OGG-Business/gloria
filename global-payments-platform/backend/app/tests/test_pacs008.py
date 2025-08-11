from app.transfers.iso20022.pacs008 import build_pacs008_xml, validate_pacs008

def test_build_validate():
    xml = build_pacs008_xml("DE12500105170648489890","FR1420041010050500013M02606","DEUTDEFF",100.00,"USD","REF")
    ok, err = validate_pacs008(xml)
    assert ok