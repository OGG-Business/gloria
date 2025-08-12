#!/usr/bin/env python3
"""
Configuration des certificats BCC pour envoi SWIFT réel
"""

import os
from pathlib import Path

def setup_bcc_certificates():
    """Configure les certificats BCC pour SWIFT réel"""
    print("🔧 CONFIGURATION DES CERTIFICATS BCC")
    print("="*50)
    
    # Création du dossier certificates
    cert_dir = Path("certificates")
    cert_dir.mkdir(exist_ok=True)
    
    print("📁 Dossier certificates créé")
    print("")
    print("📋 CERTIFICATS REQUIS POUR SWIFT RÉEL:")
    print("   - swift_client.crt (certificat client BCC)")
    print("   - swift_client.key (clé privée BCC)")
    print("   - swift_ca.crt (certificat CA SWIFT)")
    print("")
    print("💡 INSTRUCTIONS:")
    print("   1. Placez vos certificats BCC dans le dossier 'certificates/'")
    print("   2. Assurez-vous que les noms correspondent exactement")
    print("   3. Vérifiez les permissions (lecture seule pour les certificats)")
    print("")
    
    # Vérification des certificats existants
    required_files = [
        "certificates/swift_client.crt",
        "certificates/swift_client.key",
        "certificates/swift_ca.crt"
    ]
    
    print("🔍 Vérification des certificats existants:")
    missing_files = []
    
    for file_path in required_files:
        cert_path = Path(file_path)
        if cert_path.exists():
            size = cert_path.stat().st_size
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path} (manquant)")
            missing_files.append(file_path)
    
    if missing_files:
        print("")
        print("⚠️ CERTIFICATS MANQUANTS:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("")
        print("📥 Veuillez placer vos certificats BCC dans le dossier 'certificates/'")
        print("")
        
        # Création de fichiers d'exemple
        print("📝 Création de fichiers d'exemple (à remplacer par vos vrais certificats):")
        for file_path in missing_files:
            cert_path = Path(file_path)
            cert_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Création d'un fichier d'exemple
            with open(cert_path, 'w') as f:
                f.write(f"# Remplacez ce contenu par votre vrai certificat {cert_path.name}\n")
                f.write(f"# Format attendu pour {cert_path.name}:\n")
                
                if cert_path.name == "swift_client.crt":
                    f.write("# -----BEGIN CERTIFICATE-----\n")
                    f.write("# Votre certificat client BCC ici\n")
                    f.write("# -----END CERTIFICATE-----\n")
                elif cert_path.name == "swift_client.key":
                    f.write("# -----BEGIN PRIVATE KEY-----\n")
                    f.write("# Votre clé privée BCC ici\n")
                    f.write("# -----END PRIVATE KEY-----\n")
                elif cert_path.name == "swift_ca.crt":
                    f.write("# -----BEGIN CERTIFICATE-----\n")
                    f.write("# Certificat CA SWIFT ici\n")
                    f.write("# -----END CERTIFICATE-----\n")
            
            print(f"   �� {file_path} créé (exemple)")
    else:
        print("")
        print("✅ TOUS LES CERTIFICATS BCC SONT PRÉSENTS!")
        print("L'application est prête pour l'envoi SWIFT réel.")
    
    print("")
    print("🔒 SÉCURITÉ DES CERTIFICATS:")
    print("   - Ne partagez jamais vos certificats")
    print("   - Utilisez des permissions restrictives")
    print("   - Sauvegardez vos certificats en lieu sûr")
    print("   - Changez régulièrement vos certificats")
    
    # Configuration des permissions
    print("")
    print("🔐 Configuration des permissions:")
    for file_path in required_files:
        cert_path = Path(file_path)
        if cert_path.exists():
            # Permissions restrictives (lecture seule pour le propriétaire)
            os.chmod(cert_path, 0o600)
            print(f"   🔒 {file_path} - Permissions sécurisées")
    
    print("")
    print("🎯 PROCHAINES ÉTAPES:")
    print("   1. Remplacez les fichiers d'exemple par vos vrais certificats")
    print("   2. Exécutez: python test_real_swift_bcc.py")
    print("   3. Confirmez l'envoi SWIFT réel")
    print("   4. Suivez le transfert via GPI")

def verify_certificate_format():
    """Vérifie le format des certificats"""
    print("\n🔍 VÉRIFICATION DU FORMAT DES CERTIFICATS:")
    
    cert_files = {
        "swift_client.crt": "CERTIFICAT CLIENT BCC",
        "swift_client.key": "CLÉ PRIVÉE BCC", 
        "swift_ca.crt": "CERTIFICAT CA SWIFT"
    }
    
    for filename, description in cert_files.items():
        file_path = Path(f"certificates/{filename}")
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()
                
            print(f"\n📄 {description} ({filename}):")
            
            if "BEGIN CERTIFICATE" in content:
                print("   ✅ Format certificat détecté")
            elif "BEGIN PRIVATE KEY" in content:
                print("   ✅ Format clé privée détecté")
            elif "Remplacez ce contenu" in content:
                print("   ⚠️ Fichier d'exemple - à remplacer")
            else:
                print("   ❓ Format non reconnu")
                
            # Vérification de la taille
            size = file_path.stat().st_size
            if size < 100:
                print("   ⚠️ Fichier trop petit - probablement un exemple")
            else:
                print(f"   ✅ Taille correcte ({size} bytes)")

def main():
    """Fonction principale"""
    print("🚀 CONFIGURATION CERTIFICATS BCC POUR SWIFT RÉEL")
    print("="*60)
    
    try:
        # Configuration des certificats
        setup_bcc_certificates()
        
        # Vérification du format
        verify_certificate_format()
        
        print("\n" + "="*60)
        print("✅ CONFIGURATION TERMINÉE")
        print("="*60)
        print("")
        print("💡 POUR ENVOYER UN TRANSFERT SWIFT RÉEL:")
        print("   python test_real_swift_bcc.py")
        print("")
        print("📞 SUPPORT:")
        print("   - Vérifiez que vos certificats BCC sont valides")
        print("   - Contactez BCC si vous avez des questions")
        print("   - Assurez-vous d'avoir les autorisations nécessaires")
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {e}")

if __name__ == "__main__":
    main()
