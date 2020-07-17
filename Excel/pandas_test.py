import numpy as np
from pandas import DataFrame
import pandas as pd

xls = r'D:\test\tempexcel.xls'

df = pd.read_excel(xls)

# print(df)

print(df['x_temp_l'][0])
print(float(df['x_temp_l'][0]))
print(type(float(df['x_temp_l'][0])))
# print(df['x_temp_l'])





# print(df)
#
# df=DataFrame(np.arange(12).reshape((3,4)),index=['one','two','thr'],columns=list('abcd'))
