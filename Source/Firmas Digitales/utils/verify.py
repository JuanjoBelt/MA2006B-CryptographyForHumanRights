import sys
import os
from pyhanko.keys import load_cert_from_pemder
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature

def verify_pdf_signature(signed_pdf_path: str):
    if not os.path.isfile(signed_pdf_path):
        raise FileNotFoundError(f"PDF file not found: {signed_pdf_path}")

    pdf_name = os.path.basename(signed_pdf_path)
    root_cert_path = f'./certs/root/cert.pem'

    print(f"Verifying signature in: {pdf_name}")
    root_cert = load_cert_from_pemder(root_cert_path)
    vc = ValidationContext(trust_roots=[root_cert])

    with open(signed_pdf_path, 'rb') as doc:
        reader = PdfFileReader(doc)

        if not reader.embedded_signatures:
            print("[X] No signature fields found in the PDF.")
            return

        sig = reader.embedded_signatures[0]
        status = validate_pdf_signature(sig, vc)
        print(status.pretty_print_details())

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python verify.py <signed_pdf_path>")
        sys.exit(1)

    signed_pdf = sys.argv[1]

    verify_pdf_signature(signed_pdf)