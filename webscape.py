from ast import Try
import imp
from bs4 import BeautifulSoup
import requests
import pandas as pd
import gspread
import df2gspread as d2g
from datetime import date
import time
from random import random

from utils import extract_books, get_free_proxies




HEADERS = { 
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
'Accept-Language' : 'en-US,en;q=0.5',
'Accept-Encoding' : 'gzip', 
'DNT' : '1', # Do Not Track Request Header 
'Connection' : 'close'
}

today = date.today().strftime("%d_%m_%Y")

gc = gspread.service_account("webscrape-346716-e7082b6f73c5.json")

sh = gc.open("Amazon Data")


urls = {
    'UK_Hist_Romance': 'https://www.amazon.co.uk/Best-Sellers-Kindle-Store-Historical-Romance/zgbs/digital-text/362727031/ref=zg_bs_unv_digital-text_4_3507148031_2',
    'UK_Reg Romance': 'https://www.amazon.co.uk/Best-Sellers-Kindle-Store-Regency-Historical-Romance/zgbs/digital-text/3507148031/ref=zg_bs_nav_digital-text_4_362727031',
    'US_Hist_Romance': 'https://www.amazon.com/Best-Sellers-Kindle-Store-Historical-Romance/zgbs/digital-text/158571011/ref=zg_bs_unv_digital-text_4_158573011_2',
    'US_Reg_Romance' : 'https://www.amazon.com/Best-Sellers-Regency-Historical-Romance/zgbs/digital-text/158573011',
    'UK_Womens_Fiction' : 'https://www.amazon.co.uk/Best-Sellers-Kindle-Store-Womens-Fiction/zgbs/digital-text/4542772031/ref=zg_bs_nav_digital-text_3_362270031',
    'UK_Womens_Romance_Fiction': 'https://www.amazon.co.uk/Best-Sellers-Kindle-Store-Womens-Romance-Fiction/zgbs/digital-text/4542787031/ref=zg_bs_nav_digital-text_4_4542772031',
    'US_Womens_Fiction' : 'https://www.amazon.com/Best-Sellers-Kindle-Store-Womens-Fiction/zgbs/digital-text/6190492011/ref=zg_bs_nav_digital-text_3_157028011',
    'US_Womens_Rom_Fiction' : 'https://www.amazon.com/Best-Sellers-Kindle-Store-Womens-Romance-Fiction/zgbs/digital-text/7588898011/ref=zg_bs_nav_digital-text_4_6190492011'
}


proxies = get_free_proxies()

ips = proxies.ip.array

proxy = ips[0]

for url in urls:
    
    time.sleep(random() / random()) 

    webpage = requests.get(urls[url], headers=HEADERS, proxies={"http": proxy, "https": proxy})
    page = BeautifulSoup(webpage.content, features= "html.parser")

    books = extract_books(page)

    books_df = pd.DataFrame.from_dict(books, orient='index')

    sheetName = today + '_' + url

    try:
        sh.add_worksheet(sheetName, rows = 20, cols = 10)
    except:
        sheetName = sheetName + '1'
        sh.add_worksheet(sheetName, rows = 20, cols = 10)

    worksheet = sh.worksheet(sheetName)

    worksheet.update([books_df.columns.values.tolist()] + books_df.values.tolist())
