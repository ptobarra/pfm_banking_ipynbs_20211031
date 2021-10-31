Autor: Pedro Tobarra
Version: 00
Fecha: 2021-06-28

Descripción:
Este script toma una fecha introducida por el usuario (en producción tomará la fecha del sistema) y estima para el
mes siguiente a la fecha de petición el dia que le van a pasar el recibo (moda de la distribución del dia de pago)
y el importe del mismo (calculado con prophet para el dia de la moda del mes siguiente a la fecha de petición)
para las transacciones de una hoja excel formateada como '20210513 mmelero (249236).xlsx' (transacción con 
'ID Categoría'==219.0).
Se le genera aviso al usuario en caso que tenga recibos domiciliados en los dos meses anteriores a la fecha de petición. 

Entorno de ejecución:
Python 3.8.10
pandas 1.2.4
fbprophet 0.7.1
Detalle de librerías y versiones del entorno de ejecución en el archivo 
'requirements_20210625_219_gas_natural_prophet_ide.txt'.