import pandas as pd
from datetime import date, datetime
import time
from random import random
import logging

from utils import extract_books, get_free_proxies, Proxy, write_gs

today = date.today().strftime("%d_%m_%Y")

logging.basicConfig(
    level=logging.DEBUG, 
    filename = f'logs/app_{today}.log', 
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s')


time_start = datetime.now()
logging.debug(f'Time started {time_start}')

HEADERS = { 
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
'Accept-Language' : 'en-US,en;q=0.5',
'Accept-Encoding' : 'gzip', 
'DNT' : '1', # Do Not Track Request Header 
'Connection' : 'close'
}

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


# urls = {
#     'UK_Hist_Romance': 'https://www.amazon.co.uk/Best-Sellers-Kindle-Store-Historical-Romance/zgbs/digital-text/362727031/ref=zg_bs_unv_digital-text_4_3507148031_2'
# }

Prox = Proxy(HEADERS)

book_pages = {}

for url in urls:
    time.sleep(random() / random()) 

    page = Prox.get_webpage(
        url= urls[url],
    )

    logging.debug(f'Scraped {url}')

    books = extract_books(page)

    df =  pd.DataFrame.from_dict(books, orient='index')
    df['category'] = url

    book_pages[url] = df


all_webpages_df =  pd.concat(book_pages.values(), ignore_index=True)

try:
    write_gs(all_webpages_df)
except:
    all_webpages_df.to_csv(f'backup_data_{today}.csv', index=False)

time_end = datetime.now()
logging.debug(f'Time end {time_end}')
logging.debug(f'Time taken {time_end - time_start}')