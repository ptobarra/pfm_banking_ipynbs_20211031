Autor: Pedro Tobarra
Version: 00
Fecha: 2021-07-14

Descripción:
Este script toma una fecha introducida por el usuario (en producción tomará la fecha del sistema) y estima para el
mes siguiente a la fecha de petición el dia que le van a pasar el recibo mensual no periódico de la categoría 
'78_seguro' (a partir de las fechas de cobro de los 12 meses anteriores) y el importe del mismo (calculado con prophet 
y también a partir los importes de cobro de los 12 meses anteriores) para las transacciones de una hoja excel 
formateada como '20210513 mmelero (249236).xlsx', 'Hoja1' (transacción con 'ID Categoría'==78.0).
Se le genera aviso al usuario en caso que tenga recibos domiciliados por el mismo importe en los 12 meses anteriores a 
la fecha de petición y si la próxima fecha de cobro se encuentra en el mes siguiente a la fecha de petición. 

Entorno de ejecución:
Python      3.8.10
pandas      1.2.4
fbprophet   0.7.1
Detalle de librerías y versiones del entorno de ejecución en el archivo 
'requirements_20210714_78_seguro_vehiculo_ide.txt'.