import threading

"""
线程传参：
1、参数在线程实例化时传入
2、传入参数关键字为args 或 kwargs
3、args传入类型为元组，kwargs传入类型为字典且key为字符串
"""

def worker(n):
    for _ in range(n):
        print("working...")
    print("finish")

t = threading.Thread(target=worker, name="worker", args=(10,))
t.start()