import datetime

import pandas
from fbprophet import Prophet
from pandas import read_excel, date_range, DataFrame, to_numeric
from pandas.tseries.offsets import DateOffset, MonthEnd, MonthBegin

"""
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
"""

# vamos a crear una serie temporal agrupando el gasto por meses

# Load data using read_excel
transacciones_df = read_excel('20210513 mmelero (249236).xlsx', sheet_name='Hoja1')

# nos quedamos con la fecha en que nos dan los datos de las transacciones
last_date_obj = transacciones_df.loc[0, 'BALANCE_DATE']

# nos quedamos con las transacciones de la categoría 'restaurantes_salidas_116'
transacciones_restaurantes_df = transacciones_df[transacciones_df['ID Categoría'] == 116.0]

# nos quedamos con columnas desde 'Fecha transacción' hasta 'Importe'
transacciones_restaurantes_df = transacciones_restaurantes_df.iloc[:, 0:2]

# ya no necesitamos transacciones_df
del transacciones_df

# renombramos columnas
transacciones_restaurantes_df.rename(columns={'Fecha transacción': 'FECHA', 'Importe': 'IMPORTE'}, inplace=True)

# ordenamos las fechas por orden ascendente
transacciones_restaurantes_df.sort_values(by=['FECHA'], ascending=True, inplace=True, ignore_index=True)

# vamos a agrupar los valores y sumarlos por fecha
transacciones_restaurantes_df = transacciones_restaurantes_df.groupby(['FECHA']).sum()

# hacemos una columna con el indice
transacciones_restaurantes_df['FECHA'] = transacciones_restaurantes_df.index

# sumamos la cuantía de las transacciones de cada mes y la suma la ponemos fecha del inicio de cada mes
transacciones_month_df = transacciones_restaurantes_df.groupby(pandas.Grouper(key='FECHA', freq="MS")).sum()

# ya no necesitamos transacciones_restaurantes_df
del transacciones_restaurantes_df

# para que los datos sean más fáciles de interpretar vamos a hacerlos todos positivos multiplicándolos por '-1'
transacciones_month_df['IMPORTE'] = -transacciones_month_df['IMPORTE']

# en transacciones_mfilled_df rellenaremos las fechas sin importe con el importe valido inmediatamente anterior
transacciones_mfilled_df = transacciones_month_df.copy()

# ya no necesitamos transacciones_month_df
del transacciones_month_df

# hacemos una columna con la fecha del indice
transacciones_mfilled_df['FECHA'] = transacciones_mfilled_df.index

# indice de fechas hasta el ultimo dia del mes para el cual hay datos
idx = date_range(start=transacciones_mfilled_df.FECHA.min(), end=transacciones_mfilled_df.FECHA.max() + MonthEnd(1))

# rellenamos las missing dates en el indice
transacciones_mfilled_df = transacciones_mfilled_df.reindex(idx, fill_value='NaN')

# hacemos drop de la columna FECHA
transacciones_mfilled_df.drop(columns='FECHA', inplace=True)

# pasamos IMPORTE a formato 'numeric'
transacciones_mfilled_ser = transacciones_mfilled_df.T.squeeze()

transacciones_mfilled_ser = to_numeric(transacciones_mfilled_ser, errors='coerce')

transacciones_mfilled_df = DataFrame(transacciones_mfilled_ser)
del transacciones_mfilled_ser

# rellenamos los NaN con el ultimo valor numérico anterior
transacciones_mfilled_df['IMPORTE'].fillna(method='ffill', inplace=True)

# a continuación vamos a estimar con prophet la serie temporal del importe con los datos del dataframe
# 'transacciones_mfilled_df'
# vamos a entrenar la serie desde el segundo mes de transacciones_mfilled_df hasta el penúltimo mes de
# transacciones_mfilled_df porque para el primer y ultimo mes de datos en ocasiones no se dispondrá del mes completo
# con lo que tenemos valores inferiores de IMPORTE para esos meses que distorsionan el calculo de la serie temporal

prophet_train_df = transacciones_mfilled_df.copy()

# Time Series Forecasting With Prophet in Python
# https://machinelearningmastery.com/time-series-forecasting-with-prophet-in-python/

# Fit Prophet Model

# para los datos de training tenemos que quitar los datos del mes en el que pedimos la estimación.
# ya que si hacemos la estimación al principio del mes el gasto en supermercados sera mucho menor respecto al gasto
# en supermercados de un mes completo similar

# hacemos una columna con el indice que se llame fecha
prophet_train_df['FECHA'] = prophet_train_df.index

# calculamos el ultimo año
last_year = prophet_train_df['FECHA'].dt.year.max()

# calculamos el ultimo mes del ultimo año
last_month = prophet_train_df[str(last_year)]['FECHA'].dt.month.max()

# hacemos un string con el ultimo año y mes para hacer una mascara
last_year_month = str(last_year) + '-' + str(last_month)

# calculamos la fecha maxima para quitarnos las transacciones en fecha iguales o posterior a esta
maximum_date_obj = prophet_train_df[last_year_month]['FECHA'].min()

# hacemos una mascara para quitar las filas del ultimo mes
before_maximum_date_ser = prophet_train_df['FECHA'] < maximum_date_obj

