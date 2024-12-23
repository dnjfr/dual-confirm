import os
import subprocess

# Generate SSL certificates function
def generate_ssl_certificates():
    cert_dir = os.path.join(os.path.dirname(__file__), '..', 'ssl_certificates')
    os.makedirs(cert_dir, exist_ok=True)
    
    cert_path = os.path.join(cert_dir, 'cert.pem')
    key_path = os.path.join(cert_dir, 'key.pem')
    
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("Generating SSL Certificates...")
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", key_path, "-out", cert_path,
            "-days", "365", "-nodes"
        ])
        print(f"Generated Certificates:\n- {cert_path}\n- {key_path}")
    else:
        print("SSL certificates already exist.")

if __name__ == "__main__":
    generate_ssl_certificates()
