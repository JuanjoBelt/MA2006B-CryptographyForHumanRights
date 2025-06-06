# —————————————————————————————————————————————————————————————————————————— 
#                         Módulo para Consultar SQL
#                             Updated 03/06/25
# ——————————————————————————————————————————————————————————————————————————

import pyodbc
import logging
import os
from dotenv import load_dotenv
load_dotenv()

# Detalles de la base de datos
server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
username = os.getenv("SQL_USERNAME")
password = os.getenv("SQL_PASSWORD")
driver = os.getenv("SQL_DRIVER")

#logging.info(f"SQL Credentials: {server}, {database}, {username}, {password}, {driver}")

try:
    #Crear la conexión
    connection = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    #Acceder a la base
    cursor = connection.cursor()
except:
    logging.error("ERROR: Ocurrió un error al establecer conexión con la base de datos.")

# —————————————————————————————————————————————————————————————————————————— 
#                            Hacer una Consulta
# ——————————————————————————————————————————————————————————————————————————
def Query(query):
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except:
        logging.error("ERROR: Ocurrió un error al realizar la consulta.")
        return
    
# —————————————————————————————————————————————————————————————————————————— 
#                           Actualizar una tabla
# ——————————————————————————————————————————————————————————————————————————
def Update(query):
    try:
        cursor.execute(query)
        connection.commit()
        return
    except:
        logging.error("ERROR: Ocurrió un error al actualizar la tabla.")
        return
    

def turnOff():
    #Cerrar el cursor y la conexión
    cursor.close()
    connection.close()