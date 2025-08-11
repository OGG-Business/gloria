import structlog

audit_log = structlog.get_logger("audit")

def log_audit(action: str, target: str, actor_subject: str | None, details: str | None = None):
    audit_log.info("audit", action=action, target=target, actor_subject=actor_subject, details=details)