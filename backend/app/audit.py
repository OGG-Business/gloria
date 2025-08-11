from typing import Dict, Any
from sqlalchemy.orm import Session
from .models import AuditLog


def write_audit_log(db: Session, trace_id: str, actor: str, action: str, entity: str, entity_id: str, details: Dict[str, Any]):
    record = AuditLog(
        trace_id=trace_id,
        actor=actor,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details,
    )
    db.add(record)
    db.commit()