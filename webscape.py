import imp
from bs4 import BeautifulSoup
import requests
import pandas as pd
import gspread
import df2gspread as d2g
from datetime import date

URL = "https://www.amazon.co.uk/Best-Sellers-Books-Romance/zgbs/books/88/ref=zg_bs_unv_books_2_277563_2"

HEADERS = { 
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
'Accept-Language' : 'en-US,en;q=0.5',
'Accept-Encoding' : 'gzip', 
'DNT' : '1', # Do Not Track Request Header 
'Connection' : 'close'
}

webpage = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(webpage.content)


books = {}


book_list = soup.find_all('span', {'class' : 'zg-bdg-text'})


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





books_df = pd.DataFrame.from_dict(books, orient='index')


today = date.today().strftime("%d_%m_%Y")


gc = gspread.service_account('webscrape-346716-8f0851ec8cad.json')

sh = gc.open("Amazon Data")

sh.add_worksheet(today, rows = 20, cols = 10)

worksheet = sh.worksheet(today)

worksheet.update([books_df.columns.values.tolist()] + books_df.values.tolist())
