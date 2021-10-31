import calendar
import statistics
from datetime import datetime, timedelta

from pandas import read_excel

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

SALARIO = 950.0
PENSION = 609.9
DESEMPLEO = 451.92

cobrado = False

# Load data using read_excel
transacciones_nomina_df = read_excel('20210513 mmelero (249236).xlsx', sheet_name='Hoja1')

# nos quedamos con transacciones desde 'Fecha transacción' hasta 'ID Categoría'
transacciones_nomina_df = transacciones_nomina_df.iloc[:, 0:3]

"""
nos quedamos con las transacciones que cumplan las siguientes condiciones:
(18.0) retribucion_liquida_18 >= SALARIO (950.0) eur OR
(588.0) Prestación de Seguridad Social >= PENSION (609.9) eur OR
(589.0) Prestación de desempleo >= DESEMPLEO (451.92) eur
"""
transacciones_nomina_df = \
    transacciones_nomina_df[
        (transacciones_nomina_df['ID Categoría'] == 18.0) & (transacciones_nomina_df['Importe'] >= SALARIO) |
        (transacciones_nomina_df['ID Categoría'] == 588.0) & (transacciones_nomina_df['Importe'] >= PENSION) |
        (transacciones_nomina_df['ID Categoría'] == 589.0) & (transacciones_nomina_df['Importe'] >= DESEMPLEO)]

# borramos la columna de 'ID Categoría'
transacciones_nomina_df = transacciones_nomina_df.drop(['ID Categoría'], axis=1)

# ordenamos las filas del dataframe por fechas en orden ascendente
transacciones_nomina_df.sort_values(by='Fecha transacción', inplace=True)

# renombramos columnas
transacciones_nomina_df.columns = ['FECHA', 'IMPORTE']

# agrupamos los valores por FECHA para quitarnos los duplicados
transacciones_nomina_df = transacciones_nomina_df.groupby(transacciones_nomina_df.FECHA).sum()

# hacemos un dataframe con el dia que pagaron la nomina para ver en que dias se cobra mas frecuentemente la misma

# hacemos una columna con la fecha a partir del índice
transacciones_nomina_df['FECHA'] = transacciones_nomina_df.index

# hacemos una columna con el dia a partir de la columna de la fecha
transacciones_nomina_df['DIA'] = transacciones_nomina_df['FECHA'].dt.day

# calculamos la moda
stat_mode = statistics.mode(transacciones_nomina_df['DIA'])

# extraemos el 1er cuartil
quartil1_dist = int(transacciones_nomina_df.describe().loc['25%']['DIA'])

# extraemos el 3er cuartil
quartil3_dist = int(transacciones_nomina_df.describe().loc['75%']['DIA'])

iqr_dist = quartil3_dist - quartil1_dist

# si NO cobramos a FIN DE MES
if stat_mode < 28:
    iqr = iqr_dist
# si SÍ cobramos a FIN DE MES
else:
    # si quartil3_dist - quartil1_dist es mayor a 4 dias
    if iqr_dist > 4:
        iqr = 4
    else:
        iqr = iqr_dist

# pedimos al usuario la fecha (en producción tomamos la fecha del sistema)
year = input('year: ')
month = input('month: ')
day = input('day: ')

# pasamos la fecha a string
current_date_str = year + '-' + month + '-' + day

current_date_obj = datetime.strptime(current_date_str, '%Y-%m-%d')

# pasamos iqr a formato datetime
iqr_obj = timedelta(days=iqr)

# calculamos quartil3_obj en función de current_date_obj, quartil3_dist y si cobramos a FIN de MES o NO

# si SÍ cobramos a FIN de MES
if stat_mode >= 28:
    # quartil3_obj sera el ultimo dia del mes de current_date_obj
    quartil3 = calendar.monthrange(current_date_obj.year, current_date_obj.month)[1]
    quartil3_str = str(current_date_obj.year) + '-' + str(current_date_obj.month) + '-' + str(quartil3)
# si NO cobramos a FIN de MES
else:
    quartil3_str = str(current_date_obj.year) + '-' + str(current_date_obj.month) + '-' + str(quartil3_dist)

q3_obj = datetime.strptime(quartil3_str, '%Y-%m-%d')

q1_obj = q3_obj - iqr_obj

limInf_obj = q1_obj - 1.5 * iqr_obj
# quitamos partes de dias no enteros que haya podido introducir 1.5*iqr_obj
limInf_obj = limInf_obj.replace(hour=0, minute=0, second=0, microsecond=0)

# calculamos limite superior de barrido según cobremos a fin de mes o no
limSup_obj = q3_obj + timedelta(days=1)

for d in range(int((limSup_obj - limInf_obj).days)):
    # ESTA LINEA NO SE EJECUTA EN PRODUCCIÓN
    # fecha_str = str((limInf_obj + timedelta(d)).year) + '-' + str((limInf_obj + timedelta(d)).month) + '-' + \
    #            str((limInf_obj + timedelta(days=d)).day)
    # ESTA LINEA NO SE EJECUTA EN PRODUCCIÓN
    # print(fecha_str)
    if (limInf_obj + timedelta(days=d)) in transacciones_nomina_df.index:
        cobrado = True
        print('El usuario cobró una nómina de ' +
              str(transacciones_nomina_df['IMPORTE'][str(limInf_obj + timedelta(days=d))[:10]]) +
              ' eur el día ' + str(limInf_obj + timedelta(d))[:10])
if not cobrado:
    fecha_obj = limSup_obj - timedelta(days=1)
    fecha = str(fecha_obj.year) + '-' + str(fecha_obj.month) + '-' + str(fecha_obj.day)
    print(fecha + ': El usuario aún no ha cobrado la nómina. Hay que avisarle')

# if para decidir si genero aviso
if not cobrado and current_date_obj == q3_obj:
    aviso = True
else:
    aviso = False

print('Aviso: ' + str(aviso))
