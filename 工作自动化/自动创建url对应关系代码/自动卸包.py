import os

try:
    print("正在卸载 requests")
    os.system("pip uninstall requests")
    print("成功卸载 requests")
except:
    print("卸载 requests 失败")

try:
    print("正在卸载 openpyxl")
    os.system("pip uninstall openpyxl")
    print("成功卸载 openpyxl")
except:
    print("卸载 openpyxl 失败")

try:
    print("正在卸载 beautifulsoup4")
    os.system("pip uninstall beautifulsoup4")
    print("成功卸载 beautifulsoup4")
except:
    print("卸载 beautifulsoup4 失败")
    
try:
    print("正在卸载 lxml")
    os.system("pip uninstall lxml")
    print("成功卸载 lxml")
except:
    print("卸载 lxml 失败")


print("卸载程序结束")