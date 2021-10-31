Pedro Tobarra 2021-03-22:

- El archivo 'temporal_series_forecast_20210318.py' debe ser ejecutado desde la linea de comandos mediante el comando '$ python temporal_series_forecast_20210318.py'.

- Toma un fichero 'Cuenta_124075.xlsx' con una hoja '_select_TRANSACTION_DATE_cast_a' que debe estar en el mismo directorio que el de el script del cual coge el historico de movimientos de las columnas 'A' y 'B' ('TRANSACTION_DATE' y 'AMOUNT' respectivamente) y el saldo de la cuenta del último día (celda I2).

- El script construye el histórico del balance de la cuenta y devuelve la predicción del balance semanal medio de la cuenta para los próximos 90 días en un archivo csv llamado 'forecast_per_week.csv' que dejará en el mismo directorio del script 'temporal_series_forecast_20210318.py'.

- El archivo 'forecast_per_week.csv' contiene las observaciones del balance semanal medio de la cuenta acompañado de la fecha del domingo de la semana para la cual predice su balance semanal medio. Por ejemplo:

,BALANCE
2021-02-14,12989.197685758627
2021-02-21,16567.458106261023
2021-02-28,17870.146338501796
2021-03-07,16183.389318507116
2021-03-14,12603.728623623654
2021-03-21,8950.966941810375
2021-03-28,7016.209697157242
2021-04-04,6974.844076429045
2021-04-11,6612.119332881882
2021-04-18,3107.861708346971
2021-04-25,-3660.749427870807
2021-05-02,-9803.187919803751
2021-05-09,-10192.129284343499
2021-05-16,-6963.4995124333545

- El script 'temporal_series_forecast_20210318.py' ha sido probado con éxito en los sistemas operativos windows 7 y ubuntu 20.04 con Python 3.8 instalado y un entorno Python con las siguientes librerias instaladas (las cuales son las que se vienen por defecto en la última versión del programa 'Anaconda' que fue utilizado para codificar y depurar el script):

scipy: 1.6.1
numpy: 1.19.2
matplotlib: 3.3.4
pandas: 1.2.2
statsmodels: 0.12.2
sklearn: 0.23.2
Prophet 0.7.1

- La libreria Prophet o fbprophet 0.7.1 puede ser instalada ejecutando desde la línea de comandos '$ pip install fbprophet' ya que se encuentra disponible en el siguiente repositorio 'https://pypi.org/project/fbprophet/'. fpprohet también está disponible para su descarga e instalación como paquete de conda.

- Con el script 'versions.py' se pueden comprobar las versiones de las librerias instaladas en nuestro entorno ejecutándola desde la línea de comandos como '$ python versions.py'.

- Para dudas o problemas con la instalación del entorno y ejecución del script se puede contactar con el autor en el siguiente correo: pedro.tobarra@myvalue.com