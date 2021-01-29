import threading
import time

def worker():
    # 查看当前线程对象
    print(threading.current_thread())
    # for _ in range(5):
    while True:
        time.sleep(2)
        print("worker1...")
    print("finish")

# 查看当前线程对象
print(threading.current_thread())
t = threading.Thread(target=worker, name="worker")
t.start()