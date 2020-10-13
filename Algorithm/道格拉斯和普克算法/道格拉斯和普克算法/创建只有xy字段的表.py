import sqlite3

conn = sqlite3.connect(r"E:/GIS算法/道格拉斯和普克算法/测试数据/DPTest.db")
cur = conn.cursor()
for i in range(1, 8):
    cur.execute(f"drop table if exists new_shp_{i};")
    cur.execute(f"drop table if exists shp_{i}_res;")
    cur.execute(f"create table if not exists new_shp_{i} as select x, y from shp_{i};")
    conn.commit()

conn.close()
