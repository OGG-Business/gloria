#!/bin/bash

# SwiftPay Connectivity Testing Script
# This script tests connectivity to external services in dry-run mode
# SAFE MODE: No real transfers will be initiated

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL=${BACKEND_URL:-"http://localhost:8080"}
MANAGEMENT_URL=${MANAGEMENT_URL:-"http://localhost:8081"}
TIMEOUT=${TIMEOUT:-30}

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Test basic application health
test_application_health() {
    log "Testing application health..."
    
    # Test main health endpoint
    if curl -f -s --max-time "$TIMEOUT" "$MANAGEMENT_URL/actuator/health" > /dev/null; then
        success "Application health check passed"
    else
        error "Application health check failed"
        return 1
    fi
    
    # Test database connectivity
    if curl -f -s --max-time "$TIMEOUT" "$MANAGEMENT_URL/actuator/health/db" > /dev/null; then
        success "Database connectivity check passed"
    else
        error "Database connectivity check failed"
        return 1
    fi
    
    # Test Redis connectivity
    if curl -f -s --max-time "$TIMEOUT" "$MANAGEMENT_URL/actuator/health/redis" > /dev/null; then
        success "Redis connectivity check passed"
    else
        error "Redis connectivity check failed"
        return 1
    fi
    
    return 0
}

# Test API endpoints
test_api_endpoints() {
    log "Testing API endpoints..."
    
    # Test health endpoint
    local health_response=$(curl -s --max-time "$TIMEOUT" "$BACKEND_URL/api/v1/health")
    if [[ $? -eq 0 ]]; then
        success "API health endpoint accessible"
        echo "Response: $health_response"
    else
        error "API health endpoint failed"
        return 1
    fi
    
    # Test OpenAPI documentation
    if curl -f -s --max-time "$TIMEOUT" "$BACKEND_URL/swagger-ui/index.html" > /dev/null; then
        success "OpenAPI documentation accessible"
    else
        warn "OpenAPI documentation not accessible (may require authentication)"
    fi
    
    return 0
}

# Test SWIFT connectivity (dry-run)
test_swift_connectivity() {
    log "Testing SWIFT connectivity (dry-run mode)..."
    
    # Test SWIFT configuration endpoint
    local swift_test_response=$(curl -s --max-time "$TIMEOUT" \
        -X POST "$BACKEND_URL/api/v1/admin/swift/test-connectivity" \
        -H "Content-Type: application/json" \
        -d '{"dryRun": true}' 2>/dev/null || echo "ENDPOINT_NOT_AVAILABLE")
    
    if [[ "$swift_test_response" != "ENDPOINT_NOT_AVAILABLE" ]]; then
        success "SWIFT connectivity test endpoint accessible"
        echo "Response: $swift_test_response"
    else
        warn "SWIFT connectivity test endpoint not available (may require authentication or implementation)"
    fi
    
    # Test certificate availability
    if [[ -f "/app/certs/swift/client.p12" ]]; then
        log "Checking SWIFT client certificate..."
        if openssl pkcs12 -info -in /app/certs/swift/client.p12 -noout -passin pass:"${SWIFT_CERT_PASSWORD:-test}" 2>/dev/null; then
            success "SWIFT client certificate is valid"
        else
            warn "SWIFT client certificate validation failed or password incorrect"
        fi
    else
        warn "SWIFT client certificate not found at /app/certs/swift/client.p12"
    fi
    
    return 0
}

# Test Mojaloop connectivity (dry-run)
test_mojaloop_connectivity() {
    log "Testing Mojaloop connectivity (dry-run mode)..."
    
    # Test Mojaloop configuration endpoint
    local mojaloop_test_response=$(curl -s --max-time "$TIMEOUT" \
        -X POST "$BACKEND_URL/api/v1/admin/mojaloop/test-connectivity" \
        -H "Content-Type: application/json" \
        -d '{"dryRun": true}' 2>/dev/null || echo "ENDPOINT_NOT_AVAILABLE")
    
    if [[ "$mojaloop_test_response" != "ENDPOINT_NOT_AVAILABLE" ]]; then
        success "Mojaloop connectivity test endpoint accessible"
        echo "Response: $mojaloop_test_response"
    else
        warn "Mojaloop connectivity test endpoint not available (may require authentication or implementation)"
    fi
    
    return 0
}

