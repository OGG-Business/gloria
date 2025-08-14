#!/bin/bash
echo "🚀 === LANCEMENT COMPLET BANKING TRANSFER PLATFORM ==="
echo ""

echo "🔍 Test du backend..."
cd backend
python -c "from app.main import app; print('✅ Backend OK')"
echo ""

echo "🚀 Lancement du serveur backend..."
echo "Le serveur sera accessible sur http://localhost:8000"
echo "Appuyez sur Ctrl+C pour arrêter"
echo ""

# Lance le serveur en arrière-plan et capture le PID
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Attend que le serveur démarre
sleep 5

echo "🔍 Test de l'API..."
curl -s http://localhost:8000/ && echo ""
curl -s http://localhost:8000/health && echo ""
curl -s http://localhost:8000/auth/ && echo ""
curl -s http://localhost:8000/accounts/ && echo ""
curl -s http://localhost:8000/transfers/ && echo ""

echo ""
echo "✅ Application lancée avec succès!"
echo "📋 Endpoints disponibles sur http://localhost:8000"
echo "📖 Documentation: http://localhost:8000/docs"

# Garde le script en vie
wait $BACKEND_PID
