import json
import os
from datetime import date, datetime
import time
import logging
import boto3
from bs4 import BeautifulSoup
import requests
import io

def main():

    today = date.today().strftime("%d_%m_%Y")
    
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

    for url in urls:

        page = get_webpage(
            url= urls[url],
        )

        logging.info(f'Scraped {url}')

        books = extract_books(page)

        book_pages[url] = books


    book_data = {
        "data" : book_pages,
        "date" : today
    }

    try:
        write_books_s3(book_data, filename = today)
    except Exception as e:
        logging.info(f'Writeing to s3 failed {e}')

    time_end = datetime.now()
    logging.info(f'Time end {time_end}')
    logging.info(f'Time taken {time_end - time_start}')



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



def write_books_s3(book_dict, filename):

    aws_access_key = os.getenv('access_key')
    aws_secret_access = os.getenv('secret')

    if aws_access_key is None or aws_secret_access is None:
        raise Exception("Missing envrioment variables to access s3- access_key and secret")

    s3 = boto3.client(
        service_name = 's3',
        region_name = 'eu-west-2',
        aws_access_key_id = aws_access_key,
        aws_secret_access_key = aws_secret_access
    )

    s3_bucket_name = 'books-webscrape'

    response = s3.put_object(
        Body = json.dumps(book_dict),
        Bucket = s3_bucket_name,
        Key = filename
    )

    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        logging.info(f"Successful S3 put_object response. Status - {status}")
    else:
        logging.info(f"Unsuccessful S3 put_object response. Status - {status}")



def lambda_handler(event, context):
    main()
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Successful')
    }
