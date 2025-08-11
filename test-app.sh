#!/bin/bash

echo "=== Test de l'application Banking Transfer Platform ==="
echo

# Test du backend
echo "1. Test du backend..."
cd backend
if mvn clean compile -q; then
    echo "✅ Backend: Compilation réussie"
else
    echo "❌ Backend: Erreur de compilation"
    exit 1
fi

# Test du frontend
echo "2. Test du frontend..."
cd ../frontend
if npm run build --silent; then
    echo "✅ Frontend: Build réussi"
else
    echo "❌ Frontend: Erreur de build"
    exit 1
fi

echo
echo "=== Résumé ==="
echo "✅ Backend: Compilation OK"
echo "✅ Frontend: Build OK"
echo "⚠️  Note: Les services ne sont pas démarrés (base de données manquante)"
echo
echo "Pour démarrer l'application complète:"
echo "1. Installer et configurer PostgreSQL, Redis, Kafka"
echo "2. Lancer: docker-compose up -d"
echo "3. Lancer le backend: cd backend && mvn spring-boot:run"
echo "4. Lancer le frontend: cd frontend && npm start"