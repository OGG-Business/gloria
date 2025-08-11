# SwiftPay Infrastructure as Code
# Terraform configuration for deploying SwiftPay to cloud environments

terraform {
  required_version = ">= 1.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

# Variables
variable "cloud_provider" {
  description = "Cloud provider (aws, gcp, azure)"
  type        = string
  default     = "aws"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "domain_name" {
  description = "Domain name for SwiftPay"
  type        = string
  default     = "swiftpay.example.com"
}

variable "kubernetes_cluster_name" {
  description = "Name of the Kubernetes cluster"
  type        = string
}

variable "database_instance_class" {
  description = "Database instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

# Data sources
data "kubernetes_namespace" "swiftpay" {
  metadata {
    name = "swiftpay"
  }
  depends_on = [kubernetes_namespace.swiftpay]
}

# Local values
locals {
  common_tags = {
    Project     = "SwiftPay"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  
  namespace = "swiftpay"
}

# Kubernetes namespace
resource "kubernetes_namespace" "swiftpay" {
  metadata {
    name = local.namespace
    labels = {
      name        = local.namespace
      environment = var.environment
      app         = "swiftpay"
    }
  }
}

# Generate random passwords
resource "random_password" "database_password" {
  length  = 32
  special = true
}

resource "random_password" "redis_password" {
  length  = 32
  special = true
}

resource "random_password" "encryption_key" {
  length  = 32
  special = false
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# Kubernetes secrets
resource "kubernetes_secret" "swiftpay_secrets" {
  metadata {
    name      = "swiftpay-secrets"
    namespace = kubernetes_namespace.swiftpay.metadata[0].name
  }

  data = {
    # Database
    SPRING_DATASOURCE_PASSWORD = random_password.database_password.result
    
    # Redis
    SPRING_DATA_REDIS_PASSWORD = random_password.redis_password.result
    
    # Encryption
    SWIFTPAY_SECURITY_ENCRYPTION_KEY = base64encode(random_password.encryption_key.result)
    
    # JWT
    SWIFTPAY_SECURITY_JWT_SECRET = random_password.jwt_secret.result
    
    # Vault (placeholder - should be set externally)
    VAULT_TOKEN = "REPLACE_WITH_ACTUAL_VAULT_TOKEN"
    
    # SWIFT (placeholders - should be set externally)
    SWIFTPAY_SWIFT_USERNAME = "REPLACE_WITH_SWIFT_USERNAME"
    SWIFTPAY_SWIFT_PASSWORD = "REPLACE_WITH_SWIFT_PASSWORD"
    SWIFTPAY_SWIFT_CLIENT_CERT_PASSWORD = "REPLACE_WITH_CERT_PASSWORD"
    
    # Mojaloop (placeholder - should be set externally)
    SWIFTPAY_MOJALOOP_API_KEY = "REPLACE_WITH_MOJALOOP_API_KEY"
    
    # KYC/AML (placeholders - should be set externally)
    SWIFTPAY_KYC_API_KEY = "REPLACE_WITH_KYC_API_KEY"
    SWIFTPAY_SANCTIONS_API_KEY = "REPLACE_WITH_SANCTIONS_API_KEY"
    
    # Notifications (placeholders - should be set externally)
    SWIFTPAY_NOTIFICATIONS_EMAIL_PASSWORD = "REPLACE_WITH_EMAIL_PASSWORD"
    SWIFTPAY_NOTIFICATIONS_SMS_API_KEY = "REPLACE_WITH_SMS_API_KEY"
  }

  type = "Opaque"
}

# TLS certificates (self-signed for demo)
resource "tls_private_key" "swiftpay_tls" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "tls_self_signed_cert" "swiftpay_tls" {
  private_key_pem = tls_private_key.swiftpay_tls.private_key_pem

  subject {
    common_name  = var.domain_name
    organization = "SwiftPay"
    country      = "CD"
    province     = "Kinshasa"
    locality     = "Kinshasa"
  }

  dns_names = [
    var.domain_name,
    "api.${var.domain_name}",
    "auth.${var.domain_name}"
  ]

  validity_period_hours = 8760 # 1 year

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

resource "kubernetes_secret" "swiftpay_tls" {
  metadata {
    name      = "swiftpay-tls"
    namespace = kubernetes_namespace.swiftpay.metadata[0].name
  }

  data = {
    "tls.crt" = tls_self_signed_cert.swiftpay_tls.cert_pem
    "tls.key" = tls_private_key.swiftpay_tls.private_key_pem
  }

  type = "kubernetes.io/tls"
}

# Helm releases
resource "helm_release" "postgresql" {
  name       = "postgresql"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "postgresql"
  version    = "12.12.10"
  namespace  = kubernetes_namespace.swiftpay.metadata[0].name

  set_sensitive {
    name  = "auth.postgresPassword"
    value = random_password.database_password.result
  }

  set {
    name  = "auth.database"
    value = "swiftpay"
  }

  set {
    name  = "primary.persistence.size"
    value = "50Gi"
  }

  set {
    name  = "primary.resources.requests.memory"
    value = "2Gi"
  }

  set {
    name  = "primary.resources.requests.cpu"
    value = "1000m"
  }

  set {
    name  = "metrics.enabled"
    value = "true"
  }

  set {
    name  = "metrics.serviceMonitor.enabled"
    value = "true"
  }
}

resource "helm_release" "redis" {
  name       = "redis"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "redis"
  version    = "18.4.0"
  namespace  = kubernetes_namespace.swiftpay.metadata[0].name

  set_sensitive {
    name  = "auth.password"
    value = random_password.redis_password.result
  }

  set {
    name  = "master.persistence.size"
    value = "10Gi"
  }

  set {
    name  = "replica.replicaCount"
    value = "1"
  }

  set {
    name  = "metrics.enabled"
    value = "true"
  }

  set {
    name  = "metrics.serviceMonitor.enabled"
    value = "true"
  }
}

# Monitoring namespace
resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
    labels = {
      name = "monitoring"
    }
  }
}

# Prometheus & Grafana
resource "helm_release" "kube_prometheus_stack" {
  name       = "kube-prometheus-stack"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  version    = "54.2.2"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name

  set {
    name  = "prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  set {
    name  = "grafana.persistence.enabled"
    value = "true"
  }

  set {
    name  = "grafana.persistence.size"
    value = "10Gi"
  }

  set {
    name  = "prometheus.prometheusSpec.retention"
    value = "30d"
  }

  set {
    name  = "prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage"
    value = "50Gi"
  }
}

# Logging namespace
resource "kubernetes_namespace" "logging" {
  metadata {
    name = "logging"
    labels = {
      name = "logging"
    }
  }
}

# ELK Stack
resource "helm_release" "elasticsearch" {
  name       = "elasticsearch"
  repository = "https://helm.elastic.co"
  chart      = "elasticsearch"
  version    = "8.5.1"
  namespace  = kubernetes_namespace.logging.metadata[0].name

  set {
    name  = "replicas"
    value = "3"
  }

  set {
    name  = "volumeClaimTemplate.resources.requests.storage"
    value = "30Gi"
  }

  set {
    name  = "esJavaOpts"
    value = "-Xmx2g -Xms2g"
  }
}

resource "helm_release" "kibana" {
  name       = "kibana"
  repository = "https://helm.elastic.co"
  chart      = "kibana"
  version    = "8.5.1"
  namespace  = kubernetes_namespace.logging.metadata[0].name

  set {
    name  = "service.type"
    value = "ClusterIP"
  }

  depends_on = [helm_release.elasticsearch]
}

# SwiftPay application
resource "helm_release" "swiftpay" {
  name      = "swiftpay"
  chart     = "./helm/swiftpay"
  namespace = kubernetes_namespace.swiftpay.metadata[0].name

  set {
    name  = "backend.image.tag"
    value = "latest"
  }

  set {
    name  = "frontend.image.tag"
    value = "latest"
  }

  set {
    name  = "ingress.hosts[0].host"
    value = var.domain_name
  }

  set {
    name  = "frontend.config.apiBaseUrl"
    value = "https://api.${var.domain_name}"
  }

  depends_on = [
    helm_release.postgresql,
    helm_release.redis,
    kubernetes_secret.swiftpay_secrets,
    kubernetes_secret.swiftpay_tls
  ]
}

# Outputs
output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace.swiftpay.metadata[0].name
}

output "frontend_url" {
  description = "Frontend URL"
  value       = "https://${var.domain_name}"
}

output "backend_url" {
  description = "Backend API URL"
  value       = "https://api.${var.domain_name}"
}

output "grafana_admin_password" {
  description = "Grafana admin password"
  value       = random_password.database_password.result
  sensitive   = true
}

output "database_password" {
  description = "Database password"
  value       = random_password.database_password.result
  sensitive   = true
}

output "redis_password" {
  description = "Redis password"
  value       = random_password.redis_password.result
  sensitive   = true
}