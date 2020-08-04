import requests
from bs4 import BeautifulSoup
import os

# os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple lxml')

url = 'http://www.pythonscraping.com/pages/warandpeace.html'

res = requests.get(url)

data = BeautifulSoup(res.text, 'lxml')

# print(data.prettify())

greens = data.findAll('span', {'class': 'green'})
print(greens)