impago_nomina_20210525.py

Autor: Pedro Tobarra
Version: 00
Fecha: 2021-05-25

Descripcion:
Este script toma una fecha introducida por el usuario (En producción tomará la fecha del sistema) y comprueba si
para las transacciones de una hoja excel formateada como '20210513 mmelero (249236).xlsx' el usuario cobró la 
nómina (transacción con 'ID Categoría'==18.0 e 'Importe'>=950.0) y con fecha dentro del tercer cuartil Q3 y del limite
inferior 'Q1 - 1.5*IQR' de la distribucion del dia del mes en que el usuario cobró la nómina.
Se le genera aviso al usuario en caso que no haya cobrado la nómina y la fecha de comprobación  se encuentre en el
intervalo [q3 + 1, q3 + 5]

Entorno de ejecución:
Python 3.8.10
pandas 1.2.4
