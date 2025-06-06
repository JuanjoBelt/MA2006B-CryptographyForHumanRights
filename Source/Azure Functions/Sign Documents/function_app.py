# —————————————————————————————————————————————————————————————————————————— 
#                       Función para Firmar Documentos
#                             Updated 03/06/25
# ——————————————————————————————————————————————————————————————————————————

import json
import logging
import azure.functions as func
from azure.functions.decorators.core import DataType
import datetime

import managePDF
import signPDF
import sqlQuery
import verifyPDF

from dotenv import load_dotenv
load_dotenv()


# —————————————————————————————————————————————————————————————————————————— 
#                               Algunos Paths
# ——————————————————————————————————————————————————————————————————————————

# Local Paths
path_raw_doc = "./docs/rawdoc.pdf"
signed_pdf_path = './docs/output.pdf'

key_path = './certs/signer.key'
cert_path = './certs/signer.crt'

# Path in Azure Blob Storage
signed_files_path = "docs-signed"


# —————————————————————————————————————————————————————————————————————————— 
#                   Inicializar función, inputs y outputs
# ——————————————————————————————————————————————————————————————————————————

app = func.FunctionApp()

@app.function_name(name="docSigner")

@app.sql_output(arg_name="nuevaFila",
                        command_text="[dbo].[docs_firmados]",
                        connection_string_setting="AzureWebJobsStorage")

@app.sql_trigger(arg_name="todo",
                        table_name="docs_firmados",
                        connection_string_setting="AzureWebJobsStorage")


