import psutil
import time
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


# mysql
conn = pymysql.connect(
    host=ip,
    port=port,
    user=username,
    password=password,
    db=db,
    charset=charset,
    cursorclass=pymysql.cursors.DictCursor
)

cur = conn.cursor()

while True:
    # try:
    # 查看 cpu 的使用率
    cpuStatus = psutil.cpu_percent(interval=1, percpu=False)
    # print("CPU使用率：", cpuStatus)

    # 查看 内存 使用情况
    virMemStatus = psutil.virtual_memory()

    sqlExp = f"insert into MYSYS_STATUS(CPU_USE, MEM_USE) values({cpuStatus}, {virMemStatus.percent});"
    print(sqlExp)

    cur.execute(sqlExp)
    conn.commit()

    time.sleep(29)

