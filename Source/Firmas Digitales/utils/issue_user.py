import os
import sys
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.backends import default_backend

CA_CERT_PATH = './certs/root/cert.pem'
CA_KEY_PATH = './certs/root/private_key.pem'
USERS_DIR = './certs/users/'

def load_ca():
    with open(CA_CERT_PATH, 'rb') as f:
        ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())
    with open(CA_KEY_PATH, 'rb') as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None)
    return ca_cert, ca_key

def issue_user_cert(username: str, email: str):
    ca_cert, ca_key = load_ca()

    user_dir = os.path.join(USERS_DIR, email)
    os.makedirs(user_dir, exist_ok=True)

    # Generate user private key
    # user_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    user_key = ec.generate_private_key(ec.SECP384R1())
    with open(os.path.join(user_dir, 'private_key.pem'), 'wb') as f:
        f.write(user_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Build user certificate
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"MX"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Nuevo León"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Monterrey"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Morfosis"),
        x509.NameAttribute(NameOID.COMMON_NAME, username),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        user_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now()
    ).not_valid_after(
        datetime.now() + timedelta(days=365 * 2)
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=True,  # Non-repudiation
            key_encipherment=False,   # usually False for EC
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False
        ), critical=True
    ).add_extension(
        x509.ExtendedKeyUsage([
            ExtendedKeyUsageOID.CODE_SIGNING,
            ExtendedKeyUsageOID.EMAIL_PROTECTION
        ]), critical=False
    ).sign(ca_key, hashes.SHA256())

    # Save user certificate
    with open(os.path.join(user_dir, 'cert.pem'), 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"Issued certificate for {username}.")

# Example usage
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python issue_user_cert.py <username> <email>")
    else:
        issue_user_cert(sys.argv[1], sys.argv[2])