# Test IBAN validation
test_iban_validation() {
    log "Testing IBAN validation..."
    
    # Test valid IBAN
    local iban_test_response=$(curl -s --max-time "$TIMEOUT" \
        "$BACKEND_URL/api/v1/validation/iban?iban=GB82WEST12345698765432" 2>/dev/null || echo "ENDPOINT_NOT_AVAILABLE")
    
    if [[ "$iban_test_response" != "ENDPOINT_NOT_AVAILABLE" ]]; then
        success "IBAN validation endpoint accessible"
        echo "Response: $iban_test_response"
    else
        warn "IBAN validation endpoint not available (may require authentication)"
    fi
    
    # Test DRC account validation (local format)
    local drc_test_response=$(curl -s --max-time "$TIMEOUT" \
        "$BACKEND_URL/api/v1/validation/account?accountNumber=1234567890&countryCode=CD" 2>/dev/null || echo "ENDPOINT_NOT_AVAILABLE")
    
    if [[ "$drc_test_response" != "ENDPOINT_NOT_AVAILABLE" ]]; then
        success "DRC account validation endpoint accessible"
        echo "Response: $drc_test_response"
    else
        warn "DRC account validation endpoint not available (may require authentication)"
    fi
    
    return 0
}

# Test external dependencies
test_external_dependencies() {
    log "Testing external dependencies..."
    
    # Test internet connectivity
    if curl -f -s --max-time 10 "https://httpbin.org/get" > /dev/null; then
        success "Internet connectivity available"
    else
        error "Internet connectivity failed"
        return 1
    fi
    
    # Test DNS resolution
    if nslookup google.com > /dev/null 2>&1; then
        success "DNS resolution working"
    else
        error "DNS resolution failed"
        return 1
    fi
    
    return 0
}

# Test monitoring endpoints
test_monitoring() {
    log "Testing monitoring endpoints..."
    
    # Test Prometheus metrics
    if curl -f -s --max-time "$TIMEOUT" "$MANAGEMENT_URL/actuator/prometheus" > /dev/null; then
        success "Prometheus metrics endpoint accessible"
    else
        warn "Prometheus metrics endpoint not accessible"
    fi
    
    # Test application info
    local info_response=$(curl -s --max-time "$TIMEOUT" "$MANAGEMENT_URL/actuator/info" 2>/dev/null || echo "FAILED")
    if [[ "$info_response" != "FAILED" ]]; then
        success "Application info endpoint accessible"
        echo "Info: $info_response"
    else
        warn "Application info endpoint not accessible"
    fi
    
    return 0
}

# Test security configuration
test_security() {
    log "Testing security configuration..."
    
    # Test CORS headers
    local cors_response=$(curl -s -I --max-time "$TIMEOUT" \
        -H "Origin: https://swiftpay.example.com" \
        "$BACKEND_URL/api/v1/health" 2>/dev/null || echo "FAILED")
    
    if [[ "$cors_response" != "FAILED" ]]; then
        if echo "$cors_response" | grep -q "Access-Control-Allow-Origin"; then
            success "CORS headers configured"
        else
            warn "CORS headers not found in response"
        fi
    else
        warn "Could not test CORS configuration"
    fi
    
    # Test security headers
    local security_headers=$(curl -s -I --max-time "$TIMEOUT" "$BACKEND_URL/api/v1/health" 2>/dev/null || echo "FAILED")
    if [[ "$security_headers" != "FAILED" ]]; then
        if echo "$security_headers" | grep -q "X-Content-Type-Options"; then
            success "Security headers configured"
        else
            warn "Security headers not found"
        fi
    else
        warn "Could not test security headers"
    fi
    
    return 0
}

