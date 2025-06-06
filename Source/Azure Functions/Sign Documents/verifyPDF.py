from pyhanko.keys import load_cert_from_pemder
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
import logging

root_cert_path = 'certs/root/rootCA.pem'

def verify_pdf_signature(signed_pdf_path):

    logging.info(f"Verifying signature in: {signed_pdf_path}")

    try:
        root_cert = load_cert_from_pemder(root_cert_path)
        vc = ValidationContext(trust_roots=[root_cert])
    except:
        logging.error("ERROR: No se pudo cargar root cert.")
        return

    try:
        with open(signed_pdf_path, 'rb') as doc:
            reader = PdfFileReader(doc)

            if not reader.embedded_signatures:
                logging.error("ERROR: No signature fields found in the PDF.")
                return
            try:
                sig = reader.embedded_signatures[0]
                status = validate_pdf_signature(sig, vc)
                logging.info("Se analizó correctamente la firma.")
                try:
                    common_name = status.pretty_print_sections()[0][1].split("\n")[0].split("Common Name: ")[1].split(",")[0]
                    logging.info("Se obtuvo el nombre del firmante anterior.")
                except:
                    logging.error("No se pudo obtener el nombre del firmante anterior.")
                    return
                return status.valid, common_name
            except:
                logging.error("ERROR: Ocurrió un error al validar la firma.")
    except:
        logging.error("ERROR: Occurrió un error al intentar cargar el PDF firmado.")