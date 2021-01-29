import psutil
import time
import sqlite3


db = "./db/sysStatus.db"
conn = sqlite3.connect(db)
cur = conn.cursor()

while True:
    # try:
    # 查看 cpu 的使用率
    cpuStatus = psutil.cpu_percent(interval=1, percpu=False)
    # print("CPU使用率：", cpuStatus)

    # 查看 内存 使用情况
    virMemStatus = psutil.virtual_memory()
    # print(virMemStatus)

    info = [cpuStatus, virMemStatus.percent]

    cur.execute("insert into MYSYS_STATUS(CPU_USE, MEM_USE) values(?, ?)", info)
    conn.commit()

    time.sleep(29)