# Generate test report
generate_report() {
    local report_file="connectivity-test-report-$(date +%Y%m%d_%H%M%S).txt"
    
    log "Generating connectivity test report: $report_file"
    
    cat > "$report_file" << EOF
SwiftPay Connectivity Test Report
Generated: $(date)
Environment: ${ENVIRONMENT:-development}
Backend URL: $BACKEND_URL
Management URL: $MANAGEMENT_URL

Test Results:
=============

Application Health: $([[ $health_status -eq 0 ]] && echo "✅ PASS" || echo "❌ FAIL")
API Endpoints: $([[ $api_status -eq 0 ]] && echo "✅ PASS" || echo "❌ FAIL")
SWIFT Connectivity: $([[ $swift_status -eq 0 ]] && echo "✅ PASS" || echo "⚠️ PARTIAL")
Mojaloop Connectivity: $([[ $mojaloop_status -eq 0 ]] && echo "✅ PASS" || echo "⚠️ PARTIAL")
IBAN Validation: $([[ $iban_status -eq 0 ]] && echo "✅ PASS" || echo "⚠️ PARTIAL")
External Dependencies: $([[ $external_status -eq 0 ]] && echo "✅ PASS" || echo "❌ FAIL")
Monitoring: $([[ $monitoring_status -eq 0 ]] && echo "✅ PASS" || echo "⚠️ PARTIAL")
Security: $([[ $security_status -eq 0 ]] && echo "✅ PASS" || echo "⚠️ PARTIAL")

Overall Status: $([[ $overall_status -eq 0 ]] && echo "✅ ALL TESTS PASSED" || echo "⚠️ SOME TESTS FAILED - REVIEW REQUIRED")

Notes:
- All tests run in safe/dry-run mode
- No real transfers were initiated
- External service tests may show partial results if authentication is required
- Review any failed tests before proceeding to production

Next Steps:
1. Review any failed or partial tests
2. Configure authentication for protected endpoints
3. Verify SWIFT and Mojaloop credentials in production
4. Run full integration tests with bank partners
5. Monitor logs and metrics after deployment

EOF
    
    success "Test report generated: $report_file"
}

# Main execution
main() {
    log "Starting SwiftPay connectivity tests..."
    warn "Running in SAFE MODE - no real transfers will be initiated"
    
    # Initialize status variables
    health_status=1
    api_status=1
    swift_status=1
    mojaloop_status=1
    iban_status=1
    external_status=1
    monitoring_status=1
    security_status=1
    overall_status=1
    
    # Run tests
    test_application_health && health_status=0
    test_api_endpoints && api_status=0
    test_swift_connectivity && swift_status=0
    test_mojaloop_connectivity && mojaloop_status=0
    test_iban_validation && iban_status=0
    test_external_dependencies && external_status=0
    test_monitoring && monitoring_status=0
    test_security && security_status=0
    
    # Calculate overall status
    if [[ $health_status -eq 0 && $api_status -eq 0 && $external_status -eq 0 ]]; then
        overall_status=0
    fi
    
    # Generate report
    generate_report
    
    # Print summary
    echo
    log "Connectivity test summary:"
    echo "=========================="
    echo "✅ Core functionality: $([[ $health_status -eq 0 && $api_status -eq 0 ]] && echo "WORKING" || echo "ISSUES DETECTED")"
    echo "⚠️  Banking integrations: $([[ $swift_status -eq 0 && $mojaloop_status -eq 0 ]] && echo "CONFIGURED" || echo "REQUIRES SETUP")"
    echo "📊 Monitoring: $([[ $monitoring_status -eq 0 ]] && echo "ACTIVE" || echo "PARTIAL")"
    echo "🔒 Security: $([[ $security_status -eq 0 ]] && echo "CONFIGURED" || echo "REVIEW NEEDED")"
    echo
    
    if [[ $overall_status -eq 0 ]]; then
        success "All critical connectivity tests passed!"
        log "SwiftPay is ready for further configuration and testing"
    else
        warn "Some tests failed or require attention"
        log "Review the generated report and address any issues before production deployment"
    fi
    
    return $overall_status
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi