import os

dirPath = r"E:\松江管廊\新数据0805\服务发布\自动创建url对应关系代码"

support_packages_dir = os.path.join(dirPath, "support_package")
pRequests = os.path.join(support_packages_dir, "requests-2.23.0-py2.py3-none-any.whl")
pOpenpyxl = os.path.join(support_packages_dir, "openpyxl-3.0.5-py2.py3-none-any.whl")
pBS4 = os.path.join(support_packages_dir, "beautifulsoup4-4.9.1-py3-none-any.whl")
pLxml = os.path.join(support_packages_dir, "lxml-4.5.2-cp36-cp36m-win_amd64.whl")

try:
    print("正在尝试导入 requests")
    import requests

    print("成功导入 requests \n")
except:
    print("导入 requests 失败，正在安装 requests")
    os.system("pip install %s" % pRequests)
    print("成功安装 requests \n")

try:
    print("正在尝试导入 openpyxl")
    import openpyxl

    print("成功导入 openpyxl \n")
except:
    print("导入 openpyxl 失败，正在安装 openpyxl")
    os.system("pip install %s" % pOpenpyxl)
    print("成功安装 openpyxl \n")

try:
    print("正在尝试导入 beautifulsoup4")
    from bs4 import BeautifulSoup

    print("成功导入 beautifulsoup4 \n")
except:
    print("导入 beautifulsoup4 失败，正在安装 beautifulsoup4")
    os.system("pip install %s" % pBS4)
    print("成功安装 beautifulsoup4 \n")

try:
    print("正在尝试导入 lxml")
    import lxml

    print("成功导入 lxml \n")
except:
    print("导入 lxml 失败，正在安装 lxml")
    os.system("pip install %s" % pLxml)
    print("成功安装 lxml \n")

print("程序运行结束")
