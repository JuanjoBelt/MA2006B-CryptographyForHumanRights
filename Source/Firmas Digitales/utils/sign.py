import os
import sys
import asyncio
from pyhanko import stamp
from pyhanko.pdf_utils import text
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers
from pyhanko.sign.signers import PdfSignatureMetadata

USERS_DIR = './certs/users/'

def find_user_dir_by_email(email: str) -> str:
    """Return user dir path from email lookup in users/."""
    CERT_PATH = f"{USERS_DIR}/{email}/cert.pem"
    print(f"Checking {CERT_PATH} for email {email}...")
    if not os.path.exists(CERT_PATH):
        raise FileNotFoundError(f"Certificate for {email} not found in {USERS_DIR}.")
    return os.path.dirname(CERT_PATH)

async def sign_pdf(pdf_path: str, email: str):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"{pdf_path} does not exist.")

    pdf_name = os.path.basename(pdf_path)
    signed_pdf_path = f'./signed_files/{pdf_name}'

    user_dir = find_user_dir_by_email(email)
    cert_path = os.path.join(user_dir, 'cert.pem')
    key_path = os.path.join(user_dir, 'private_key.pem')

    print(f"Signing {pdf_name} with certificate of {email}...")

    # Load the CMS signer
    cms_signer = signers.SimpleSigner.load(
        key_path, cert_path,
        ca_chain_files=(cert_path,),  # Assuming no intermediate chain
        key_passphrase=None
    )

    with open(pdf_path, 'rb') as doc:
        w = IncrementalPdfFileWriter(doc)

        # Add visible signature field (bottom-right corner box)
        fields.append_signature_field(
            w,
            sig_field_spec=fields.SigFieldSpec(
                'Signature', box=(0, 0, 250, 40)  # Adjust as needed
            )
        )

        meta = PdfSignatureMetadata(field_name='Signature')

        qr_style = stamp.QRStampStyle(
            stamp_text='Signed by: %(signer)s\nTime: %(ts)s\nURL: %(url)s',
            text_box_style=text.TextBoxStyle(font_size=14),
        )

        pdf_signer = signers.PdfSigner(
            signature_meta=meta,
            signer=cms_signer,
            stamp_style=qr_style
        )

        with open(signed_pdf_path, 'wb') as outf:
            await pdf_signer.async_sign_pdf(
                w,
                output=outf,
                appearance_text_params={'url': 'https://github.com/Racoo203'}
            )

    print(f"Done. Signed file: {signed_pdf_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python sign.py <pdf_path> <email>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    email = sys.argv[2]

    asyncio.run(sign_pdf(pdf_path, email))