from app.utils.iban import validate_iban, validate_bic

def test_validate_iban():
    assert validate_iban("DE12500105170648489890")
    assert not validate_iban("INVALID")

def test_validate_bic():
    assert validate_bic("DEUTDEFF")
    assert not validate_bic("BADBIC")