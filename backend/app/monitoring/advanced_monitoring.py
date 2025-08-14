"""
Monitoring simplifié pour Banking Transfer Platform
"""

import structlog
from datetime import datetime, timezone
from typing import Dict, Any

logger = structlog.get_logger(__name__)

class AdvancedMonitoring:
    """Système de monitoring simplifié"""
    
    def __init__(self):
        logger.info("Monitoring simplifié initialisé")
        self.metrics = {}

    def record_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Enregistre une requête HTTP"""
        logger.info("Requête HTTP enregistrée", method=method, endpoint=endpoint, status=status, duration=duration)

    def record_transfer_request(self, connector: str, currency: str, amount: float, status: str):
        """Enregistre une demande de transfert"""
        logger.info("Transfert enregistré", connector=connector, currency=currency, amount=amount, status=status)

    def add_custom_metric(self, name: str, value: Any, labels: Dict[str, str] = None):
        """Ajoute une métrique personnalisée"""
        self.metrics[name] = {
            "value": value,
            "labels": labels or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        logger.info("Métrique ajoutée", name=name, value=value)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Récupère un résumé des métriques"""
        return {
            "metrics_count": len(self.metrics),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": self.metrics
        }

# Instance globale du monitoring
monitoring = AdvancedMonitoring()