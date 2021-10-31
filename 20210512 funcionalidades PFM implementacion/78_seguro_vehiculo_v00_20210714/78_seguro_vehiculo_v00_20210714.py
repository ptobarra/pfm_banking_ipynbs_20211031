from datetime import datetime, timedelta

import pandas
from dateutil.relativedelta import relativedelta
from fbprophet import Prophet
from pandas import read_excel, date_range, DatetimeIndex, DataFrame, to_numeric
from pandas.tseries.offsets import DateOffset

"""
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
numpy       1.19.5
Detalle de librerías y versiones del entorno de ejecución en el archivo 
'requirements_20210714_78_seguro_vehiculo_ide.txt'.
"""

# Load data using read_excel
transacciones_df = read_excel('20210513 mmelero (249236).xlsx', sheet_name='Hoja1')

# nos quedamos con la fecha en que nos dan los datos de las transacciones
last_date_tstamp = transacciones_df.loc[0, 'BALANCE_DATE']

# nos quedamos con las transacciones de la categoría 'seguro_vehiculo_78'
transacciones_78_df = transacciones_df[transacciones_df['ID Categoría'] == 78.0]
del transacciones_df

# nos quedamos con categoría desde 'Fecha transacción' hasta 'Nombre Categoría'
transacciones_78_df = transacciones_78_df.iloc[:, 0:4]

# quitamos las columnas de 'ID Categoría' y 'Nombre Categoría' que ya no nos aportan nada
transacciones_78_df.drop(columns=['ID Categoría', 'Nombre categoría'], inplace=True)

# renombramos columnas
transacciones_78_df.rename(columns={'Fecha transacción': 'FECHA', 'Importe': 'IMPORTE'}, inplace=True)

# ordenamos las fechas por orden ascendente
transacciones_78_df.sort_values(by=['FECHA'], ascending=True, inplace=True, ignore_index=True)

# vamos a agrupar los valores y sumarlos por fecha para agrupar cargos distintos realizados el mismo dia (por si acaso)
transacciones_78_df = transacciones_78_df.groupby(['FECHA']).sum()

# para que los datos sean más fáciles de interpretar vamos a hacerlos todos positivos multiplicándolos por '-1'
transacciones_78_df['IMPORTE'] = -transacciones_78_df['IMPORTE']

# EMPEZAMOS POR HACER EL DATAFRAME DE LOS IMPORTES
# vamos a rellenar las missing dates con el ultimo valor válido
transacciones_78_importe_df = transacciones_78_df.copy()

# hacemos una columna con la fecha del indice
transacciones_78_importe_df['FECHA'] = transacciones_78_importe_df.index
idx = date_range(start=transacciones_78_importe_df.FECHA.min(), end=transacciones_78_importe_df.FECHA.max())

# pasamos el indice de transacciones_78_importe_df a formato DatetimeIndex
transacciones_78_importe_df.index = DatetimeIndex(transacciones_78_importe_df.index)

# rellenamos las missing dates en el indice
transacciones_78_importe_df = transacciones_78_importe_df.reindex(idx, fill_value='NaN')

# hacemos drop de la columna FECHA
transacciones_78_importe_df.drop(columns='FECHA', inplace=True)

# pasamos IMPORTE a formato 'numeric'
transacciones_78_importe_ser = transacciones_78_importe_df.T.squeeze()
transacciones_78_importe_ser = to_numeric(transacciones_78_importe_ser, errors='coerce')
transacciones_78_importe_df = DataFrame(transacciones_78_importe_ser)
del transacciones_78_importe_ser

# rellenamos los NaN con el ultimo valor numérico anterior
transacciones_78_importe_df['IMPORTE'].fillna(method='ffill', inplace=True)

# HACEMOS EL DATAFRAME DEL IMPORTE DE LOS 3 AÑOS PASADOS
# para el dataframe del importe cogemos el ultimo año de datos y lo repetimos 3 veces hacia atrás
transacciones_78_importe_past_df = transacciones_78_importe_df.copy()

# hacemos una columna con la fecha a partir del índice
transacciones_78_importe_past_df['FECHA'] = transacciones_78_importe_past_df.index

# vamos a repetir el ultimo año 3 veces hacia atrás
end_date = transacciones_78_importe_past_df.FECHA.max()
start_date = end_date - relativedelta(years=1)

# hacemos una mascara con el ultimo año de transacciones
mask = \
    (transacciones_78_importe_past_df['FECHA'] > start_date) & (transacciones_78_importe_past_df['FECHA'] <= end_date)

# nos quedamos con el ultimo año de transacciones aplicando la mascara
transacciones_78_importe_plus0_df = transacciones_78_importe_past_df.loc[mask]

# hacemos el dataframe de 1 año atrás
transacciones_78_importe_minus1_df = transacciones_78_importe_plus0_df.copy()

