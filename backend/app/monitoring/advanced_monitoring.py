"""
Monitoring avancé pour Banking Transfer Platform
Alertes, métriques et dashboards en temps réel
"""

import asyncio
import time
import psutil
import structlog
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, push_to_gateway
)
import aiohttp
import json

logger = structlog.get_logger(__name__)

@dataclass
class AlertRule:
    """Règle d'alerte"""
    name: str
    description: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: str  # 'critical', 'warning', 'info'
    threshold: float
    cooldown: int = 300  # secondes
    last_triggered: Optional[datetime] = None

@dataclass
class Metric:
    """Métrique personnalisée"""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class AdvancedMonitoring:
    """Système de monitoring avancé avec alertes"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # Métriques Prometheus
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        self.transfer_requests_total = Counter(
            'transfer_requests_total',
            'Total transfer requests',
            ['connector', 'currency', 'status'],
            registry=self.registry
        )
        
        self.transfer_amount_total = Counter(
            'transfer_amount_total',
            'Total transfer amount',
            ['connector', 'currency'],
            registry=self.registry
        )
        
        self.active_transfers = Gauge(
            'active_transfers',
            'Number of active transfers',
            ['connector', 'status'],
            registry=self.registry
        )
        
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_percent',
            'Memory usage percentage',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_percent',
            'Disk usage percentage',
            registry=self.registry
        )
        
        self.database_connections = Gauge(
            'database_connections',
            'Number of database connections',
            registry=self.registry
        )
        
        self.redis_connections = Gauge(
            'redis_connections',
            'Number of Redis connections',
            registry=self.registry
        )
        
        # Alertes
        self.alerts: List[AlertRule] = []
        self.alert_history: List[Dict[str, Any]] = []
        
        # Métriques personnalisées
        self.custom_metrics: List[Metric] = []
        
        # Configuration
        self.prometheus_pushgateway = "http://prometheus-pushgateway:9091"
        self.grafana_api_url = "http://grafana-service:3000/api"
        self.alert_webhook_url = None
        
        self._setup_alert_rules()
        self._start_background_tasks()
        
        logger.info("Monitoring avancé initialisé")

    def _setup_alert_rules(self):
        """Configure les règles d'alerte"""
        
        # Alerte CPU élevé
        self.alerts.append(AlertRule(
            name="high_cpu_usage",
            description="CPU usage is above threshold",
            condition=lambda metrics: metrics.get('cpu_usage', 0) > 80,
            severity="warning",
            threshold=80
        ))
        
        # Alerte mémoire élevée
        self.alerts.append(AlertRule(
            name="high_memory_usage",
            description="Memory usage is above threshold",
            condition=lambda metrics: metrics.get('memory_usage', 0) > 85,
            severity="warning",
            threshold=85
        ))
        
        # Alerte disque plein
        self.alerts.append(AlertRule(
            name="high_disk_usage",
            description="Disk usage is above threshold",
            condition=lambda metrics: metrics.get('disk_usage', 0) > 90,
            severity="critical",
            threshold=90
        ))
        
        # Alerte taux d'erreur élevé
        self.alerts.append(AlertRule(
            name="high_error_rate",
            description="Error rate is above threshold",
            condition=lambda metrics: metrics.get('error_rate', 0) > 5,
            severity="critical",
            threshold=5
        ))
        
        # Alerte transferts échoués
        self.alerts.append(AlertRule(
            name="transfer_failures",
            description="Transfer failure rate is above threshold",
            condition=lambda metrics: metrics.get('transfer_failure_rate', 0) > 10,
            severity="critical",
            threshold=10
        ))
        
        # Alerte connectivité SWIFT
        self.alerts.append(AlertRule(
            name="swift_connectivity",
            description="SWIFT connectivity issues detected",
            condition=lambda metrics: metrics.get('swift_connectivity', True) is False,
            severity="critical",
            threshold=0
        ))
        
        # Alerte connectivité Mojaloop
        self.alerts.append(AlertRule(
            name="mojaloop_connectivity",
            description="Mojaloop connectivity issues detected",
            condition=lambda metrics: metrics.get('mojaloop_connectivity', True) is False,
            severity="critical",
            threshold=0
        ))

    def _start_background_tasks(self):
        """Démarre les tâches en arrière-plan"""
        asyncio.create_task(self._collect_system_metrics())
        asyncio.create_task(self._check_alerts())
        asyncio.create_task(self._push_metrics_to_prometheus())
        asyncio.create_task(self._cleanup_old_metrics())

    async def _collect_system_metrics(self):
        """Collecte les métriques système"""
        while True:
            try:
                # Métriques CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_cpu_usage.set(cpu_percent)
                
                # Métriques mémoire
                memory = psutil.virtual_memory()
                self.system_memory_usage.set(memory.percent)
                
                # Métriques disque
                disk = psutil.disk_usage('/')
                self.system_disk_usage.set((disk.used / disk.total) * 100)
                
                # Métriques réseau
                network = psutil.net_io_counters()
                
                # Métrique personnalisée pour les métriques système
                self.add_custom_metric("system_metrics", {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "disk_usage": (disk.used / disk.total) * 100,
                    "network_bytes_sent": network.bytes_sent,
                    "network_bytes_recv": network.bytes_recv
                })
                
                await asyncio.sleep(30)  # Collecte toutes les 30 secondes
                
            except Exception as e:
                logger.error("Erreur collecte métriques système", error=str(e))
                await asyncio.sleep(60)

    async def _check_alerts(self):
        """Vérifie les alertes"""
        while True:
            try:
                current_metrics = self._get_current_metrics()
                
                for alert in self.alerts:
                    # Vérification du cooldown
                    if (alert.last_triggered and 
                        datetime.now(timezone.utc) - alert.last_triggered < timedelta(seconds=alert.cooldown)):
                        continue
                    
                    # Vérification de la condition
                    if alert.condition(current_metrics):
                        await self._trigger_alert(alert, current_metrics)
                        alert.last_triggered = datetime.now(timezone.utc)
                
                await asyncio.sleep(60)  # Vérification toutes les minutes
                
            except Exception as e:
                logger.error("Erreur vérification alertes", error=str(e))
                await asyncio.sleep(120)

    def _get_current_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques actuelles"""
        metrics = {}
        
        # Métriques système
        metrics['cpu_usage'] = psutil.cpu_percent()
        metrics['memory_usage'] = psutil.virtual_memory().percent
        metrics['disk_usage'] = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
        
        # Métriques personnalisées récentes
        recent_metrics = [m for m in self.custom_metrics 
                         if datetime.now(timezone.utc) - m.timestamp < timedelta(minutes=5)]
        
        for metric in recent_metrics:
            if metric.name == "system_metrics":
                metrics.update(metric.labels)
            elif metric.name == "error_rate":
                metrics['error_rate'] = metric.value
            elif metric.name == "transfer_failure_rate":
                metrics['transfer_failure_rate'] = metric.value
            elif metric.name == "swift_connectivity":
                metrics['swift_connectivity'] = metric.value == 1
            elif metric.name == "mojaloop_connectivity":
                metrics['mojaloop_connectivity'] = metric.value == 1
        
        return metrics

    async def _trigger_alert(self, alert: AlertRule, metrics: Dict[str, Any]):
        """Déclenche une alerte"""
        alert_data = {
            "name": alert.name,
            "description": alert.description,
            "severity": alert.severity,
            "threshold": alert.threshold,
            "current_value": metrics.get(alert.name.split('_')[0] + '_usage', 0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics
        }
        
        self.alert_history.append(alert_data)
        
        # Limiter l'historique des alertes
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        logger.warning("Alerte déclenchée", 
                      alert_name=alert.name,
                      severity=alert.severity,
                      current_value=alert_data["current_value"])
        
        # Envoi webhook si configuré
        if self.alert_webhook_url:
            await self._send_webhook_alert(alert_data)
        
        # Envoi à Grafana si configuré
        await self._send_grafana_alert(alert_data)

    async def _send_webhook_alert(self, alert_data: Dict[str, Any]):
        """Envoie une alerte via webhook"""
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    self.alert_webhook_url,
                    json=alert_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
        except Exception as e:
            logger.error("Erreur envoi webhook alerte", error=str(e))

    async def _send_grafana_alert(self, alert_data: Dict[str, Any]):
        """Envoie une alerte à Grafana"""
        try:
            # Création d'une annotation Grafana
            annotation_data = {
                "dashboardId": 1,  # ID du dashboard
                "panelId": 1,      # ID du panel
                "time": int(datetime.now(timezone.utc).timestamp() * 1000),
                "timeEnd": int(datetime.now(timezone.utc).timestamp() * 1000),
                "tags": [alert_data["severity"], alert_data["name"]],
                "text": f"{alert_data['description']} - Current: {alert_data['current_value']}"
            }
            
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"{self.grafana_api_url}/annotations",
                    json=annotation_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
        except Exception as e:
            logger.error("Erreur envoi alerte Grafana", error=str(e))

    async def _push_metrics_to_prometheus(self):
        """Pousse les métriques vers Prometheus Pushgateway"""
        while True:
            try:
                push_to_gateway(
                    self.prometheus_pushgateway,
                    job='banking-transfer-backend',
                    registry=self.registry
                )
                await asyncio.sleep(15)  # Push toutes les 15 secondes
            except Exception as e:
                logger.error("Erreur push métriques Prometheus", error=str(e))
                await asyncio.sleep(60)

    async def _cleanup_old_metrics(self):
        """Nettoie les anciennes métriques"""
        while True:
            try:
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                self.custom_metrics = [m for m in self.custom_metrics 
                                     if m.timestamp > cutoff_time]
                await asyncio.sleep(3600)  # Nettoyage toutes les heures
            except Exception as e:
                logger.error("Erreur nettoyage métriques", error=str(e))
                await asyncio.sleep(3600)

    def record_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Enregistre une requête HTTP"""
        self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_transfer_request(self, connector: str, currency: str, amount: float, status: str):
        """Enregistre une demande de transfert"""
        self.transfer_requests_total.labels(connector=connector, currency=currency, status=status).inc()
        if status == "completed":
            self.transfer_amount_total.labels(connector=connector, currency=currency).inc(amount)

    def update_active_transfers(self, connector: str, status: str, count: int):
        """Met à jour le nombre de transferts actifs"""
        self.active_transfers.labels(connector=connector, status=status).set(count)

    def update_database_connections(self, count: int):
        """Met à jour le nombre de connexions base de données"""
        self.database_connections.set(count)

    def update_redis_connections(self, count: int):
        """Met à jour le nombre de connexions Redis"""
        self.redis_connections.set(count)

    def add_custom_metric(self, name: str, value: Any, labels: Dict[str, str] = None):
        """Ajoute une métrique personnalisée"""
        if labels is None:
            labels = {}
        
        if isinstance(value, dict):
            for key, val in value.items():
                self.custom_metrics.append(Metric(
                    name=f"{name}_{key}",
                    value=float(val) if isinstance(val, (int, float)) else 0,
                    labels=labels
                ))
        else:
            self.custom_metrics.append(Metric(
                name=name,
                value=float(value) if isinstance(value, (int, float)) else 0,
                labels=labels
            ))

    def record_error(self, error_type: str, error_message: str):
        """Enregistre une erreur"""
        self.add_custom_metric("errors_total", 1, {"type": error_type})
        logger.error("Erreur enregistrée", type=error_type, message=error_message)

    def record_connectivity_status(self, service: str, is_connected: bool):
        """Enregistre le statut de connectivité"""
        self.add_custom_metric(f"{service}_connectivity", 1 if is_connected else 0)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Récupère un résumé des métriques"""
        return {
            "system": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            },
            "alerts": {
                "total": len(self.alert_history),
                "critical": len([a for a in self.alert_history if a["severity"] == "critical"]),
                "warning": len([a for a in self.alert_history if a["severity"] == "warning"]),
                "recent": len([a for a in self.alert_history 
                             if datetime.now(timezone.utc) - datetime.fromisoformat(a["timestamp"]) < timedelta(hours=1)])
            },
            "custom_metrics_count": len(self.custom_metrics),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Récupère l'historique des alertes"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        return [a for a in self.alert_history 
                if datetime.fromisoformat(a["timestamp"]) > cutoff_time]

    def get_custom_metrics(self, name: str = None, hours: int = 24) -> List[Metric]:
        """Récupère les métriques personnalisées"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        metrics = [m for m in self.custom_metrics if m.timestamp > cutoff_time]
        
        if name:
            metrics = [m for m in metrics if m.name == name]
        
        return metrics

    def generate_prometheus_metrics(self) -> str:
        """Génère les métriques Prometheus"""
        return generate_latest(self.registry)

# Instance globale du monitoring
monitoring = AdvancedMonitoring()