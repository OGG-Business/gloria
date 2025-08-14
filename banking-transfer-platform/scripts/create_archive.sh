#!/bin/bash

# Script de création d'archive du projet Banking Transfer Platform
# Usage: ./scripts/create_archive.sh [version]

set -e

# Configuration
PROJECT_NAME="banking-transfer-platform"
VERSION=${1:-"1.0.0"}
ARCHIVE_NAME="${PROJECT_NAME}-${VERSION}.tar.gz"
TEMP_DIR="/tmp/${PROJECT_NAME}-archive"

echo "🚀 Création de l'archive ${ARCHIVE_NAME}..."

# Nettoyer le répertoire temporaire
rm -rf "${TEMP_DIR}"
mkdir -p "${TEMP_DIR}"

# Copier les fichiers du projet
echo "📁 Copie des fichiers du projet..."
cp -r \
    backend/ \
    frontend/ \
    docs/ \
    infrastructure/ \
    scripts/ \
    docker-compose.yml \
    docker-compose.prod.yml \
    Makefile \
    README.md \
    LICENSE \
    .gitignore \
    requirements.txt \
    package.json \
    "${TEMP_DIR}/"

# Créer le fichier de version
echo "${VERSION}" > "${TEMP_DIR}/VERSION"

# Créer le fichier de checksum
echo "🔍 Calcul des checksums..."
cd "${TEMP_DIR}"
find . -type f -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "*.sh" | sort | xargs sha256sum > checksums.txt

# Créer l'archive
echo "📦 Création de l'archive..."
tar -czf "${ARCHIVE_NAME}" --exclude='__pycache__' --exclude='node_modules' --exclude='.git' --exclude='*.pyc' --exclude='*.log' .

# Déplacer l'archive dans le répertoire courant
mv "${ARCHIVE_NAME}" "/workspace/${ARCHIVE_NAME}"

# Nettoyer
rm -rf "${TEMP_DIR}"

echo "✅ Archive créée avec succès: ${ARCHIVE_NAME}"
echo "📊 Taille de l'archive: $(du -h "/workspace/${ARCHIVE_NAME}" | cut -f1)"

# Afficher le contenu de l'archive
echo "📋 Contenu de l'archive:"
tar -tzf "/workspace/${ARCHIVE_NAME}" | head -20
echo "... (et plus)"

echo "🎉 Archive prête pour la livraison !"
