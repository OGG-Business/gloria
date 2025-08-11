"""
Monitoring configuration with Prometheus metrics
"""

import time
import threading
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import structlog

logger = structlog.get_logger()

# HTTP request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Business metrics
transfers_total = Counter(
    'transfers_total',
    'Total number of transfers',
    ['status', 'currency', 'type']
)

transfers_amount_total = Counter(
    'transfers_amount_total',
    'Total amount of transfers',
    ['currency', 'type']
)

accounts_total = Gauge(
    'accounts_total',
    'Total number of accounts',
    ['status', 'currency']
)

users_total = Gauge(
    'users_total',
    'Total number of users',
    ['status', 'role']
)

kyc_checks_total = Counter(
    'kyc_checks_total',
    'Total number of KYC checks',
    ['status', 'type']
)

# System metrics
system_memory_usage = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

# Connector metrics
swift_messages_total = Counter(
    'swift_messages_total',
    'Total number of SWIFT messages',
    ['type', 'status']
)

mojaloop_transfers_total = Counter(
    'mojaloop_transfers_total',
    'Total number of Mojaloop transfers',
    ['status']
)

iso20022_messages_total = Counter(
    'iso20022_messages_total',
    'Total number of ISO 20022 messages',
    ['type', 'status']
)

class MonitoringMiddleware:
    """Middleware for collecting HTTP metrics"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        # Create a custom send function to capture response
        async def custom_send(message):
            if message["type"] == "http.response.start":
                # Record metrics
                duration = time.time() - start_time
                method = scope["method"]
                path = scope["path"]
                status = message["status"]
                
                http_requests_total.labels(method=method, endpoint=path, status=status).inc()
                http_request_duration_seconds.labels(method=method, endpoint=path).observe(duration)
            
            await send(message)
        
        await self.app(scope, receive, custom_send)

def setup_monitoring():
    """Setup monitoring and metrics collection"""
    logger.info("Setting up monitoring...")
    
    # Start metrics collection in background thread
    metrics_thread = threading.Thread(target=start_metrics_collection, daemon=True)
    metrics_thread.start()
    
    logger.info("Monitoring setup completed")

def start_metrics_collection():
    """Start collecting system metrics"""
    import psutil
    
    while True:
        try:
            # Collect system metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            system_memory_usage.set(memory.used)
            system_cpu_usage.set(cpu_percent)
            
            time.sleep(30)  # Collect every 30 seconds
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            time.sleep(60)  # Wait longer on error

def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Helper functions for recording business metrics
def record_transfer(status: str, currency: str, amount: float, transfer_type: str):
    """Record transfer metrics"""
    transfers_total.labels(status=status, currency=currency, type=transfer_type).inc()
    transfers_amount_total.labels(currency=currency, type=transfer_type).inc(amount)

def record_kyc_check(status: str, check_type: str):
    """Record KYC check metrics"""
    kyc_checks_total.labels(status=status, type=check_type).inc()

def record_swift_message(message_type: str, status: str):
    """Record SWIFT message metrics"""
    swift_messages_total.labels(type=message_type, status=status).inc()

def record_mojaloop_transfer(status: str):
    """Record Mojaloop transfer metrics"""
    mojaloop_transfers_total.labels(status=status).inc()

def record_iso20022_message(message_type: str, status: str):
    """Record ISO 20022 message metrics"""
    iso20022_messages_total.labels(type=message_type, status=status).inc()

class MetricsCollector:
    """Collector for business metrics"""
    
    @staticmethod
    def collect_system_metrics() -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            import psutil
            
            return {
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "used": psutil.virtual_memory().used,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count()
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            }
        except ImportError:
            logger.warning("psutil not available, skipping system metrics")
            return {}
    
    @staticmethod
    def collect_business_metrics() -> Dict[str, Any]:
        """Collect business metrics"""
        # This would typically query the database
        return {
            "transfers": {
                "total": 0,
                "pending": 0,
                "completed": 0,
                "failed": 0
            },
            "accounts": {
                "total": 0,
                "active": 0,
                "suspended": 0
            },
            "users": {
                "total": 0,
                "active": 0,
                "inactive": 0
            }
        }