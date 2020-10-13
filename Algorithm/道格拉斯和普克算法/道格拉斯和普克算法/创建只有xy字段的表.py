import sqlite3
import random

conn = sqlite3.connect(
    r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\Algorithm\道格拉斯和普克算法\道格拉斯和普克算法\打包\代码/DPTest.db")
cur = conn.cursor()
for i in range(1, 8):
    cur.execute(f"drop table if exists new_withattr_shp_{i};")
    cur.execute(f"drop table if exists new_withattr_shp_{i}_res;")
    cur.execute(f"drop table if exists shp_{i}_res;")
    cur.execute(f"create table if not exists new_withattr_shp_{i} as select x, y, z, rowid as id from shp_{i};")
    cur.execute(f"alter table new_withattr_shp_{i} add name text(25);")

    rowNum = cur.execute(f"select count(id) from new_withattr_shp_{i}").fetchone()[0]
    print(rowNum)

    for j in range(1, rowNum + 1):
        cur.execute(f"update new_withattr_shp_{i}"
                    f" set name='{chr(random.randint(97, 122)) + chr(random.randint(97, 122)) + chr(random.randint(97, 122))}'"
                    f"where id={j}")

        # cur.execute(f"update new_withattr_shp_{i}"
        #             f" set name='a'"
        #             f"where id={j}")
    # res = cur.execute(f'PRAGMA table_info(new_withattr_shp_{i})').fetchall()
    # res = cur.execute(f'PRAGMA table_info(test)').fetchall()
    # print(res)
    # print(res[0][4])
    # print(type(res[0][4]))
    # print(res[0][4] is None)
    conn.commit()

conn.close()
