"""
Système de monitoring avec Prometheus et métriques personnalisées
"""
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import time
import structlog

logger = structlog.get_logger()

# Métriques Prometheus
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

REQUEST_SIZE = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'http_active_connections',
    'Number of active HTTP connections'
)

# Métriques métier
TRANSFER_COUNT = Counter(
    'banking_transfers_total',
    'Total number of transfers',
    ['type', 'status', 'currency']
)

TRANSFER_AMOUNT = Histogram(
    'banking_transfer_amount',
    'Transfer amounts',
    ['type', 'currency']
)

ACCOUNT_COUNT = Gauge(
    'banking_accounts_total',
    'Total number of accounts',
    ['status', 'type']
)

USER_COUNT = Gauge(
    'banking_users_total',
    'Total number of users',
    ['status']
)

KYC_CHECK_COUNT = Counter(
    'kyc_checks_total',
    'Total number of KYC checks',
    ['type', 'status']
)

AUTH_FAILURE_COUNT = Counter(
    'auth_failures_total',
    'Total number of authentication failures',
    ['reason']
)

# Métriques système
DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

REDIS_CONNECTIONS = Gauge(
    'redis_connections_active',
    'Number of active Redis connections'
)

SWIFT_MESSAGE_COUNT = Counter(
    'swift_messages_total',
    'Total number of SWIFT messages',
    ['type', 'status']
)

MOJALOOP_TRANSFER_COUNT = Counter(
    'mojaloop_transfers_total',
    'Total number of Mojaloop transfers',
    ['status']
)


class MonitoringMiddleware:
    """Middleware pour collecter les métriques"""
    
    def __init__(self):
        self.start_time = time.time()
    
    async def __call__(self, request: Request, call_next):
        # Incrémenter les connexions actives
        ACTIVE_CONNECTIONS.inc()
        
        # Mesurer la taille de la requête
        content_length = request.headers.get('content-length')
        if content_length:
            REQUEST_SIZE.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(float(content_length))
        
        # Mesurer le temps de traitement
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Mesurer la durée
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            # Mesurer la taille de la réponse
            response_size = len(response.body) if hasattr(response, 'body') else 0
            RESPONSE_SIZE.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(response_size)
            
            # Incrémenter le compteur de requêtes
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            return response
            
        except Exception as e:
            # En cas d'erreur, incrémenter quand même le compteur
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
            raise
        finally:
            # Décrémenter les connexions actives
            ACTIVE_CONNECTIONS.dec()


def setup_monitoring():
    """Configuration du monitoring"""
    logger.info("Setting up monitoring system")
    
    # Initialiser les métriques de base
    _initialize_base_metrics()
    
    # Configurer les métriques personnalisées
    _setup_custom_metrics()
    
    logger.info("Monitoring system setup completed")


def _initialize_base_metrics():
    """Initialiser les métriques de base"""
    # Métriques système
    DATABASE_CONNECTIONS.set(0)
    REDIS_CONNECTIONS.set(0)
    
    # Métriques métier
    ACCOUNT_COUNT.labels(status='active', type='current').set(0)
    ACCOUNT_COUNT.labels(status='active', type='savings').set(0)
    ACCOUNT_COUNT.labels(status='suspended', type='current').set(0)
    ACCOUNT_COUNT.labels(status='suspended', type='savings').set(0)
    
    USER_COUNT.labels(status='active').set(0)
    USER_COUNT.labels(status='inactive').set(0)
    USER_COUNT.labels(status='suspended').set(0)


def _setup_custom_metrics():
    """Configurer les métriques personnalisées"""
    # Métriques de performance
    TRANSFER_PROCESSING_TIME = Histogram(
        'transfer_processing_time_seconds',
        'Time to process a transfer',
        ['type', 'priority']
    )
    
    # Métriques de sécurité
    SECURITY_EVENTS = Counter(
        'security_events_total',
        'Total number of security events',
        ['type', 'severity']
    )
    
    # Métriques de conformité
    COMPLIANCE_CHECKS = Counter(
        'compliance_checks_total',
        'Total number of compliance checks',
        ['type', 'result']
    )


def record_transfer(transfer_type: str, status: str, currency: str, amount: float):
    """Enregistrer une métrique de transfert"""
    TRANSFER_COUNT.labels(
        type=transfer_type,
        status=status,
        currency=currency
    ).inc()
    
    TRANSFER_AMOUNT.labels(
        type=transfer_type,
        currency=currency
    ).observe(amount)


def record_kyc_check(check_type: str, status: str):
    """Enregistrer une métrique de vérification KYC"""
    KYC_CHECK_COUNT.labels(
        type=check_type,
        status=status
    ).inc()


def record_auth_failure(reason: str):
    """Enregistrer un échec d'authentification"""
    AUTH_FAILURE_COUNT.labels(reason=reason).inc()


def record_swift_message(message_type: str, status: str):
    """Enregistrer une métrique de message SWIFT"""
    SWIFT_MESSAGE_COUNT.labels(
        type=message_type,
        status=status
    ).inc()


def record_mojaloop_transfer(status: str):
    """Enregistrer une métrique de transfert Mojaloop"""
    MOJALOOP_TRANSFER_COUNT.labels(status=status).inc()


def update_account_count(status: str, account_type: str, count: int):
    """Mettre à jour le nombre de comptes"""
    ACCOUNT_COUNT.labels(
        status=status,
        type=account_type
    ).set(count)


def update_user_count(status: str, count: int):
    """Mettre à jour le nombre d'utilisateurs"""
    USER_COUNT.labels(status=status).set(count)


def update_database_connections(count: int):
    """Mettre à jour le nombre de connexions à la base de données"""
    DATABASE_CONNECTIONS.set(count)


def update_redis_connections(count: int):
    """Mettre à jour le nombre de connexions Redis"""
    REDIS_CONNECTIONS.set(count)


async def metrics_endpoint():
    """Endpoint pour les métriques Prometheus"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


class MetricsCollector:
    """Collecteur de métriques personnalisées"""
    
    @staticmethod
    def collect_system_metrics():
        """Collecter les métriques système"""
        import psutil
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Créer des métriques système si elles n'existent pas
        if not hasattr(MetricsCollector, 'cpu_usage'):
            MetricsCollector.cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
            MetricsCollector.memory_usage = Gauge('system_memory_usage_percent', 'Memory usage percentage')
            MetricsCollector.disk_usage = Gauge('system_disk_usage_percent', 'Disk usage percentage')
        
        MetricsCollector.cpu_usage.set(cpu_percent)
        MetricsCollector.memory_usage.set(memory.percent)
        MetricsCollector.disk_usage.set(disk.percent)
    
    @staticmethod
    def collect_business_metrics():
        """Collecter les métriques métier"""
        # Cette méthode sera appelée périodiquement pour mettre à jour
        # les métriques métier depuis la base de données
        pass


def start_metrics_collection():
    """Démarrer la collecte périodique de métriques"""
    import asyncio
    import threading
    
    def collect_metrics():
        while True:
            try:
                MetricsCollector.collect_system_metrics()
                MetricsCollector.collect_business_metrics()
                time.sleep(60)  # Collecter toutes les minutes
            except Exception as e:
                logger.error("Error collecting metrics", error=str(e))
                time.sleep(60)
    
    # Démarrer la collecte dans un thread séparé
    metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
    metrics_thread.start()
    
    logger.info("Metrics collection started")