# restamos 1 año en columna fecha
transacciones_78_importe_minus1_df['FECHA'] = transacciones_78_importe_plus0_df['FECHA'] - DateOffset(years=1)

# hacemos el dataframe de 2 años atrás
transacciones_78_importe_minus2_df = transacciones_78_importe_plus0_df.copy()

# restamos 2 años en columna fecha
transacciones_78_importe_minus2_df['FECHA'] = transacciones_78_importe_plus0_df['FECHA'] - DateOffset(years=2)

# reseteamos los indices de los 3 dataframes
transacciones_78_importe_plus0_df.reset_index(drop=True, inplace=True)
transacciones_78_importe_minus1_df.reset_index(drop=True, inplace=True)
transacciones_78_importe_minus2_df.reset_index(drop=True, inplace=True)

# a continuación concatenamos los 3 dataframes
transacciones_78_importe_minus2_df = \
    transacciones_78_importe_minus2_df.append(transacciones_78_importe_minus1_df, ignore_index=True)
transacciones_78_importe_minus2_df = \
    transacciones_78_importe_minus2_df.append(transacciones_78_importe_plus0_df, ignore_index=True)

del transacciones_78_importe_past_df
transacciones_78_importe_past_df = transacciones_78_importe_minus2_df.copy()

del transacciones_78_importe_minus2_df
del transacciones_78_importe_minus1_df
del transacciones_78_importe_plus0_df

# HACEMOS EL DATAFRAME DEL DIA DE PAGO DEL SEGURO DEL COCHE HASTA EL AÑO SIGUIENTE AL DE last_date_tstamp

# extendemos dataframe del dia de pago del seguro hasta 1 año después de la fecha de la ultima transacción en cuenta
target_year = 1 + last_date_tstamp.year

# hacemos la diferencia entre target_year y transacciones_78_df.iloc[-1]['FECHA'].year para saber cuantos
# años tenemos q extender el dataframe anterior
numberOf_future_years = target_year - transacciones_78_df.index[-1].year

# transacciones_78_forecast_df sera el dataframe donde guardaremos las futuras fechas de cobro (y las pasadas reales)
transacciones_78_forecast_df = transacciones_78_df.copy()

while numberOf_future_years > 0:
    # calculo el 1er y ultimo dia del ultimo año
    start_date_dtime = datetime(transacciones_78_forecast_df.index[-1].year, 1, 1)
    end_date_dtime = datetime(transacciones_78_forecast_df.index[-1].year, 12, 31)

    # construyo la condición para seleccionar las fechas entre el 1er y ultimo dia del ultimo año
    after_start_date = transacciones_78_forecast_df.index >= start_date_dtime
    before_end_date = transacciones_78_forecast_df.index <= end_date_dtime
    between_two_dates = after_start_date & before_end_date

    # construyo un dataframe solo con las fechas del ultimo año
    transacciones_78_nextYear_df = transacciones_78_forecast_df.loc[between_two_dates]

    # añadimos 1 año al indice
    transacciones_78_nextYear_df.index += pandas.offsets.DateOffset(years=1)

    # añadimos las filas de transacciones_78_nextYear_df a las de transacciones_78_forecast_df
    transacciones_78_forecast_df = transacciones_78_forecast_df.append(transacciones_78_nextYear_df)

    # decrementamos el contador de años futuros
    numberOf_future_years -= 1

    # borramos el dataframe q tiene solo las transacciones del ultimo año
    del transacciones_78_nextYear_df

# ESTIMAMOS CON PROPHET LA SERIE TEMPORAL DEL IMPORTE CON LOS DATOS DEL DATAFRAME # 'transacciones_78_importe_past_df'
# ya que con el dataframe 'transacciones_78_forecast_df' ya tenemos estimados el importe y las fechas de cobro mediante
# la 'cuenta de la vieja'

# vamos a hacer la serie hasta la fecha de la ultima fila de 'transacciones_78_forecast_df'
prophet_train_df = transacciones_78_importe_past_df.copy()

# Time Series Forecasting With Prophet in Python
# https://machinelearningmastery.com/time-series-forecasting-with-prophet-in-python/
# Fit Prophet Model

# reordenamos las columnas de prophet_train_df
prophet_train_df = prophet_train_df[['FECHA', 'IMPORTE']]

# prepare expected column names
prophet_train_df.columns = ['ds', 'y']

# define the model
model = Prophet()

# fit the model
model.fit(prophet_train_df)

# vamos a pedirle a prophet que haga la predicción para el rango de fechas de 'transacciones_78_forecast_df'
future_out_sample = transacciones_78_forecast_df.copy()

# hacemos una columna 'FECHA' con el indice
future_out_sample['FECHA'] = future_out_sample.index

# hacemos un drop de la columna 'IMPORTE'
future_out_sample.drop(columns='IMPORTE', inplace=True)

# calculamos el rango de fechas de la estimación
idx = date_range(start=future_out_sample.FECHA.min(), end=future_out_sample.FECHA.max())

