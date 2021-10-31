"""
Autor: Pedro Tobarra
Version: 00
Fecha: 2021-06-07

Descripción:
Este script toma una fecha introducida por el usuario (En producción tomará la fecha del sistema) y comprueba si
para las transacciones de una hoja excel formateada como '20210513 mmelero (249236).xlsx' el usuario cobró
la nómina (transacción con 'ID Categoría'==18.0 e 'Importe'>=950.0)
o la pensión (transacción con 'ID Categoría'==588.0 e 'Importe'>=609.9)
o el paro (transacción con 'ID Categoría'==589.0 e 'Importe'>=451.92)
y con fecha dentro del tercer cuartil Q3 y del limite inferior 'Q1 - 1.5*IQR' de la distribución del dia del mes en que
el usuario cobró la nómina.
Se le genera aviso al usuario en caso que no haya cobrado la nómina y la fecha de comprobación  sea la misma que q3_obj.
Siendo q3_obj el último día del mes si el usuario cobra a fin de mes (moda <= 28) o el 3er cuartil de la distribución
quartil3_dist si el usuario no cobra a fin de mes.

Entorno de ejecución:
Python 3.8.10
pandas 1.2.4
Detalle de librerías del entorno de ejecución en archivo requirements_20210607.txt
"""