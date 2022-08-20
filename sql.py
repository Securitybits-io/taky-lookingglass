import pymysql

sql_conn = pymysql.connect(host='localhost', user='root', password='mypass', cursorclass=pymysql.cursors.DictCursor)

cursor = sql_conn.cursor()

cursor.execute('CREATE DATABASE IF NOT EXISTS taky;')
sql_conn.commit()