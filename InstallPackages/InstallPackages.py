import os

pks = ['pillow', 'couchdb']

try:
    print('*' * 30, 'pip update start', '*' * 30)
    os.system('python -m pip install --upgrade pip')
    print('*' * 30, 'pip update finish', '*' * 30)
except:
    print('*' * 30, 'pip update failed', '*' * 30)

for each in pks:
    os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple %s' % each)