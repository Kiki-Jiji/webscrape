import imp
from bs4 import BeautifulSoup
import requests
import pandas as pd
import gspread
import df2gspread as d2g
from datetime import date

from utils import extract_books




HEADERS = { 
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
'Accept-Language' : 'en-US,en;q=0.5',
'Accept-Encoding' : 'gzip', 
'DNT' : '1', # Do Not Track Request Header 
'Connection' : 'close'
}

today = date.today().strftime("%d_%m_%Y")

gc = gspread.service_account('webscrape-346716-8f0851ec8cad.json')

sh = gc.open("Amazon Data")



urls = {
    'all_romance': "https://www.amazon.co.uk/Best-Sellers-Books-Romance/zgbs/books/88/ref=zg_bs_unv_books_2_277563_2",
    'historical': "https://www.amazon.co.uk/Best-Sellers-Books-Historical-Romance/zgbs/books/277831/ref=zg_bs_nav_books_2_88"
}

for url in urls:
    
    webpage = requests.get(urls[url], headers=HEADERS)
    page = BeautifulSoup(webpage.content)

    books = extract_books(page)

    books_df = pd.DataFrame.from_dict(books, orient='index')

    sheetName = today + '_' + url

    sh.add_worksheet(sheetName, rows = 20, cols = 10)

    worksheet = sh.worksheet(sheetName)

    worksheet.update([books_df.columns.values.tolist()] + books_df.values.tolist())
