#!/usr/bin/env python
# coding: utf-8

# In[1]:


from datetime import datetime

from fbprophet import Prophet
from pandas import read_excel, date_range, to_datetime, DatetimeIndex
from pandas import to_numeric, DateOffset

# LOAD DATA USING READ_EXCEL
transactions_df = read_excel('Cuenta_124075.xlsx', sheet_name='_select_TRANSACTION_DATE_cast_a')
balance_last_day_real = to_numeric(transactions_df.loc[[0], ['BALANCE']].squeeze(), downcast='float')
transactions_df: object = transactions_df.iloc[:, 0:2]

# AGREGAMOS LAS TRANSACCIONES POR DIA
transactions_df = transactions_df.groupby(transactions_df.TRANSACTION_DATE).sum()
transactions_df.reset_index(level=0, inplace=True)
range_of_dates = date_range(start=transactions_df.TRANSACTION_DATE.min(), end=transactions_df.TRANSACTION_DATE.max())

# rellenamos los dias sin transacciones con el valor 0.0
transactions_df = \
    transactions_df.set_index('TRANSACTION_DATE').reindex(range_of_dates).fillna(0.0) \
        .rename_axis('TRANSACTION_DATE').reset_index()
transactions_df = transactions_df.set_index(transactions_df.iloc[:, 0])
transactions_df = transactions_df.drop(['TRANSACTION_DATE'], axis=1)

# CONSTRUIMOS EL DATAFRAME DEL BALANCE DE LA CUENTA
balance_df = transactions_df.copy()
balance_df.reset_index(level=0, inplace=True)
balance_df["DATE"] = balance_df["TRANSACTION_DATE"]
balance_df["BALANCE"] = 0

for i in range(balance_df.index[0], balance_df.index[-1]):
    balance_df.loc[i + 1, 'BALANCE'] = balance_df.loc[i, 'BALANCE'] + balance_df.loc[i, 'AMOUNT']

balance_df = balance_df.drop(['TRANSACTION_DATE', 'AMOUNT'], axis=1)
balance_df = balance_df.set_index(balance_df.iloc[:, 0])
balance_df = balance_df.drop(['DATE'], axis=1)
balance_last_day_fake = to_numeric(balance_df.iloc[-1:].squeeze(), downcast='float')
bias = balance_last_day_real - balance_last_day_fake
balance_df['BALANCE'] = balance_df['BALANCE'] + bias

# PREPARAMOS UN DATAFRAME prophet_df PARA ENTRENAR UN MODELO
prophet_df = balance_df.copy()
prophet_df.reset_index(level=0, inplace=True)

# prepare expected column names
prophet_df.columns = ['ds', 'y']
prophet_df['ds'] = to_datetime(prophet_df['ds'])

# define the model
model = Prophet()
# fit the model
model.fit(prophet_df)

# HACEMOS UNA PREDICCION A 90 DIAS
# Make an Out-of-Sample Forecast
future_out_sample_df = prophet_df.copy()
future_out_sample_df = future_out_sample_df.drop(['y'], axis=1)
future_out_sample_df = future_out_sample_df[-90:]
future_out_sample_df.reset_index(level=0, inplace=True)
future_out_sample_df = future_out_sample_df.drop(['index'], axis=1)
future_out_sample_df.iloc[0, 0] = future_out_sample_df.iloc[-1, 0] + DateOffset(1)

for i in range(1, len(future_out_sample_df)):
    future_out_sample_df.iloc[i, 0] = future_out_sample_df.iloc[i - 1, 0] + DateOffset(1)

# use the model to make a forecast
forecast_df = model.predict(future_out_sample_df)
forecast_per_day_df = forecast_df.loc[:, ['ds', 'yhat']]
forecast_per_day_df.columns = ['DATE', 'BALANCE']

# HACEMOS UN DATAFRAME CON LA PREDICCION DEL BALANCE MEDIO SEMANAL DE LA CUENTA A 90 DIAS
forecast_per_week_df = forecast_per_day_df.copy()

# Using a lambda function on apply.() to separate the year, month, day components
forecast_per_week_df['DATE'].apply(lambda forecast_per_week_df: datetime(year=forecast_per_week_df.year, \
                                                                         month=forecast_per_week_df.month, \
                                                                         day=forecast_per_week_df.day))

# Set the date as the index

# convert the column (if it's a string) to datetime type
datetime_ser = to_datetime(forecast_per_week_df['DATE'])

# create datetime index passing the datetime series
datetime_index = DatetimeIndex(datetime_ser.values)
forecast_per_week_df = forecast_per_week_df.set_index(datetime_index)

# we don't need the column DATE anymore
forecast_per_week_df.drop('DATE', axis=1, inplace=True)

# Using resample() method to aggregate by weeks and add mean() to take the average
forecast_per_week_ser = forecast_per_week_df['BALANCE'].resample('W').mean()

# guardamos el resultado final en un fichero .csv
forecast_per_week_ser.to_csv(path_or_buf='forecast_per_week.csv')

# In[ ]:
