"""
Monitoring and metrics configuration
"""

import time
import threading
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import structlog
import psutil

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Number of active HTTP requests'
)

# Business metrics
TRANSFER_COUNT = Counter(
    'transfers_total',
    'Total number of transfers',
    ['type', 'status']
)

TRANSFER_AMOUNT = Counter(
    'transfers_amount_total',
    'Total amount of transfers',
    ['currency']
)

ACCOUNT_COUNT = Gauge(
    'accounts_total',
    'Total number of accounts'
)

USER_COUNT = Gauge(
    'users_total',
    'Total number of users'
)

# System metrics
CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'system_memory_usage_percent',
    'Memory usage percentage'
)

DISK_USAGE = Gauge(
    'system_disk_usage_percent',
    'Disk usage percentage'
)

# ISO 20022 metrics
ISO20022_MESSAGES = Counter(
    'iso20022_messages_total',
    'Total ISO 20022 messages processed',
    ['type', 'status']
)

class MonitoringMiddleware:
    """Middleware for monitoring HTTP requests"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        method = scope["method"]
        path = scope["path"]
        
        # Increment active requests
        ACTIVE_REQUESTS.inc()
        
        start_time = time.time()
        
        # Create a custom send function to capture response
        async def custom_send(message):
            if message["type"] == "http.response.start":
                status = message["status"]
                REQUEST_COUNT.labels(method=method, endpoint=path, status=status).inc()
            
            await send(message)
        
        try:
            await self.app(scope, receive, custom_send)
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.dec()
            
            # Record request duration
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)

def setup_monitoring():
    """Setup monitoring and start background tasks"""
    logger.info("Setting up monitoring...")
    
    # Start system metrics collection
    def collect_system_metrics():
        """Collect system metrics in background"""
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                CPU_USAGE.set(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                MEMORY_USAGE.set(memory.percent)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                DISK_USAGE.set((disk.used / disk.total) * 100)
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                time.sleep(60)  # Wait longer on error
    
    # Start background thread
    metrics_thread = threading.Thread(target=collect_system_metrics, daemon=True)
    metrics_thread.start()
    
    logger.info("Monitoring setup completed")

def get_metrics():
    """Get Prometheus metrics"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Utility functions for recording business metrics
def record_transfer(transfer_type: str, status: str, amount: float = None, currency: str = None):
    """Record transfer metrics"""
    TRANSFER_COUNT.labels(type=transfer_type, status=status).inc()
    if amount and currency:
        TRANSFER_AMOUNT.labels(currency=currency).inc(amount)

def record_iso20022_message(message_type: str, status: str):
    """Record ISO 20022 message metrics"""
    ISO20022_MESSAGES.labels(type=message_type, status=status).inc()

def update_account_count(count: int):
    """Update account count metric"""
    ACCOUNT_COUNT.set(count)

def update_user_count(count: int):
    """Update user count metric"""
    USER_COUNT.set(count)