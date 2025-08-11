#!/bin/bash

# SwiftPay Archive Creation Script
# Creates a complete distributable package of the SwiftPay project

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VERSION=${VERSION:-"1.0.0"}
ARCHIVE_NAME="swiftpay-${VERSION}"
BUILD_DIR="dist"

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Clean and create build directory
prepare_build_dir() {
    log "Preparing build directory..."
    
    rm -rf "$BUILD_DIR"
    mkdir -p "$BUILD_DIR/$ARCHIVE_NAME"
    
    success "Build directory prepared: $BUILD_DIR/$ARCHIVE_NAME"
}

# Copy project files
copy_project_files() {
    log "Copying project files..."
    
    # Core project structure
    cp -r backend "$BUILD_DIR/$ARCHIVE_NAME/"
    cp -r frontend "$BUILD_DIR/$ARCHIVE_NAME/"
    cp -r k8s "$BUILD_DIR/$ARCHIVE_NAME/"
    cp -r helm "$BUILD_DIR/$ARCHIVE_NAME/"
    cp -r terraform "$BUILD_DIR/$ARCHIVE_NAME/"
    cp -r scripts "$BUILD_DIR/$ARCHIVE_NAME/"
    cp -r docs "$BUILD_DIR/$ARCHIVE_NAME/"
    cp -r monitoring "$BUILD_DIR/$ARCHIVE_NAME/"
    
    # Root configuration files
    cp docker-compose.yml "$BUILD_DIR/$ARCHIVE_NAME/"
    cp .env.example "$BUILD_DIR/$ARCHIVE_NAME/"
    cp README.md "$BUILD_DIR/$ARCHIVE_NAME/"
    cp ONBOARDING_SWIFT.md "$BUILD_DIR/$ARCHIVE_NAME/"
    
    # License and legal
    if [[ -f LICENSE ]]; then
        cp LICENSE "$BUILD_DIR/$ARCHIVE_NAME/"
    fi
    
    success "Project files copied"
}

# Clean unnecessary files
clean_unnecessary_files() {
    log "Cleaning unnecessary files..."
    
    # Remove development artifacts
    find "$BUILD_DIR/$ARCHIVE_NAME" -name "target" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BUILD_DIR/$ARCHIVE_NAME" -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BUILD_DIR/$ARCHIVE_NAME" -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BUILD_DIR/$ARCHIVE_NAME" -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BUILD_DIR/$ARCHIVE_NAME" -name "*.log" -type f -delete 2>/dev/null || true
    find "$BUILD_DIR/$ARCHIVE_NAME" -name ".DS_Store" -type f -delete 2>/dev/null || true
    
    # Remove IDE files
    find "$BUILD_DIR/$ARCHIVE_NAME" -name ".idea" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BUILD_DIR/$ARCHIVE_NAME" -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BUILD_DIR/$ARCHIVE_NAME" -name "*.iml" -type f -delete 2>/dev/null || true
    
    success "Unnecessary files cleaned"
}

# Generate checksums
generate_checksums() {
    log "Generating checksums..."
    
    cd "$BUILD_DIR"
    
    # Generate SHA256 checksums for all files
    find "$ARCHIVE_NAME" -type f -exec sha256sum {} \; > "${ARCHIVE_NAME}.sha256"
    
    # Generate MD5 checksums for compatibility
    find "$ARCHIVE_NAME" -type f -exec md5sum {} \; > "${ARCHIVE_NAME}.md5"
    
    cd ..
    
    success "Checksums generated"
}

# Create archive
create_archive() {
    log "Creating archive..."
    
    cd "$BUILD_DIR"
    
    # Create tar.gz archive
    tar -czf "${ARCHIVE_NAME}.tar.gz" "$ARCHIVE_NAME"
    
    # Create zip archive for Windows compatibility
    zip -r "${ARCHIVE_NAME}.zip" "$ARCHIVE_NAME" > /dev/null
    
    cd ..
    
    success "Archives created:"
    echo "  - ${BUILD_DIR}/${ARCHIVE_NAME}.tar.gz"
    echo "  - ${BUILD_DIR}/${ARCHIVE_NAME}.zip"
}

