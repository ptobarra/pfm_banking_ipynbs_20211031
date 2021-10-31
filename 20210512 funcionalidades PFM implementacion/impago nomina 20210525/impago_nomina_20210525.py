from datetime import datetime, timedelta
from pandas import read_excel

"""
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
"""

# preguntamos al usuario por la fecha actual. En produccion cogeremos la fecha del sistema.
print()
current_year_str = input("Por favor, introduce el año actual YYYY: ")
current_month_str = input("Por favor, introduce el mes actual MM (01-12): ")
current_day_str = input("Por favor, introduce el dia de hoy DD (01-31): ")
print()

current_date_str = current_year_str + '-' + current_month_str + '-' + current_day_str

current_date_obj = datetime.strptime(current_date_str, '%Y-%m-%d')

# Load data using read_excel
transacciones_nomina_df = read_excel('20210513 mmelero (249236).xlsx', sheet_name='Hoja1')

# nos quedamos con transacciones desde 'Fecha transacción' hasta 'ID Categoría'
transacciones_nomina_df = transacciones_nomina_df.iloc[:, 0:3]

# nos quedamos con las transacciones de categoria 18
transacciones_nomina_df = transacciones_nomina_df[transacciones_nomina_df['ID Categoría'] == 18.0]

# borramos la columna de 'ID Categoría'
transacciones_nomina_df = transacciones_nomina_df.drop(['ID Categoría'], axis=1)

# nos quedamos con las transacciones mayores o iguales a 950 eur
transacciones_nomina_df = transacciones_nomina_df[transacciones_nomina_df['Importe'] >= 950.0]

# ordenamos las filas del dataframe por fechas en orden ascendente
transacciones_nomina_df.sort_values(by='Fecha transacción', inplace=True)

# renombramos columnas
transacciones_nomina_df.columns = ['FECHA', 'IMPORTE']

# agrupamos los valores por FECHA para quitarnos los duplicados
transacciones_nomina_df = transacciones_nomina_df.groupby(transacciones_nomina_df.FECHA).sum()

# hacemos un dataframe con el dia que pagaron la nomina para ver en que dias se cobra mas frecuentemente la misma
transacciones_nomina_df['FECHA'] = transacciones_nomina_df.index

transacciones_nomina_df['DIA'] = transacciones_nomina_df['FECHA'].dt.day

# hacemos un drop de FECHA para quedarnos solo con DIA
transacciones_nomina_df = transacciones_nomina_df.drop(columns=['FECHA'])

# extraemos el 1er cuartil
quartil1 = transacciones_nomina_df.describe().loc['25%']['DIA']

# extraemos el 3er cuartil
quartil3 = transacciones_nomina_df.describe().loc['75%']['DIA']

# pasamos a formato fecha q1 y q3 de acuerdo al año y mes que estamos mirando
q3_date_str = str(current_date_obj.year) + '-' + str(current_date_obj.month) + '-' + str(int(quartil3))
q3_date_obj = datetime.strptime(q3_date_str, '%Y-%m-%d')

# este bloque de codigo para q1_date_str sirve para tener en cuenta cuando q1_date_str esta en el mes anterior a
# q3_date_str o en el año y mes anterior a q3_date_str
if int(quartil1) <= int(quartil3):
    q1_date_str = str(current_date_obj.year) + '-' + str(current_date_obj.month) + '-' + str(int(quartil1))
else:
    if current_date_obj.month != 1:
        q1_date_str = str(current_date_obj.year) + '-' + str(current_date_obj.month - 1) + '-' + str(int(quartil1))
    else:
        q1_date_str = str(current_date_obj.year - 1) + '-' + str(current_date_obj.month - 1) + '-' + str(int(quartil1))

q1_date_obj = datetime.strptime(q1_date_str, '%Y-%m-%d')

# calculamos el rango intercuartilico para calcular el limite inferior de barrido como 'q1_date_obj - 1.5*iqr_obj'
iqr_obj = q3_date_obj - q1_date_obj
limInf_obj = q1_date_obj - 1.5 * iqr_obj
# quitamos partes de dias no enteros que haya podido introducir 1.5*iqr_obj
limInf_obj = limInf_obj.replace(hour=0, minute=0, second=0, microsecond=0)

# como haremos un range con los limites el limite superior será q3_date_obj - 1 dia
limSup_obj = q3_date_obj + timedelta(days=1)

# si q1 - 1.5*IQR <= q1 - 1.5*iqr <= current_date_obj <= q3 entonces que no compruebe si he cobrado
if current_date_obj >= limInf_obj and current_date_obj <= limSup_obj:
    print(current_date_str + ': Aún es pronto para avisar al usuario de que no ha cobrado la nómina.')
else:
    # booleano para saber si ha cobrado la nomina
    cobrado = False

    for d in range(int((limSup_obj - limInf_obj).days)):
        """
        # este snippet es solo para debugear y ver por pantalla que día barre
        fecha = str((limInf_obj + timedelta(d)).year) + '-' + str((limInf_obj + timedelta(d)).month) + '-' + \
        str((limInf_obj + timedelta(d)).day)
        print(fecha)
        """
        if (limInf_obj + timedelta(d)) in transacciones_nomina_df.index:
            cobrado = True
            print('El usuario cobró una nómina de ' +
                  str(transacciones_nomina_df['IMPORTE'][str(limInf_obj + timedelta(d))[:10]]) + ' eur el día ' +
                  str(limInf_obj + timedelta(d))[:10] + '. No se le genera aviso.')

    if not cobrado:
        fechaAvisoInf_str = str(limSup_obj.year) + '-' + str(limSup_obj.month) + '-' + str(limSup_obj.day)
        fechaAvisoSup_obj = limSup_obj + timedelta(days=4)
        fechaAvisoSup_str = str(fechaAvisoSup_obj.year) + '-' + str(fechaAvisoSup_obj.month) + '-' \
                            + str(fechaAvisoSup_obj.day)
        if current_date_obj >= limSup_obj and current_date_obj <= fechaAvisoSup_obj:
            print(fechaAvisoInf_str + ': El usuario aún no ha cobrado la nómina. Hay que avisarle!')
        else:
            print(current_date_str + ': El usuario aún no ha cobrado la nómina.')
            print('No hay que avisarle. Estamos fuera del intervalo: ' + fechaAvisoInf_str + ' / ' + fechaAvisoSup_str)
