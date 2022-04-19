from ipaddress import ip_address
from itertools import count
import requests
from requests.exceptions import ProxyError
import random
from bs4 import BeautifulSoup, Comment
import pandas as pd
from datetime import date
import gspread
import df2gspread as d2g
import logging

def get_child(html, pos):
    return [i for i in html[pos].children][0]

def extract_books(page):

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

            else:
                # no idea jk :P but dict always needs 5 keys
                book['book_title_txt'] = 'unknown'
                book['author_txt'] = 'unknown'
                book['star_rating_txt' ] = 'unknown'
                book['book_type_txt'] = 'unknown'
                book['price_txt'] = 'unknown'
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

        books[book_rank_scrape] = book

    return books



def get_free_proxies():

    url = "https://free-proxy-list.net/"
    # get the HTTP response and construct soup object
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    proxies = []

    table = soup.find_all('tbody')

    ip_addresses = [i for i in [i for i in table][0]]

    rows = {}
    count = 0

    for table_row in ip_addresses:

        try:
            ip = [i for i in table_row.children]

            row = {
                'ip': get_child(ip, 0),
                'port': get_child(ip, 1),
                'code': get_child(ip, 2),
                'country': get_child(ip, 3),
                'Anonymity': get_child(ip, 4),
                'Google': get_child(ip, 5),
                'Https': get_child(ip, 6),
                'last_checked': get_child(ip, 7),
            }

            rows[count] = row
        except:
            pass
        count += 1

    return pd.DataFrame.from_dict(rows, orient='index')



class Proxy:
    def __init__(self, HEADERS) -> None:
        self.headers = HEADERS
        self.proxies = get_free_proxies()
        self.proxy_num = 0
        self.current_proxy = self.proxies.ip.array[self.proxy_num]

    def get_webpage(self, url):
        success = False
        while success is False:
            print(self.current_proxy)
            try:
                webpage = self.try_proxy(url)
                logging.debug(f'Success with {self.current_proxy}, proxy number {self.proxy_num}')
                success = True
            except:
                self.set_current_proxy()
        return webpage

    def set_current_proxy(self):
        self.proxy_num += 1
        self.current_proxy = self.proxies.ip.array[self.proxy_num]

    def try_proxy(self, url):

        i = 1
        n = 5
        success_status = False
        while success_status is False:
            print(success_status)
            try:
                webpage = requests.get(url, headers=self.headers , proxies={"http": self.current_proxy, "https": self.current_proxy})
                page = BeautifulSoup(webpage.content, features= "html.parser")
                
                if amazon_blocked(page):
                    if i < n:
                        i += 1
                    else:
                        success_status = True
                success_status = True
            except ProxyError:
                if i < n:
                    i += 1
                else:
                    success_status = True
        
        assert i < n, "Proxy failed"

        return webpage


def write_gs(df):

    gc = gspread.service_account("webscrape-346716-e7082b6f73c5.json")

    sh = gc.open("Amazon Data")

    sheetName = date.today().strftime("%d_%m_%Y") 

    try:
        sh.add_worksheet(sheetName, rows = 20, cols = 10)
    except:
        sheetName = sheetName + '_1'
        sh.add_worksheet(sheetName, rows = 20, cols = 10)

    logging.debug(f'Created excel sheetnamer was: {sheetName}')

    worksheet = sh.worksheet(sheetName)

    worksheet.update([df.columns.values.tolist()] + df.values.tolist())




def amazon_blocked(page):

    comments = page.find_all(string=lambda text: isinstance(text, Comment))

    return True in ['automated' in i for i in comments]
