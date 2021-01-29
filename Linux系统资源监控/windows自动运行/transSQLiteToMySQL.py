import sqlite3
import pymysql

# sqlite params
tableName = "MYSYS_STATUS"
cpuField = "CPU_USE"
memField = "MEM_USE"
timeField = "RTIME"

# mysql params
ip = "192.168.10.149"
port = 3306
username = "sysmon"
password = "0403"
db = "iserver_monitor"
charset = "utf8"

# sqlite
sqliteDB = "./db/sysStatus.db"

conn_sqlite = sqlite3.connect(sqliteDB)
cur_sqlite = conn_sqlite.cursor()
datas = cur_sqlite.execute(f"select {cpuField}, {memField}, {timeField} from {tableName};").fetchall()
conn_sqlite.commit()
conn_sqlite.close()

# mysql
conn_mysql = pymysql.connect(
    host=ip,
    port=port,
    user=username,
    password=password,
    db=db,
    charset=charset,
    cursorclass=pymysql.cursors.DictCursor
)

cur_mysql = conn_mysql.cursor()

for i, each in enumerate(datas):
    sqlExp = (f"insert into {tableName}({cpuField}, {memField}, {timeField}) "
              f"values({each[0]}, {each[1]}, STR_TO_DATE(" + "'" + each[2] + "', '%Y-%m-%d %H:%i:%s'));")
    cur_mysql.execute(sqlExp)

    if i % 50 == 0:
        print(i)

conn_mysql.commit()
conn_mysql.close()
