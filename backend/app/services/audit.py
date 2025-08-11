import hashlib
import time
from typing import Optional, List, Dict

_audit_chain: List[Dict] = []
_prev_hash = b""


def append_audit(action: str, subject: str, actor: str, details: dict) -> dict:
    global _prev_hash
    payload = {
        "ts": int(time.time()),
        "action": action,
        "subject": subject,
        "actor": actor,
        "details": details,
    }
    h = hashlib.sha256()
    h.update(_prev_hash + str(payload).encode("utf-8"))
    digest = h.hexdigest()
    entry = {**payload, "prev_hash": _prev_hash.hex(), "hash": digest}
    _audit_chain.append(entry)
    _prev_hash = bytes.fromhex(digest)
    return entry


def get_audit_tail(n: int = 50) -> List[Dict]:
    return _audit_chain[-n:]