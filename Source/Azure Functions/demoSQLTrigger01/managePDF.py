# —————————————————————————————————————————————————————————————————————————— 
#            Módulo para Descargar y Subir Archivos a Blob Storage
#                             Updated 03/06/25
# ——————————————————————————————————————————————————————————————————————————

from datetime import datetime, timedelta, timezone
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import requests
import os
from dotenv import load_dotenv
load_dotenv()


def download_pdf(file_path): #Output: Variable tipo PDF
    # Split path into container & file name
    file_path = file_path.split("/")
    container_name = file_path[-2]
    file_name = file_path[-1]
    #print(container_name)
    #print(file_name)

    #Ingresas credenciales
    account_name = os.getenv("BLOB_ACCOUNT_NAME")
    account_key = os.getenv("BLOB_ACCOUNT_KEY")
    #container_name = 'documentos'

    #Crear un cliente para interactuar con Blob Storage
    connect_str = 'DefaultEndpointsProtocol=https;AccountName=' + account_name + ';AccountKey=' + account_key + ';EndpointSuffix=core.windows.net'
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    #Usar el cliente para conectarse al contenedor
    container_client = blob_service_client.get_container_client(container_name)

    #Generar URL por tiempo limitado
    url = generate_blob_sas(account_name = account_name,
                                container_name = container_name,
                                blob_name = file_name,
                                account_key=account_key,
                                permission=BlobSasPermissions(read=True),
                                expiry= datetime.now(timezone.utc) + timedelta(hours=10))
    sas_url = 'https://' + account_name+'.blob.core.windows.net/' + container_name + '/' + file_name + '?' + url

    #Almacenar el archivo en una variable
    pdf_file = requests.get(sas_url)
    print('URL:', sas_url)

    return(pdf_file)




def upload_pdf(file_path, new_name, container_name):
    local_dir = file_path

    # set client to access azure storage container
    #Ingresas credenciales
    account_name = os.getenv("BLOB_ACCOUNT_NAME")
    account_key = os.getenv("BLOB_ACCOUNT_KEY")
    #container_name = 'documentos'

    #Crear un cliente para interactuar con Blob Storage
    connect_str = 'DefaultEndpointsProtocol=https;AccountName=' + account_name + ';AccountKey=' + account_key + ';EndpointSuffix=core.windows.net'
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # get the container client 
    container_client = blob_service_client.get_container_client(container=container_name)
    
    with open(local_dir, "rb") as fl :
        data = fl.read()
        container_client.upload_blob(name = new_name, data = data,  overwrite=True)