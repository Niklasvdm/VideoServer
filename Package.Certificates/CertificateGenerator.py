
# ssl_setup.py
from OpenSSL import crypto
import os

def create_self_signed_cert():
    """Create a self-signed certificate for development"""
    
    # Generate key
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    # Generate certificate
    cert = crypto.X509()
    cert.get_subject().CN = "localhost"
    cert.get_subject().O = "Development"
    cert.get_subject().OU = "Development Team"
    cert.get_subject().C = "US"
    cert.get_subject().ST = "Development State"
    cert.get_subject().L = "Development City"
    
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for one year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')
    
    # Save certificate and private key
    with open("cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open("key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    print("Certificate and key files created: cert.pem, key.pem")

if __name__ == "__main__":
    create_self_signed_cert()