# rehacemos el indice de future_out_sample de acuerdo a las fechas de idx
future_out_sample = future_out_sample.reindex(idx)

# hacemos una columna con el nuevo indice
future_out_sample.reset_index(drop=False, inplace=True)

# hacemos un drop de la columna 'FECHA'
future_out_sample.drop(columns='FECHA', inplace=True)

# renombramos la columna del dataframe a 'ds'
future_out_sample.columns = ['ds']

# use the model to make a forecast
forecast_df = model.predict(future_out_sample)

# CON LOS DATOS ANTERIORES VAMOS A HACER LA PARTE DEL ALGORITMO QUE HACE LAS PREDICCIONES

# pedimos la fecha al usuario (en producción tomamos la fecha del sistema o del excel de datos: 2020-07-26)
print()
year = input('year:\t')
month = input('month:\t')
day = input('day:\t')

# pasamos la fecha a string
system_date_str = year + '-' + month + '-' + day

# pasamos la fecha al formato datetime
system_date_obj = datetime.strptime(system_date_str, '%Y-%m-%d')

# en transacciones_78_forecast_df tenemos la fecha de los próximos recibos y su importe (proyectados del pasado)
# hasta 1 año después de la fecha del sistema

# en transacciones_78_df tenemos el histórico de la fecha de los recibos y su importe

# en forecast_df tenemos el importe de los próximos recibos estimada con prophet
# hasta 1 año después de la fecha del sistema

# hacemos un bucle desde la fecha del sistema; incrementándola hasta que encontremos la fecha del próximo recibo en el
# indice transacciones_78_forecast_df

# calculamos el rango de fechas del bucle for para buscar las fechas de los próximos recibos
idx = date_range(start=system_date_obj, end=transacciones_78_forecast_df.index.max())

# inicializamos la variable de la fecha del próximo recibo
next_bill_date_obj = system_date_obj

# buscamos la fecha del próximo recibo
for date_obj in idx:
    if date_obj in transacciones_78_forecast_df.index:
        next_bill_date_obj = date_obj
        break

# obtenemos el importe del recibo del dataframe transacciones_78_forecast_df para next_bill_date_obj
next_bill_amount = float(transacciones_78_forecast_df.loc[next_bill_date_obj, 'IMPORTE'])

# calcula el importe del recibo del dataframe forecast_df retrasando la fecha de petición unos días
# vamos a pedirle la estimación a prophet posponiendo la fecha de petición 11 días respecto a next_bill_date_obj
next_bill_fbp_date_obj = next_bill_date_obj + timedelta(days=11)
next_bill_fbp_amount = float(forecast_df.loc[forecast_df['ds'] == next_bill_fbp_date_obj]['yhat'])

# chequeamos si la fecha del próximo recibo está en el mes siguiente al de la petición para dar aviso
next_month_bool = False
if next_bill_date_obj.month - system_date_obj.month == 1:
    next_month_bool = True

# chequeamos si hay un recibo el mismo dia (+/- 3 dias) y cantidad next_bill_date_obj en transacciones_78_df y si la
# diferencia entre next_bill_date_obj y esta fecha encontrada es igual o menor a 1 año para dar la predicción como real
last_year_bool = False
if next_bill_amount in transacciones_78_df['IMPORTE'].tolist():
    last_bill_date_obj = max(transacciones_78_df.index[transacciones_78_df['IMPORTE'] == next_bill_amount].tolist())
    if abs(next_bill_date_obj.day - last_bill_date_obj.day) <= 3 & \
            next_bill_date_obj.year - last_bill_date_obj.year <= 1:
        last_year_bool = True

print()
print('Fecha sistema:\t\t\t\t\t\t\t\t\t', system_date_str)
next_bill_date_str = next_bill_date_obj.strftime('%Y-%m-%d')
print('Fecha próximo recibo:\t\t\t\t\t\t\t', next_bill_date_str)
last_bill_date_str = last_bill_date_obj.strftime('%Y-%m-%d')
print('Fecha último recibo equivalente (mismo importe):', last_bill_date_str)
print()
print('Importe próximo recibo (proyectado):\t\t\t', int(next_bill_amount), 'eur')
print('Importe próximo recibo (fprophet delay 11 dias):', int(next_bill_fbp_amount), 'eur')
print()
print('Aviso recibo real (anterior en último año):\t', last_year_bool)
print('Aviso recibo mes siguiente:\t\t\t\t\t', next_month_bool)
print('Aviso definitivo recibo mes siguiente\t\t', last_year_bool & next_month_bool)
print()
print(
    'NB(1): La estimación con fbprophet puede ser errónea si hay dos recibos distintos dentro del intervalo del delay.')
print('NB(2): El delay de la estimación con fbprophet puede dar mayor error con datos con mayor variación de importes.')
print('NB(3): Mejor coger el importe proyectado que es más preciso que el de fbprophet.')
