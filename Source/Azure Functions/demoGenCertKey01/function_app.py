# —————————————————————————————————————————————————————————————————————————— 
#                   Función para Generar Llaves y Certificados
#                             Updated 03/06/25
# ——————————————————————————————————————————————————————————————————————————

import json
import logging
import azure.functions as func
from azure.functions.decorators.core import DataType

import issueUser


# —————————————————————————————————————————————————————————————————————————— 
#                Inicializar función, entradas y salidas
# ——————————————————————————————————————————————————————————————————————————

app = func.FunctionApp()

@app.function_name(name="keyCertGen")

@app.sql_output(arg_name="nuevaFila",
                        command_text="[dbo].[usuarios]",
                        connection_string_setting="AzureWebJobsStorage")

@app.sql_trigger(arg_name="todo",
                        table_name="usuarios",
                        connection_string_setting="AzureWebJobsStorage")


# —————————————————————————————————————————————————————————————————————————— 
#                           Función Principal
# ——————————————————————————————————————————————————————————————————————————

def keyCertGen(todo: str, nuevaFila: func.Out[func.SqlRow]):
    changesFromSQL = json.loads(todo)
    logging.info("SQL Changes: %s", changesFromSQL)

    for change in changesFromSQL:

        # Si se creó una nueva fila en SQL...
        if change["Operation"] == 0:

            # Obtener la información de la nueva fila de SQL
            row = change["Item"]
            if row == None:
                logging.error("ERROR: No existe información sobre la fila en el trigger.")
                return
            
            if row["usuario_id"] == None or row["nombre"] == None or \
                row["apellido_paterno"] == None or row["apellido_materno"] == None or \
                row["correo_electronico"] == None:
                logging.error("ERROR: Los datos del usuario nuevo no están completos.")
                return

            logging.info("Processing " + str(row["usuario_id"]) + " - " + str(row["nombre"]) + "...")

            user_username = row["nombre"] + " " + row["apellido_paterno"] + " " + row["apellido_materno"]
            user_email = row["correo_electronico"]

            try:
                str_user_cert, str_user_key = issueUser.issue_user_cert(user_username, user_email)
            except:
                logging.error("ERROR: Los nuevos certificados no pudieron generarse.")
                return            
            
            if str_user_cert == None or str_user_key == None:
                logging.error("ERROR: La llave o certificado generado no son válidos.")

            # Agregar nueva fila
            new_row = func.SqlRow.from_dict(row)
            new_row["key"] = str_user_key
            new_row["cert"] = str_user_cert

            nuevaFila.set(new_row)
            logging.info('Llave y certificado generados y actualizados exitosamente.')
        
        else:
            logging.info("El trigger recibido no es una nueva fila.")