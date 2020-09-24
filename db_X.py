'''
import sqlite3

conn = sqlite3.connect("test.db")

cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS account(id INTEGER, user TEXT, pw TEXT)""")

sql = "DELETE FROM account"


sql = "INSERT into account(id, user, pw) values (?, ?, ?)"
cursor.execute(sql, (1, 'admin1', '1234'))


sql = "INSERT into account(id, user, pw) values (?, ?, ?)"
cursor.execute(sql, (2, 'admin2', '5678'))



sql = "SELECT * FROM account"
cursor.execute(sql)

rows = cursor.fetchall()


# for row in rows :
#     print(str(row[0]) + " " + str(row[1]) + " " + str(row[2]) + " ")


conn.commit()
conn.close
'''
