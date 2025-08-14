#!/bin/bash
echo "🚀 === LANCEMENT BANKING TRANSFER PLATFORM ==="
echo ""

echo "🔍 Test du backend..."
cd backend
python -c "from app.main import app; print('✅ Backend OK')"
echo ""

echo "🚀 Lancement du serveur..."
echo "Le serveur sera accessible sur http://localhost:8000"
echo "Appuyez sur Ctrl+C pour arrêter"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000
