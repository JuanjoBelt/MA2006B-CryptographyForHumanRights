from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.x509.oid import NameOID
from cryptography import x509
from datetime import datetime, timedelta
import os

def main():
    # Paths
    CA_DIR = './certs/root/'
    PRIVATE_KEY_PATH = os.path.join(CA_DIR, 'private_key.pem')
    CERT_PATH = os.path.join(CA_DIR, 'cert.pem')

    # Create directory if needed
    os.makedirs(CA_DIR, exist_ok=True)

    # # Generate private key
    # private_key = rsa.generate_private_key(
    #     public_exponent=65537,
    #     key_size=4096
    # )

    private_key = ec.generate_private_key(
        curve=ec.SECP384R1()  # or SECP256R1
    )

    # Save private key
    with open(PRIVATE_KEY_PATH, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Create self-signed cert
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"MX"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Nuevo León"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Monterrey"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Morfosis"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"Morfosis Root"),
    ])

    cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now()
    ).not_valid_after(
        # Valid for 10 years
        datetime.now() + timedelta(days=3650)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True
    ).sign(private_key, hashes.SHA256())

    # Save certificate
    with open(CERT_PATH, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("Root CA generated successfully.")

if __name__ == "__main__":
    main()
