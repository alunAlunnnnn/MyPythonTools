import sqlite3

# dbFile = r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\上海申通业务\data\st_main.db"
dbFile = r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\上海申通业务\data\st_main_pnt.db"
# table = "PNT_上行"
table = "PNT_下行"


db = sqlite3.connect(dbFile)
cur = db.cursor()

# res = cur.execute(f"select max(MILE) from {table} where MILE = {value}").fetchone()
# res = cur.execute(f"select max(SHT_LINE_ID) from {table};").fetchone()[0]
res = cur.execute(f"select SHT_LINE_ID from {table} where SHT_LINE_ID is not null").fetchall()
print(res)

db.commit()
cur.close()
db.close()