# —————————————————————————————————————————————————————————————————————————— 
#                            Función Principal
# ——————————————————————————————————————————————————————————————————————————
def docSigner(todo: str, nuevaFila: func.Out[func.SqlRow]):
    changesFromSQL = json.loads(todo)
    logging.info("SQL Changes: %s", changesFromSQL)

    for change in changesFromSQL:

        # Si se creó una nueva fila de SQL y esa fila NO tiene path...
        if change["Operation"] == 0 and change["Item"]["path"] == None:
            # Obtener la información de la nueva fila de SQL
            row = change["Item"]

            # Comprobar que los datos de la fila estén completos:
            if row["documento_id"] == None or row["firmante_id"] == None or row["flujo_id"] == None:
                logging.error("ERROR: Los datos de la fila están incompletos.")
                return

            logging.info("Processing Documento ID " + str(row["documento_id"]) + "...")
            firmante_id = row["firmante_id"]
            flujo_id = row["flujo_id"]

            # Obtener la tupla de la entrada previa de ese flujo
            query_text = f"SELECT * FROM docs_firmados WHERE flujo_id = {flujo_id} AND siguiente_id = {firmante_id};"
            
            # Hacer la query para agarrar la fila anterior
            # !!!!!!!!!!! TOMA LA FILA MÁS RECIENTE QUE COINCIDA !!!!!!!!!!!!!!!!
            prev_row = sqlQuery.Query(query_text)
            if prev_row == None:
                logging.error("ERROR: No se encontraron resultados para la consulta en docs_firmados.")
                return
            prev_row = prev_row[-1]
            
            # La ruta de accceso es el último elemento de la tupla
            orig_rutaDeAcceso = prev_row[-1]
            if orig_rutaDeAcceso == None:
                logging.error("ERROR: No existe una ruta de acceso para el documento a firmar.")
                return



            # Obtener la llave y certificado para el usuario firmante...
            query_text = f"SELECT * FROM Usuarios WHERE usuario_id = {firmante_id};"
            datos_usuario = sqlQuery.Query(query_text)[0]
            if datos_usuario == None:
                logging.error("ERROR: No se encontraron resultados para la consulta en docs_firmados.")
                return
            
            usuario_nombre = datos_usuario[1]
            usuario_cert = datos_usuario[-2]
            usuario_key = datos_usuario[-3]
            # Comprobar que los datos estén completos
            if usuario_nombre == None or usuario_cert == None or usuario_key == None:
                logging.error("Los datos del usuario están incompletos en la tabla Usuarios.")
                return

            logging.info("Se recuperaron los datos del usuario " + str(usuario_nombre))

            try:
                # Guardar la key del usuario...
                with open(key_path, 'w') as f:
                    f.write(usuario_key)

                # Guardar el cert del usuario...
                with open(cert_path, 'w') as f:
                    f.write(usuario_cert)
            except:
                logging.error("No se pudieron guardar los certificados localmente.")
                return


            try:
                # Descargar el PDF...
                pdf_file = managePDF.download_pdf(orig_rutaDeAcceso)

                with open(path_raw_doc, 'wb') as file:
                    file.write(pdf_file.content)
                logging.info('Raw file downloaded successfully.')
            except:
                logging.error("No se pudo guardar el archivo crudo localmente.")
                return
            

            # SOLO SI NO SE ACABA DE SUBIR UN ARCHIVO NUEVO...
            # Si en el eslabón anterior el firmante y el siguiente eran el mismo id
            #logging.info(str(prev_row))
            if prev_row[3] != prev_row[4]:
                # Comprobar la firma del PDF descargado...
                last_sign_status, last_sign_name = verifyPDF.verify_pdf_signature(path_raw_doc)
                # Si la firma o es válida...
                if last_sign_status != True:
                    logging.warning("La firma del archivo recibido NO es válida. Se interrummpió el proceso de firmado.")
                    # Marcar el eslabón como inactivo
                    try:
                        new_row = func.SqlRow.from_dict(row)
                        new_row["activo"] = False
                        nuevaFila.set(new_row)
                        logging.info('El eslabón actual se marcó como inactivo.')
                    except:
                        logging.error("ERROR: Ocurrió un error al actualizar marcar el eslabón como inactivo.")
                        return
                    # Actualizar el estatus del flujo.
                    try:
                        # Marcar en la tabla de «flujos» que el flujo se corrompió (5)
                        query_text = f"UPDATE [dbo].[flujos] SET estatus_id = 5 WHERE flujo_id = {flujo_id}"
                        sqlQuery.Update(query_text)
                        fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
                        query_text = f"UPDATE [dbo].[flujos] SET fecha_final = '{fecha_hoy}' WHERE flujo_id = {flujo_id}"
                        sqlQuery.Update(query_text)
                        logging.info('El flujo actual se marcó como corrupto.')
                    except:
                        logging.error("ERROR: Ocurrio un error al actualizar el estatus del flujo (Corrompido).")
                    return




            # Definir el nombre del archivo firmado
            new_name = orig_rutaDeAcceso.split("/")[-1][:-4] + f"_{firmante_id}.pdf"

            signPDF.sign_pdf(path_raw_doc, signed_pdf_path, key_path, cert_path)
            #signPDF.sign_pdf(path_raw_doc, signed_pdf_path, usuario_key, usuario_cert)
            logging.info('Raw file signed successfully.')
            managePDF.upload_pdf(signed_pdf_path, new_name, signed_files_path)
            logging.info('Signed file uploaded successfully.')


            # Agregar nueva fila
            try:
                new_row = func.SqlRow.from_dict(row)
                new_row["path"] = signed_files_path + "/" + new_name
                if row["siguiente_id"] == None:
                    new_row["activo"] = False
                    logging.info("Se marcó el último eslabón como inactivo.")
                nuevaFila.set(new_row)
                logging.info('Path updated successfully.')
            except:
                logging.error("ERROR: Ocurrió un error al actualizar el path del documento firmado.")
                return


            # Si el flujo ya se completó...
            if row["siguiente_id"] == None:
                logging.info("Se ha completado el flujo.")
                try:
                    # Marcar en la tabla de «flujos» que el flujo ya se completó (3)
                    query_text = f"UPDATE [dbo].[flujos] SET estatus_id = 3 WHERE flujo_id = {flujo_id}"
                    sqlQuery.Update(query_text)
                    fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
                    query_text = f"UPDATE [dbo].[flujos] SET fecha_final = '{fecha_hoy}' WHERE flujo_id = {flujo_id}"
                    sqlQuery.Update(query_text)
                    logging.info("El flujo se marcó exitosamente como completo.")
                except:
                    logging.error("ERROR: No se pudo actualizar el estatus del flujo (Commpletado).")
                    return

        else:
            logging.info("Esta fila no debe ser atendida por esta función.")