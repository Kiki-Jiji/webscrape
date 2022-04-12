from ipaddress import ip_address
from itertools import count
import requests
import random
from bs4 import BeautifulSoup
import pandas as pd

def get_child(html, pos):
    return [i for i in html[pos].children][0]

def extract_books(page):

    book_list = page.find_all('span', {'class' : 'zg-bdg-text'})

    books = {}

    for book_ranking in book_list:
        
        book_rank_scrape = [i for i in book_ranking][0]

        book = {
            'book_rank_scrape' : book_rank_scrape
        }

        book_box = book_ranking.parent.parent.parent


        book_info = [i for i in [i for i in [i for i in book_box.children][1]][0]]

        assert len(book_info) == 6

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