# aplicamos la mascara
prophet_train_df = prophet_train_df.loc[before_maximum_date_ser]

# también tenemos que quitar del dataframe los datos del primer mes porque también puede estar no completo y nos
# desvirtúa también la serie temporal del entrenamiento

# calculamos el primer año del dataframe
first_year = prophet_train_df['FECHA'].dt.year.min()

# calculamos el primer mes del primer año
first_month = prophet_train_df[str(first_year)]['FECHA'].dt.month.min()

# hacemos un string con el primer mes del primer año para hacer una mascara
first_year_month = str(first_year) + '-' + str(first_month)

# calculamos la fecha minima para quedarnos con todas las transacciones del dataframe posteriores a esa fecha
minimum_date_obj = prophet_train_df[first_year_month]['FECHA'].max()

# hago una mascara para quitar las filas del primer mes
after_minimum_date_ser = prophet_train_df['FECHA'] > minimum_date_obj

# aplicamos la mascara anterior
prophet_train_df = prophet_train_df.loc[after_minimum_date_ser]

# reordenamos las columnas de prophet_train_df
prophet_train_df = prophet_train_df[['FECHA', 'IMPORTE']]

# prepare expected column names
prophet_train_df.columns = ['ds', 'y']

# reseteamos el indice del dataframe
prophet_train_df.reset_index(drop=True, inplace=True)

# define the model
model = Prophet()

# fit the model
model.fit(prophet_train_df)

# vamos a pedirle a prophet que haga la predicción hasta el ultimo dia del mes siguiente al de 'last_date_obj'
future_out_sample = transacciones_mfilled_df.copy()

# hacemos una columna 'FECHA' con el indice
future_out_sample['FECHA'] = future_out_sample.index

# hacemos un drop de la columna 'IMPORTE'
future_out_sample.drop(columns='IMPORTE', inplace=True)

# calculamos la fecha del ultimo dia
target_date_obj = last_date_obj + DateOffset(months=1) + MonthEnd(1)

# calculamos el rango de fechas de la estimación
idx = date_range(start=prophet_train_df.ds.min(), end=target_date_obj)

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

# nos quedamos con las columnas 'ds' y 'yhat'
forecast_df = forecast_df[['ds', 'yhat']]

# nos quedamos con las filas del ultimo mes que es para el que hemos hecho la predicción
# calculamos el ultimo año
last_year = forecast_df['ds'].dt.year.max()

# calculamos el ultimo mes del ultimo año creándonos un dataframe donde al final tendremos la estimación del ultimo mes
prediction_df = forecast_df.copy()

# rehacemos el indice con la FECHA columna 'ds'
prediction_df.set_index('ds', drop=False, inplace=True)

# calculamos el ultimo mes del ultimo año
last_month = prediction_df[str(last_year)]['ds'].dt.month.max()

# hago una variable str con el ultimo año y el ultimo mes
last_year_month = str(last_year) + '-' + str(last_month)

# calculo la fecha minima a partir de la cual me quedo con los datos
minimum_date_obj = prediction_df[last_year_month]['ds'].min()

# hago una mascara para quedarme con las filas del ultimo año y del ultimo mes
after_minimum_date_ser = prediction_df['ds'] >= minimum_date_obj

# aplico la mascara para quedarme finalmente con las filas de las transacciones del ultimo mes y del ultimo año
prediction_df = prediction_df.loc[after_minimum_date_ser]

# hacemos un drop de la columna con las fechas
prediction_df.drop(columns='ds', inplace=True)

# damos la predicción final como la media de valores predichos para el mes
final_prediction = float(prediction_df.mean())

# a continuación comprobamos que la media de transacciones en restaurantes desde el dia 1 del mes anterior es mayor
# que 0 para poder dar la predicción como valida

# calculamos la fecha del primer dia del mes anterior a la petición
target_date_obj = last_date_obj - DateOffset(months=1) - MonthBegin(1)

# hago una mascara para solo quedarme con las filas del dataframe a partir de target_date_obj
after_target_date_ser = transacciones_mfilled_df.index >= target_date_obj

# aplico la mascara
final_mean_df = transacciones_mfilled_df.loc[after_target_date_ser]

# calculo la media final desde el dia 1 del mes anterior a la petición
final_mean = float(final_mean_df.mean())

# hago el chequeo final de que la predicción sea valida
valid_prediction = False

if final_mean != 0:
    valid_prediction = True
elif float(final_prediction) == 0:
    valid_prediction = True

# hago un dataframe para calcular el año y mes de la predicción
final_date_month_df = prediction_df.copy()

# hacemos una columna con el indice
final_date_month_df.reset_index(inplace=True)

# calculo el año de la predicción
final_year = final_date_month_df['ds'].dt.year.max()

# calculo el mes de la predicción
final_month = final_date_month_df['ds'].dt.month.max()

# paso de numero a nombre el mes de la predicción
datetime_object = datetime.datetime.strptime(str(final_month), "%m")
final_month_str = datetime_object.strftime("%B")

# damos resultados finales
print()
print('Tus gasto aproximado en restaurantes/salidas en ' + final_month_str + '-' + str(final_year) +
      ' sera: ' + str(5 * round(final_prediction / 5)) + ' eur')
print('Predicción válida: ' + str(valid_prediction))
print()
