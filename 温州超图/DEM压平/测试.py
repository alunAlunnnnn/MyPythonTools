import datetime
import time

now = datetime.datetime.now()
limit = datetime.datetime.strptime("2020-12-19 16:30:00", "%Y-%m-%d %H:%M:%S")
print(limit > now)
print(type(now.date()))


# while True:
