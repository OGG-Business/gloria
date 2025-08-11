import os
from ..core.config import settings


def is_sanctioned_name(name: str) -> bool:
    blocklist = os.environ.get("SANCTIONS_BLOCKLIST_NAMES", "").lower().split(",")
    normalized = name.strip().lower()
    return normalized in {n.strip() for n in blocklist if n.strip()}


def validate_transfer_rules(creditor_name: str, amount: float):
    if amount >= settings.aml_block_threshold_usd:
        raise ValueError("Amount exceeds AML threshold")
    if is_sanctioned_name(creditor_name):
        raise ValueError("Beneficiary appears on sanctions blocklist")