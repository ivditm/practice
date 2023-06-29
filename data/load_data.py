import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()


dbname = os.getenv('dbname', '')
host = os.getenv('host', '')
user = os.getenv('user', '')
password = os.getenv('password', '')


conn = psycopg2.connect(dbname=dbname,
                        host=host,
                        port=5432,
                        user=user,
                        password=password)
try:
    cursor = conn.cursor()
    data = pd.read_csv('C:/Dev/practice/data/cw.csv', sep=';')
    data['Date'] = pd.to_datetime(data['Date'], format='%d.%M.%Y')
    data = data.melt(id_vars=['Date'], value_vars=['AAPL', 'BA', 'CAT',
                                                   'CSCO', 'IBM', 'KO',
                                                   'MSFT', 'NKE'],
                     var_name='company_name', value_name='price')
    for index in range(len(data)):
        cursor.execute(f'''
                           insert into
                                quotes (date, company_name, price)
                                values ('{data['Date'][index]}',
                                        '{data['company_name'][index]}',
                                         {data['price'][index]});
                      ''')
    cursor.close()
    conn.commit()
finally:
    conn.close()
