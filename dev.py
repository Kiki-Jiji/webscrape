import json
import os
from datetime import date, datetime
import time
import logging
import boto3
from bs4 import BeautifulSoup
import requests
import io
from typing import Dict, List
import csv
import re


def get_child(html, pos):
    return [i for i in html[pos].children][0]

def extract_books(page, today, catagory):

    book_list = page.find_all('span', {'class' : 'zg-bdg-text'})

    assert len(book_list) > 0, 'no books found'
    books = {}

    for book_ranking in book_list:
        
        book_rank_scrape = [i for i in book_ranking][0]

        book = {
            'book_rank_scrape' : book_rank_scrape
        }

        book_box = book_ranking.parent.parent.parent


        book_info = [i for i in [i for i in [i for i in book_box.children][1]][0]]

        if len(book_info) != 6:
            if len(book_info) == 5:
                # gonna guess that 5 means no star rating TODO improve later

                img = book_info[0]
                book_title = book_info[1]
                author = book_info[2]
                book_type = book_info[3]
                price = book_info[4]

                # book title
                book['book_title_txt'] = [i for i in [i for i in [i for i in book_title.children][0].children][0].children][0]
                book['author_txt'] = [i for i in [i for i in [i for i in author][0]][0]][0]
                book['star_rating_txt' ] = 'unknown'
                book['book_type_txt'] = [i for i in [i for i in book_type][0]][0]
                book['price_txt'] = [i for i in [i for i in [i for i in [i for i in price][0]][0]][0]][0]
                book['catagory'] = catagory
                book['date'] = today

            else:
                # no idea jk :P but dict always needs 5 keys
                book['book_title_txt'] = 'unknown'
                book['author_txt'] = 'unknown'
                book['star_rating_txt' ] = 'unknown'
                book['book_type_txt'] = 'unknown'
                book['price_txt'] = 'unknown'
                book['catagory'] = catagory
                book['date'] = today
        else:
            # expected 6 catorgories
            img = book_info[0]
            book_title = book_info[1]
            author = book_info[2]
            star_rating = book_info[3]
            book_type = book_info[4]
            price = book_info[5]

            # book title
            book['book_title_txt'] = [i for i in [i for i in [i for i in book_title.children][0].children][0].children][0]
            book['author_txt'] = [i for i in [i for i in [i for i in author][0]][0]][0]
            book['star_rating_txt' ]= [i for i in [i for i in [i for i in [i for i in [i for i in star_rating][0]][0]][0]][0]][0]
            book['book_type_txt'] = [i for i in [i for i in book_type][0]][0]
            book['price_txt'] = [i for i in [i for i in [i for i in [i for i in price][0]][0]][0]][0]
            book['catagory'] = catagory
            book['date'] = today

        books[book_rank_scrape] = book

    return books



def get_webpage(url):

    api_key =  os.environ.get('proxy_api')
    assert api_key is not None, "envrioment var proxy_api not found"


    api_url = "https://api.webscrapingapi.com/v1"

    params = {
        "api_key": api_key,
        "url": url
    }

    success_status = False
    attept = 1
    max_attepts = 10

    while success_status is False and attept < max_attepts:
        
        try:
            response = requests.request("GET", api_url, params=params)
            logging.info(f'response status {response.status_code}')

            if response.status_code == 401:
                raise Exception("401 error")

            if response.status_code == 422:
                raise Exception("422 error")

            success_status = True
        except:
            attept += 1
            pass

    page = BeautifulSoup(response.content, features= "html.parser")

    return page


today: str = date.today().strftime("%d_%m_%Y")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

time_start = datetime.now()
logging.info(f'Time started {time_start}')

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

book_pages = {}


url = "UK_Hist_Romance"




page = get_webpage(
    url= urls[url],
)

logging.info(f'Scraped {url}')

books = extract_books(page, today, catagory = urls[url])

books.keys()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# image


# <a class="a-link-normal"
#  href="/Tell-Bees-that-Gone-Outlander-ebook/dp/B092DTBWN4/ref=zg_bs_362727031_1/257-9882171-3195063?pd_rd_i=B092DTBWN4&amp;psc=1" 
#  role="link"
#   tabindex="-1">
#   <div class="a-section a-spacing-mini _cDEzb_noop_3Xbw5">
#       <img alt="Go Tell the Bees that I am Gone: (Outlander 9)" 
#       class="a-dynamic-image p13n-sc-dynamic-image p13n-product-image"
#     data-a-dynamic-image='{"https://images-eu.ssl-images-amazon.com/images/I/81X9VujKgsL._AC_UL302_SR302,200_.jpg":[302,200],
#     "https://images-eu.ssl-images-amazon.com/images/I/81X9VujKgsL._AC_UL604_SR604,400_.jpg":[604,400]
#     ,"https://images-eu.ssl-images-amazon.com/images/I/81X9VujKgsL._AC_UL906_SR906,600_.jpg":[906,600]}'
#      height="200px"
#       src="https://images-eu.ssl-images-amazon.com/images/I/81X9VujKgsL._AC_UL302_SR302,200_.jpg" 
#       style="max-width:302px;max-height:200px"/></div>
#     </a>


image_url = "https://images-eu.ssl-images-amazon.com/images/I/81X9VujKgsL._AC_UL906_SR906,600_.jpg"

import requests

img_data = requests.get(image_url).content

with open('image_name.jpg', 'wb') as handler:
    handler.write(img_data)


