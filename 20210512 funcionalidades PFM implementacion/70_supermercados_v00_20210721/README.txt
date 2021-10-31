Autor: Pedro Tobarra
Version: 00
Fecha: 2021-07-21

Descripción:
Este script toma una fecha introducida por el usuario (en producción tomará la fecha del sistema) y la predice el 
gasto en '70_supermercados' para el mes siguiente al de  la fecha de petición para las transacciones de una hoja excel 
formateada como '20210513 mmelero (249236).xlsx', 'Hoja1' (transacción con 'ID Categoría' == 70.0).
Se le genera aviso al usuario en caso que tenga gastos en esa categoría desde el día 1 del mes anterior al mes en que
hace la petición. 

Entorno de ejecución:
Python      3.8.10
pandas      1.2.4
fbprophet   0.7.1

Detalle de librerías y versiones del entorno de ejecución en el archivo 
'requirements_20210721_70_supermercados_ide.txt'.