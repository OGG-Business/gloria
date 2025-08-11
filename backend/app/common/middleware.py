"""
Middlewares personnalisés pour l'audit et la sécurité
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import uuid
import structlog
from typing import Optional
import json

from app.config import get_settings
from app.audit.models import AuditLog, AuditEventType, AuditSeverity
from app.common.database import get_db_context

logger = structlog.get_logger()
settings = get_settings()


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware pour l'audit des requêtes"""
    
    async def dispatch(self, request: Request, call_next):
        # Générer un ID de trace unique
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        
        # Ajouter le trace_id au contexte de logging
        logger = logger.bind(trace_id=trace_id)
        
        # Informations de base de la requête
        start_time = time.time()
        path = request.url.path
        method = request.method
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        # Log de début de requête
        logger.info(
            "Request started",
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        try:
            # Traiter la requête
            response = await call_next(request)
            
            # Calculer le temps de traitement
            process_time = time.time() - start_time
            
            # Log de fin de requête
            logger.info(
                "Request completed",
                method=method,
                path=path,
                status_code=response.status_code,
                process_time=process_time
            )
            
            # Ajouter le temps de traitement aux headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Trace-ID"] = trace_id
            
            # Audit des actions sensibles
            await self._audit_sensitive_actions(request, response, trace_id)
            
            return response
            
        except Exception as e:
            # Log d'erreur
            logger.error(
                "Request failed",
                method=method,
                path=path,
                error=str(e),
                process_time=time.time() - start_time
            )
            raise
    
    async def _audit_sensitive_actions(self, request: Request, response: Response, trace_id: str):
        """Audit des actions sensibles"""
        path = request.url.path
        method = request.method
        
        # Définir les actions sensibles à auditer
        sensitive_patterns = [
            ("/auth/login", "POST"),
            ("/auth/logout", "POST"),
            ("/transfers", "POST"),
            ("/accounts", "POST"),
            ("/kyc", "POST"),
            ("/admin", "POST"),
            ("/admin", "PUT"),
            ("/admin", "DELETE"),
        ]
        
        # Vérifier si c'est une action sensible
        is_sensitive = any(
            path.startswith(pattern[0]) and method == pattern[1]
            for pattern in sensitive_patterns
        )
        
        if is_sensitive and response.status_code < 400:
            try:
                # Extraire les informations utilisateur si disponible
                user_id = None
                if hasattr(request.state, "user"):
                    user_id = request.state.user.id
                
                # Créer l'événement d'audit
                event_type = self._get_event_type(path, method)
                
                audit_log = AuditLog(
                    event_type=event_type,
                    severity=AuditSeverity.INFO,
                    user_id=user_id,
                    resource_type=self._get_resource_type(path),
                    resource_id=self._extract_resource_id(path),
                    action=method.lower(),
                    description=f"{method} {path}",
                    details={
                        "path": path,
                        "method": method,
                        "status_code": response.status_code,
                        "client_ip": request.client.host if request.client else "unknown",
                        "user_agent": request.headers.get("user-agent", ""),
                        "trace_id": trace_id
                    },
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    trace_id=trace_id
                )
                
                # Sauvegarder en base (async)
                # Note: En production, utiliser une queue pour éviter le blocage
                with get_db_context() as db:
                    db.add(audit_log)
                    db.commit()
                    
            except Exception as e:
                logger.error("Failed to create audit log", error=str(e))
    
    def _get_event_type(self, path: str, method: str) -> AuditEventType:
        """Déterminer le type d'événement d'audit"""
        if path.startswith("/auth/login") and method == "POST":
            return AuditEventType.LOGIN
        elif path.startswith("/auth/logout") and method == "POST":
            return AuditEventType.LOGOUT
        elif path.startswith("/transfers") and method == "POST":
            return AuditEventType.TRANSFER_INITIATED
        elif path.startswith("/accounts") and method == "POST":
            return AuditEventType.ACCOUNT_CREATED
        elif path.startswith("/kyc") and method == "POST":
            return AuditEventType.KYC_DOCUMENT_UPLOADED
        elif path.startswith("/admin") and method in ["POST", "PUT", "DELETE"]:
            return AuditEventType.SYSTEM_CONFIG_CHANGED
        else:
            return AuditEventType.SYSTEM_CONFIG_CHANGED
    
    def _get_resource_type(self, path: str) -> Optional[str]:
        """Extraire le type de ressource de l'URL"""
        if path.startswith("/transfers"):
            return "transfer"
        elif path.startswith("/accounts"):
            return "account"
        elif path.startswith("/kyc"):
            return "kyc"
        elif path.startswith("/admin"):
            return "admin"
        elif path.startswith("/auth"):
            return "auth"
        return None
    
    def _extract_resource_id(self, path: str) -> Optional[str]:
        """Extraire l'ID de ressource de l'URL"""
        parts = path.split("/")
        if len(parts) > 2 and parts[-1].isdigit():
            return parts[-1]
        return None


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de sécurité"""
    
    async def dispatch(self, request: Request, call_next):
        # Vérifications de sécurité
        security_checks = await self._perform_security_checks(request)
        
        if not security_checks["passed"]:
            logger.warning(
                "Security check failed",
                client_ip=request.client.host if request.client else "unknown",
                reason=security_checks["reason"]
            )
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Security violation",
                    "message": security_checks["reason"]
                }
            )
        
        # Ajouter des headers de sécurité
        response = await call_next(request)
        
        # Headers de sécurité
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
    
    async def _perform_security_checks(self, request: Request) -> dict:
        """Effectuer les vérifications de sécurité"""
        client_ip = request.client.host if request.client else "unknown"
        
        # Vérifier les headers suspects
        suspicious_headers = [
            "x-forwarded-for",
            "x-real-ip",
            "x-forwarded-proto"
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                # En production, vérifier la validité des headers
                pass
        
        # Vérifier le User-Agent
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            return {
                "passed": False,
                "reason": "Invalid or missing User-Agent"
            }
        
        # Vérifier les méthodes HTTP autorisées
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        if request.method not in allowed_methods:
            return {
                "passed": False,
                "reason": f"Method {request.method} not allowed"
            }
        
        # Vérifier la taille du contenu
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            return {
                "passed": False,
                "reason": "Request too large"
            }
        
        return {"passed": True, "reason": None}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de limitation de débit"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Nettoyer les anciennes entrées
        self._cleanup_old_entries(current_time)
        
        # Vérifier la limite
        if not self._check_rate_limit(client_ip, current_time):
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                limit=self.requests_per_minute
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_minute} per minute"
                }
            )
        
        return await call_next(request)
    
    def _check_rate_limit(self, client_ip: str, current_time: float) -> bool:
        """Vérifier la limite de débit"""
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # Ajouter la requête actuelle
        self.request_counts[client_ip].append(current_time)
        
        # Compter les requêtes dans la dernière minute
        one_minute_ago = current_time - 60
        recent_requests = [
            req_time for req_time in self.request_counts[client_ip]
            if req_time > one_minute_ago
        ]
        
        return len(recent_requests) <= self.requests_per_minute
    
    def _cleanup_old_entries(self, current_time: float):
        """Nettoyer les anciennes entrées"""
        one_minute_ago = current_time - 60
        
        for client_ip in list(self.request_counts.keys()):
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if req_time > one_minute_ago
            ]
            
            # Supprimer les entrées vides
            if not self.request_counts[client_ip]:
                del self.request_counts[client_ip]