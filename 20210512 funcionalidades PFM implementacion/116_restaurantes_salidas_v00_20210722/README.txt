Autor: Pedro Tobarra
Version: 00
Fecha: 2021-07-21

Descripción: Este script toma una fecha introducida por el usuario (en producción tomará la fecha del sistema) y la 
predice el gasto en 'restaurantes_salidas_116' para el mes siguiente al de  la fecha de petición para las 
transacciones de una hoja excel formateada como '20210513 mmelero (249236).xlsx', 'Hoja1' (transacción con 'ID 
Categoría' == 116.0). Se le genera aviso al usuario en caso que tenga gastos en esa categoría desde el día 1 del mes 
anterior al mes en que hace la petición. 

Entorno de ejecución:
Python      3.8.10
pandas      1.2.4
fbprophet   0.7.1

Detalle de librerías y versiones del entorno de ejecución en el archivo 
'requirements.txt'.

El entorno a partir del fichero se carga con cualquiera de las dos siguientes instrucciones:
# using pip
pip install -r requirements.txt
# using Conda
conda create --name <env_name> --file requirements.txt

https://stackoverflow.com/questions/48787250/set-up-virtualenv-using-a-requirements-txt-generated-by-conda
https://developer.akamai.com/blog/2017/06/21/how-building-virtual-python-environment