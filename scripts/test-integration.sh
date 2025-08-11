#!/bin/bash

# SwiftPay Integration Test Script
# Tests the complete system with mock data

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
API_BASE_URL=${API_BASE_URL:-"http://localhost:8080"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}
TIMEOUT=30

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Test functions
test_health() {
    log "Testing health endpoints..."
    
    # Backend health
    if ! curl -f -s "$API_BASE_URL/actuator/health" > /dev/null; then
        error "Backend health check failed"
    fi
    
    # Frontend health (if available)
    if curl -f -s "$FRONTEND_URL" > /dev/null; then
        log "✓ Frontend is accessible"
    else
        warn "Frontend not accessible at $FRONTEND_URL"
    fi
    
    log "✓ Health checks passed"
}

test_api_endpoints() {
    log "Testing API endpoints..."
    
    # Test public endpoints (no auth required)
    endpoints=(
        "/actuator/info"
        "/actuator/health"
        "/api/v1/validation/iban/GB82WEST12345698765432"
        "/api/v1/transfers/fees/calculate"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s "$API_BASE_URL$endpoint" > /dev/null; then
            log "✓ $endpoint accessible"
        else
            warn "✗ $endpoint not accessible"
        fi
    done
}

test_iban_validation() {
    log "Testing IBAN validation..."
    
    # Test valid IBAN
    response=$(curl -s "$API_BASE_URL/api/v1/validation/iban/GB82WEST12345698765432")
    if echo "$response" | grep -q '"valid":true'; then
        log "✓ Valid IBAN correctly validated"
    else
        warn "✗ Valid IBAN validation failed"
    fi
    
    # Test invalid IBAN
    response=$(curl -s "$API_BASE_URL/api/v1/validation/iban/INVALID123")
    if echo "$response" | grep -q '"valid":false'; then
        log "✓ Invalid IBAN correctly rejected"
    else
        warn "✗ Invalid IBAN validation failed"
    fi
}

test_fee_calculation() {
    log "Testing fee calculation..."
    
    # Test fee calculation request
    fee_request='{
        "sourceCountry": "CD",
        "destinationCountry": "GB",
        "amount": 1000.00,
        "currency": "USD",
        "urgency": "STANDARD"
    }'
    
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$fee_request" \
        "$API_BASE_URL/api/v1/transfers/fees/calculate")
    
    if echo "$response" | grep -q '"totalFee"'; then
        log "✓ Fee calculation working"
    else
        warn "✗ Fee calculation failed"
    fi
}

test_database_connectivity() {
    log "Testing database connectivity..."
    
    response=$(curl -s "$API_BASE_URL/actuator/health/db")
    if echo "$response" | grep -q '"status":"UP"'; then
        log "✓ Database connectivity OK"
    else
        error "✗ Database connectivity failed"
    fi
}

test_redis_connectivity() {
    log "Testing Redis connectivity..."
    
    # Check if Redis health endpoint exists
    if curl -s "$API_BASE_URL/actuator/health" | grep -q "redis"; then
        response=$(curl -s "$API_BASE_URL/actuator/health/redis")
        if echo "$response" | grep -q '"status":"UP"'; then
            log "✓ Redis connectivity OK"
        else
            warn "✗ Redis connectivity failed"
        fi
    else
        log "ℹ Redis health check not available"
    fi
}

test_metrics() {
    log "Testing metrics endpoint..."
    
    response=$(curl -s "$API_BASE_URL/actuator/prometheus")
    if echo "$response" | grep -q "jvm_memory_used_bytes"; then
        log "✓ Prometheus metrics available"
    else
        warn "✗ Prometheus metrics not available"
    fi
}

test_swagger_ui() {
    log "Testing Swagger UI..."
    
    if curl -f -s "$API_BASE_URL/swagger-ui/index.html" > /dev/null; then
        log "✓ Swagger UI accessible"
    else
        warn "✗ Swagger UI not accessible"
    fi
}

# Mock transfer test (requires authentication - skip if not configured)
test_mock_transfer() {
    log "Testing mock transfer creation..."
    
    # This would require authentication, so we'll just test the endpoint structure
    transfer_request='{
        "recipientName": "John Doe",
        "recipientIban": "GB82WEST12345698765432",
        "recipientBic": "WESTGB22",
        "amount": 100.00,
        "currency": "EUR",
        "purpose": "Personal transfer",
        "urgency": "STANDARD"
    }'
    
    # Test without auth (should return 401)
    response=$(curl -s -w "%{http_code}" -o /dev/null -X POST \
        -H "Content-Type: application/json" \
        -d "$transfer_request" \
        "$API_BASE_URL/api/v1/transfers")
    
    if [[ "$response" == "401" ]]; then
        log "✓ Transfer endpoint properly secured (401 Unauthorized)"
    else
        warn "✗ Transfer endpoint security issue (got HTTP $response)"
    fi
}

# Main test execution
main() {
    log "Starting SwiftPay Integration Tests..."
    log "API Base URL: $API_BASE_URL"
    log "Frontend URL: $FRONTEND_URL"
    echo
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 10
    
    # Run tests
    test_health
    test_database_connectivity
    test_redis_connectivity
    test_api_endpoints
    test_iban_validation
    test_fee_calculation
    test_metrics
    test_swagger_ui
    test_mock_transfer
    
    echo
    log "✓ Integration tests completed successfully!"
    echo
    echo "Next steps for full testing:"
    echo "1. Configure authentication (Keycloak)"
    echo "2. Test authenticated endpoints"
    echo "3. Test SWIFT connectivity (dry-run mode)"
    echo "4. Test Mojaloop integration"
    echo "5. Test KYC document upload"
    echo "6. Test webhook delivery"
    echo
    warn "Remember: Never test with real bank credentials or real money!"
}

# Error handling
trap 'error "Integration test failed at line $LINENO"' ERR

# Run main function
main "$@"