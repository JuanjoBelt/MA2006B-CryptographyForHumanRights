# Power Apps

A continuación se muestra la metodología utilizada para los procesos fundamentales de la aplicación. La aplicación puede ser descargada como paquete [aquí.](<Power App Source/Morfosis1.0.msapp>)

* **Firmas Pendientes (Página de Inicio)**: Esta sección muestra todos los flujos en donde el siguiente firmante sea el usuario en uso.
* **Flujos en Proceso (Página de Inicio):** Esta sección muestra todos los flujos activos creados por el usuario en uso.
* **Historial (Página de Historial de Firmas):** Esta página muestra todos los flujos no activos en donde el usuario en uso haya firmado.
* **Crear Flujo (Página de Nuevo Flujo):** Este botón sube al contenedor de Azure el documento sin firmas, agrega el nuevo flujo y documento a sus tablas correspondientes en la base de datos y agrega dos filas a la tabla *docs_firmados*: en la primera asigna al usuario en uso como el siguiente en firmar y añade la ruta hacia el documento en BlobStorage, mientras que en la segunda asigna al siguiente en la ruta como el siguiente a firmar. La función **document_signer** firma el documento y lo vuelve a añadir al contendor, agregando también la ruta en la segundo fila agregada.
* **Crear Ruta (Página de Nueva Ruta)**: Este botón añade la nueva ruta a la tabla *rutas* y agrega los firmantes en orden a *rutas_firmantes*.
* **Descargar (Página de Firmar Documento y Visualizar Documento)**: Accede al link con el documento perteneciente al flujo a firmar y que se encuentra activo en *docs_firmados*.
* **Firmar Documento (Página de Firmar Documento)**: Cambia el valor de "Activo" a falso de la última fila y agrega una nueva fila a *docs_firmados* con la ruta del documento que se acaba de firmar y el id del usuario que sigue por firmar, siendo este obtenido de *rutas_firmantes*. Al agregar esta última fila, se activa la función **document_signer**, la cual, con los datos de la fila, firma de nuevo el documento, lo sube al contenedor y agregar la ruta a *docs_firmados*.
* **Rechazar Documento (Página de Firmar Documento)**: Cambia la fila en donde el flujo está activo de *docs_firmados* a falso, cambia el estatus del flujo en *flujos* y agrega una nueva notificación de tipo rechazo en *notifiaciones*.
