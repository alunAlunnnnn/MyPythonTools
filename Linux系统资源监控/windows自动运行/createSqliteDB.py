import sqlite3

db = sqlite3.connect("./db/sysStatus.db")
cur = db.cursor()
cur.execute("drop table if exists MYSYS_STATUS")
cur.execute("create table if not exists MYSYS_STATUS(ID integer primary key, CPU_USE REAL,"
            " MEM_USE REAL, RTIME TimeStamp NOT NULL DEFAULT (datetime('now','localtime')))")
db.commit()
db.close()
