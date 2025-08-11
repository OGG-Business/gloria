from stdnum import iban as std_iban
from stdnum import bic as std_bic

def validate_iban(iban: str) -> bool:
    try:
        std_iban.validate(iban)
        return True
    except Exception:
        return False


def validate_bic(bic: str) -> bool:
    try:
        std_bic.validate(bic)
        return True
    except Exception:
        return False