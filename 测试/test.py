import pandas as pd

data = r"F:\工作项目\项目_松江基础设施系统\松江区既有玻璃幕墙建筑信息登记表（信息采集）完成（排查后调整341家）20190826.xlsx"

# df = pd.read_excel(data)
#
# print(df.head(37))

import openpyxl

wb = openpyxl.load_workbook(data)

sht = wb.active

for each in sht.rows:
    print(each[1].value)