import os
import subprocess

def generate_ssl_certificates():
    """
    Generates the SSL certificates needed for TLS:
    - Authority certificate (CA)
    - Server certificate signed by the CA
    - Associated private keys
    """
    cert_dir = os.path.join(os.path.dirname(__file__), '..', 'ssl_certificates')
    os.makedirs(cert_dir, exist_ok=True)
    
    # Chemins des fichiers
    ca_key_path = os.path.join(cert_dir, 'ca.key')
    ca_cert_path = os.path.join(cert_dir, 'ca.pem')
    cert_path = os.path.join(cert_dir, 'cert.pem')
    key_path = os.path.join(cert_dir, 'key.pem')
    csr_path = os.path.join(cert_dir, 'server.csr')
    
    # Vérifie si les certificats existent déjà
    if (not os.path.exists(ca_cert_path) or 
        not os.path.exists(cert_path) or 
        not os.path.exists(key_path)):
        
        print("Generating SSL Certificates...")
        
        try:
            # 1. Générer la clé privée du CA
            subprocess.run([
                "openssl", "genrsa",
                "-out", ca_key_path,
                "4096"
            ], check=True)
            
            # 2. Générer le certificat CA auto-signé
            subprocess.run([
                "openssl", "req", "-x509", "-new", "-nodes",
                "-key", ca_key_path,
                "-sha256",
                "-days", "3650",
                "-out", ca_cert_path,
            ], check=True)
            
            # 3. Générer la clé privée du serveur
            subprocess.run([
                "openssl", "genrsa",
                "-out", key_path,
                "2048"
            ], check=True)
            
            # 4. Créer la demande de signature de certificat (CSR)
            subprocess.run([
                "openssl", "req", "-new",
                "-key", key_path,
                "-out", csr_path,
            ], check=True)
            
            # 5. Signer le certificat serveur avec le CA
            subprocess.run([
                "openssl", "x509", "-req",
                "-in", csr_path,
                "-CA", ca_cert_path,
                "-CAkey", ca_key_path,
                "-CAcreateserial",
                "-out", cert_path,
                "-days", "365",
                "-sha256"
            ], check=True)
            
            # 6. Nettoyer les fichiers temporaires
            os.remove(csr_path)
            os.remove(ca_key_path)
            if os.path.exists(os.path.join(cert_dir, 'ca.srl')):
                os.remove(os.path.join(cert_dir, 'ca.srl'))
                
                print("Certificates generated successfully:")
                print(f"- CA certificate: {ca_cert_path}")
                print(f"- Server certificate: {cert_path}")
                print(f"- Server private key: {key_path}")
            
        except subprocess.CalledProcessError as e:
            print(f"Error generating certificates: {e}")
            # Nettoyer les fichiers partiellement créés en cas d'erreur
            for file in [ca_key_path, ca_cert_path, cert_path, key_path, csr_path]:
                if os.path.exists(file):
                    os.remove(file)
            raise
            
    else:
        print("SSL certificates already exist.")

if __name__ == "__main__":
    generate_ssl_certificates()