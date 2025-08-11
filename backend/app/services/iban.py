from typing import Optional
from schwifty import IBAN, BIC


def validate_iban(iban_str: str) -> bool:
    try:
        IBAN(iban_str)
        return True
    except Exception:
        return False


def normalize_iban(iban_str: str) -> Optional[str]:
    try:
        return IBAN(iban_str).compact
    except Exception:
        return None


def validate_bic(bic_str: str) -> bool:
    try:
        BIC(bic_str)
        return True
    except Exception:
        return False