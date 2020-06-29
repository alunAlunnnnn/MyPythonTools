import openpyxl, os

data = r'‪D:\work\污水excel\20200619报告数据(密码wslzp0616)\1标待上传0616\宝德电气有限公司.xls'
wb = openpyxl.load_workbook(data)
sht1 = wb['sheet1']

for eachRow in sht1.rows:
    print(eachRow)

