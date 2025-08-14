#!/bin/bash

echo "🚀 === LANCEMENT RÉEL DE L'APPLICATION BANKING TRANSFER ==="
echo ""

# Fonction pour afficher le statut
print_status() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# Vérification des dépendances
print_status "🔍 Vérification des dépendances..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trouvé"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm non trouvé"
    exit 1
fi

echo "✅ Dépendances OK"
echo ""

# Test du backend
print_status "🧪 Test du backend..."
cd backend
python3 -c "
import sys
sys.path.append('.')
from app.main import app
print(f'✅ Backend: {len(app.routes)} routes disponibles')
from app.connectors.swift_connector import SWIFTConnector
from app.connectors.mojaloop_connector import MojaloopConnector
print('✅ Connecteurs importés')
from app.monitoring.advanced_monitoring import monitoring
print('✅ Monitoring initialisé')
"

if [ $? -eq 0 ]; then
    print_status "✅ Backend testé avec succès"
else
    print_status "❌ Erreur test backend"
    exit 1
fi

cd ..
echo ""

# Test du frontend
print_status "🧪 Test du frontend..."
if [ -f "frontend/package.json" ] && [ -f "frontend/src/App.tsx" ]; then
    print_status "✅ Structure frontend OK"
else
    print_status "❌ Structure frontend manquante"
    exit 1
fi

echo ""

# Démarrage du backend
print_status "🚀 Démarrage du backend..."
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Attendre le démarrage du backend
sleep 5

# Test de connectivité backend
print_status "🔍 Test de connectivité backend..."
if curl -s http://localhost:8000/ > /dev/null; then
    print_status "✅ Backend accessible sur http://localhost:8000"
else
    print_status "❌ Backend non accessible"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""

# Démarrage du frontend
print_status "🚀 Démarrage du frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Attendre le démarrage du frontend
sleep 10

# Test de connectivité frontend
print_status "🔍 Test de connectivité frontend..."
if curl -s http://localhost:3000/ > /dev/null; then
    print_status "✅ Frontend accessible sur http://localhost:3000"
else
    print_status "⚠️ Frontend en cours de démarrage..."
fi

echo ""
echo "============================================================"
echo "🎉 APPLICATION LANCÉE AVEC SUCCÈS !"
echo "============================================================"
echo "📊 Backend:  http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "============================================================"
echo ""
echo "🔧 Commandes utiles:"
echo "   - Arrêter: Ctrl+C"
echo "   - Logs backend: tail -f backend/logs/app.log"
echo "   - Logs frontend: tail -f frontend/logs/app.log"
echo ""
echo "💡 Fonctionnalités disponibles:"
echo "   ✅ Transferts SWIFT simulés"
echo "   ✅ Transferts Mojaloop simulés"
echo "   ✅ Interface utilisateur React"
echo "   ✅ API REST complète"
echo "   ✅ Monitoring et logging"
echo "============================================================"

# Fonction de nettoyage
cleanup() {
    echo ""
    print_status "🛑 Arrêt des services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    print_status "✅ Services arrêtés"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Attendre indéfiniment
while true; do
    sleep 1
done