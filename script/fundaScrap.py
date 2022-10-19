from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from datetime import datetime

#%%

fundaUrl = 'https://www.funda.nl/huur/amsterdam/'
funda = requests.get(fundaUrl)
fundaSoup = BeautifulSoup(funda.text,'html.parser')

print(fundaSoup)

#get total house number in order to get page count
fundaPageCount = fundaSoup.find_all("div",{'class':'app-footer-v2-items'})[0]
.get_text().split()
