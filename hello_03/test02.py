from clickhouse_driver import connect
from datetime import date

conn = connect(host='localhost', user='hzg', password='1234', database='default')
# conn = connect('clickhouse://localhost/default?user=hzg&password=1234')
cursor = conn.cursor()

cursor.execute('SHOW TABLES')
print(cursor.fetchall())

cursor.execute('SELECT %(date)s, %(a)s + %(b)s',
    {'date': date.today(), 'a': 1, 'b': 2}
)
print(cursor.fetchall())