# —————————————————————————————————————————————————————————————————————————— 
#                      Módulo para Firmar Documentos
#                             Updated 03/06/25
# ——————————————————————————————————————————————————————————————————————————
from PyPDF2 import PdfReader, PdfWriter
import io
import asyncio
from pyhanko import stamp
from pyhanko.pdf_utils import text, images
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers

root_url = "https://docs4morfosis.blob.core.windows.net/"

# —————————————————————————————————————————————————————————————————————————— 
#                           Función de Firmado
# ——————————————————————————————————————————————————————————————————————————

async def sign_pdf_async(pdf_path, signed_pdf_path, key_path, cert_path, online_pdf_path):
    #print(f"Signing {pdf_name}...")

       # Load the CMS signer
    cms_signer = signers.SimpleSigner.load(
        key_path, cert_path,
        ca_chain_files=(cert_path,),  # Assuming no intermediate chain
        key_passphrase=None
    )

    # with open(pdf_path, 'rb') as doc:
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Copy existing pages to the writer
    for page_num in range(len(reader.pages)):
        writer.add_page(reader.pages[page_num])

    # Add a new blank page
    writer.add_blank_page(width=8.27 * 72, height=11.7 * 12)

    # Save the modified PDF
    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)

    w = IncrementalPdfFileWriter(io.BytesIO(output_stream.getvalue()), strict = False)

    # Add visible signature field (bottom-right corner box)

    fields.append_signature_field(
        w,
        sig_field_spec=fields.SigFieldSpec(
            sig_field_name="Signature",
            on_page=len(reader.pages),
            box=(0, 0, 8.27 * 72, 11.7 * 12)
        )
    )
    
    meta = signers.PdfSignatureMetadata(field_name='Signature')
    qr_style = stamp.QRStampStyle(
        stamp_text='Signed by: %(signer)s\nTime: %(ts)s\nURL: %(url)s',
        text_box_style=text.TextBoxStyle(
            font_size=18,
            border_width=0
        ),
        border_width = 0,
        background = images.PdfImage('img/morfosisBackground.png')
    )

    pdf_signer = signers.PdfSigner(
        signature_meta=meta,
        signer=cms_signer,
        stamp_style=qr_style
    )

    # Sign and write to the output file
    with open(signed_pdf_path, 'wb') as outf:
        await pdf_signer.async_sign_pdf(
            w,
            output=outf,
            appearance_text_params={'url': root_url + online_pdf_path}
        )

    print("Done signing.")

# Execute the async function
def sign_pdf(pdf_path, signed_pdf_path, key_path, cert_path, online_pdf_path):
    asyncio.run(sign_pdf_async(pdf_path, signed_pdf_path, key_path, cert_path, online_pdf_path))