import json
import logging
import azure.functions as func
from azure.functions.decorators.core import DataType

import issueUser






app = func.FunctionApp()

@app.function_name(name="keyCertGen")

@app.sql_output(arg_name="nuevaFila",
                        command_text="[dbo].[Usuarios]",
                        connection_string_setting="AzureWebJobsStorage")

@app.sql_trigger(arg_name="todo",
                        table_name="Usuarios",
                        connection_string_setting="AzureWebJobsStorage")

def keyCertGen(todo: str, nuevaFila: func.Out[func.SqlRow]):
    changesFromSQL = json.loads(todo)
    logging.info("SQL Changes: %s", changesFromSQL)

    for change in changesFromSQL:

        # Si se creó una nueva fila en SQL...
        if change["Operation"] == 0:
            # Obtener la información de la nueva fila de SQL
            row = change["Item"]

            logging.info("Processing " + str(row["usuario_id"]) + " - " + str(row["nombre"]) + "...")

            user_username = row["nombre"] + " " + row["apellido_paterno"] + " " + row["apellido_materno"]
            user_email = row["correo_electronico"]

            str_user_cert, str_user_key = issueUser.issue_user_cert(user_username,
                                                                    user_email)
            

            # Agregar nueva fila
            new_row = func.SqlRow.from_dict(row)
            new_row["key"] = str_user_key
            new_row["cert"] = str_user_cert

            nuevaFila.set(new_row)
            logging.info('Key and certificate generated succesfully.')