import pymysql

conn = pymysql.connect(
    host="192.168.10.149",
    port=3306,
    user="sysmon",
    password="0403",
    db="iserver_monitor",
    charset="utf8",
    cursorclass=pymysql.cursors.DictCursor
)

cur = conn.cursor()
cur.execute("drop table if exists MYSYS_STATUS;")
cur.execute("create table if not exists MYSYS_STATUS(ID integer primary key auto_increment, CPU_USE float,"
            " MEM_USE float, RTIME TimeStamp NOT NULL DEFAULT CURRENT_TIMESTAMP);")
# cur.execute("create table if not exists MYSYS_STATUS(ID integer primary key auto_increment, CPU_USE float,"
#             " MEM_USE float, RTIME TimeStamp not null);")

conn.commit()
conn.close()
