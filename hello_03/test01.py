from clickhouse_driver import Client
from datetime import date

client = Client(host='localhost', user='hzg', password='1234')
client.execute('SHOW DATABASES')

client.execute(
    'SELECT %(date)s, %(a)s + %(b)s',
    {'date': date.today(), 'a': 1, 'b': 2}
)