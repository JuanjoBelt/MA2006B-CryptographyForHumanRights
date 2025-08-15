# Azure SQL Database

Mórfosis utiliza una gran cantidad de datos estructurados, tanto para la creación de rutas y flujos, como para la administración de usuarios y protocolos de seguridad. Debido a esto, fue necesario implementar un servidor y base de datos con tablas relacionales en Microsoft Azure, permitiendo una excelente integración con PowerApps.

Se muestra el diagrama de tablas relacionales de la base de datos:



La mayoría de las tablas y sus respectivas columnas son lo suficientemente autoexplicativas. No obstante, existen algunas tablas especiales cuyo funcionamiento se explica a continuación:

* **rutas_firmantes**: Esta tabla es una extensión de la tabla rutas, ya que en esta se especifica la secuencia de firmas de cada ruta, habiendo una fila para cada firma de cada ruta.
  
* **docs_firmados**: Esta tabla es útil para llevar los registros de cada una de las firmas que se realizan en cada flujo. Cuando un usuario firma un documento, Power Apps agrega una nueva fila en donde especifica qué usuario acaba de firmar y qué usuario es el siguiente en hacerlo (información que se obtenida de rutas\_firmantes), a la vez, Power Apps indica si la todas las firmas ya fueron realizadas o no en la variable booleana *activo*. Finalmente, la función **document_signer** agrega la ruta en BlobStorage del documento firmado en la variable *path*.

* **notificaciones**: Tabla cuya finalidad es llevar un registro de las notificaciones, al mismo tiempo que funciona como desencadenador para el flujo de Microsoft Automate encargado de entregar dichas notificaciones.