# Generate installation instructions
generate_installation_instructions() {
    log "Generating installation instructions..."
    
    cat > "$BUILD_DIR/INSTALLATION.md" << 'EOF'
# SwiftPay Installation Guide

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Java 17+ (for backend development)
- Node.js 20+ (for frontend development)
- kubectl and Helm (for Kubernetes deployment)

### Local Development Setup

1. **Extract the archive:**
   ```bash
   tar -xzf swiftpay-1.0.0.tar.gz
   cd swiftpay-1.0.0
   ```

2. **Run the development setup:**
   ```bash
   ./scripts/setup-dev.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - API Documentation: http://localhost:8080/swagger-ui/index.html
   - Grafana: http://localhost:3001 (admin/admin)

### Production Deployment

1. **Kubernetes Deployment:**
   ```bash
   # Using kubectl
   kubectl apply -f k8s/
   
   # Using Helm
   helm install swiftpay helm/swiftpay
   
   # Using Terraform
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

2. **Production Setup:**
   ```bash
   ./scripts/setup-prod.sh
   ```

### Testing Connectivity

```bash
./scripts/test-connectivity.sh
```

## Important Security Notes

⚠️ **CRITICAL WARNING**: This software handles financial transactions. Before processing real money:

1. Complete security review and penetration testing
2. Obtain proper banking licenses and agreements
3. Configure real SWIFT/bank certificates
4. Implement proper monitoring and alerting
5. Ensure compliance with local financial regulations

## Support

For technical support and documentation:
- Read the complete README.md
- Review ONBOARDING_SWIFT.md for SWIFT integration
- Check docs/api/openapi.yaml for API documentation
- Review monitoring/ for observability setup

## License

This project is licensed under the MIT License - see the LICENSE file for details.
EOF
    
    success "Installation instructions generated: $BUILD_DIR/INSTALLATION.md"
}

# Validate archive contents
validate_archive() {
    log "Validating archive contents..."
    
    local required_files=(
        "README.md"
        "ONBOARDING_SWIFT.md"
        "docker-compose.yml"
        ".env.example"
        "backend/pom.xml"
        "backend/src/main/java/com/swiftpay/SwiftPayApplication.java"
        "frontend/package.json"
        "frontend/src/App.tsx"
        "k8s/namespace.yaml"
        "helm/swiftpay/Chart.yaml"
        "terraform/main.tf"
        "scripts/setup-dev.sh"
        "scripts/setup-prod.sh"
        "scripts/test-connectivity.sh"
        "docs/api/openapi.yaml"
    )
    
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$BUILD_DIR/$ARCHIVE_NAME/$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -eq 0 ]]; then
        success "All required files present in archive"
    else
        error "Missing required files: ${missing_files[*]}"
        return 1
    fi
    
    # Check archive sizes
    local tar_size=$(du -h "$BUILD_DIR/${ARCHIVE_NAME}.tar.gz" | cut -f1)
    local zip_size=$(du -h "$BUILD_DIR/${ARCHIVE_NAME}.zip" | cut -f1)
    
    log "Archive sizes:"
    echo "  - TAR.GZ: $tar_size"
    echo "  - ZIP: $zip_size"
    
    return 0
}

# Generate final summary
generate_summary() {
    log "Generating final summary..."
    
    cat > "$BUILD_DIR/PACKAGE_SUMMARY.txt" << EOF
SwiftPay v${VERSION} - Complete Package Summary
===============================================

Generated: $(date)
Package Contents:
- Complete source code (backend + frontend)
- Infrastructure as Code (Kubernetes, Helm, Terraform)
- Development and production setup scripts
- Comprehensive documentation
- Security and compliance configurations
- Monitoring and observability setup

Quick Start:
1. Extract archive: tar -xzf ${ARCHIVE_NAME}.tar.gz
2. Read INSTALLATION.md for setup instructions
3. Run: ./scripts/setup-dev.sh for local development
4. Review ONBOARDING_SWIFT.md for production deployment

⚠️ IMPORTANT SECURITY REMINDERS:
- This software handles real financial transactions
- Complete security review required before production use
- Obtain proper banking agreements and certificates
- Ensure compliance with financial regulations
- Never process real money without proper authorization

For support: team@swiftpay.org
Documentation: README.md, docs/
License: MIT (see LICENSE file)

Package Integrity:
- SHA256: See ${ARCHIVE_NAME}.sha256
- MD5: See ${ARCHIVE_NAME}.md5
EOF
    
    success "Package summary generated: $BUILD_DIR/PACKAGE_SUMMARY.txt"
}

# Main execution
main() {
    log "Starting SwiftPay archive creation..."
    
    prepare_build_dir
    copy_project_files
    clean_unnecessary_files
    generate_checksums
    create_archive
    generate_installation_instructions
    validate_archive
    generate_summary
    
    echo
    success "SwiftPay v${VERSION} archive created successfully!"
    echo
    echo "📦 Package Files:"
    echo "  - ${BUILD_DIR}/${ARCHIVE_NAME}.tar.gz"
    echo "  - ${BUILD_DIR}/${ARCHIVE_NAME}.zip"
    echo "  - ${BUILD_DIR}/${ARCHIVE_NAME}.sha256"
    echo "  - ${BUILD_DIR}/${ARCHIVE_NAME}.md5"
    echo "  - ${BUILD_DIR}/INSTALLATION.md"
    echo "  - ${BUILD_DIR}/PACKAGE_SUMMARY.txt"
    echo
    echo "📋 Next Steps:"
    echo "  1. Review package contents and checksums"
    echo "  2. Test installation in clean environment"
    echo "  3. Distribute to authorized personnel only"
    echo "  4. Follow INSTALLATION.md for deployment"
    echo
    warn "Remember: Complete security review required before production use!"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi