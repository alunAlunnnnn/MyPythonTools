import psutil
import time

while True:
    # 查看 cpu 的使用率
    cpuStatus = psutil.cpu_percent(interval=1, percpu=False)
    print("CPU使用率：", cpuStatus)

    # 查看 swap 空间使用情况
    # swapStatus = psutil.swap_memory()
    # print(swapStatus)

    # 查看 内存 使用情况
    virMemStatus = psutil.virtual_memory()
    print(virMemStatus)

    # 查看硬盘的 磁盘类型、读写权限
    # diskStatus = psutil.disk_partitions()
    # print(diskStatus)

    # 查看磁盘的空间占用率
    # diskUsageStatus = psutil.disk_usage("C://")
    # print(diskUsageStatus)

    # 查看磁盘IO信息
    # diskIOStatus = psutil.disk_io_counters()
    # print(diskIOStatus)

    # 查看网络接口信息
    # netAddr = psutil.net_if_addrs()
    # print(netAddr)

    # 查看所有进程
    # pidStatus = psutil.pids()
    # print(pidStatus)

    # 查看进程的详细信息
    # process = psutil.Process(1132)
    # print(process)

    time.sleep(5)