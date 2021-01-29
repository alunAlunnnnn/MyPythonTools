import threading
import time

"""
1、python中的线程没有销毁、挂起、恢复、中断、停止等概念
2、python中的线程是并发非并行，在进程内始终以先后顺序进行执行
"""

def worker():
    for _ in range(10):
        print("worker1")
        time.sleep(0.5)
    print("worker1 finish")


def worker2():
    for _ in range(10):
        print("worker2...")
        time.sleep(0.5)
    print("worker2 finish")

t = threading.Thread(target=worker, name="worker")
t2 = threading.Thread(target=worker2, name="worker2")
t.start()
t2.start()

print("main theading")