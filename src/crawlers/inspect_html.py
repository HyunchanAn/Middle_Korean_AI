import requests
from bs4 import BeautifulSoup

url = "http://db.sejongkorea.org/front/detail.do?bkCode=P01_SG_v001&recordId=P01_SG_e01_v001_0010"
response = requests.get(url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

div = soup.find('div', class_='tx_eh')
with open("data/raw/scratch_html.txt", "w", encoding="utf-8") as f:
    f.write(div.prettify())
