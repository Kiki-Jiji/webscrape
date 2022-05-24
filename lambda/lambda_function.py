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
import uuid


def main():

    today: str = date.today().strftime("%d_%m_%Y")
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    time_start = datetime.now()
    logging.info(f'Time started {time_start}')

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

    existing = load_existing(s3)

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

        try:
            books, img_urls = extract_books(page, today, catagory = url)
            process_imgs(img_urls, existing, s3)
        except:
            logging.info(f'!!!!!!!!!!!!!!1Failed to process!!!!!!!!!!! {url}')

        book_pages[url] = books


    try:
        save_existing(s3, existing)
        write_books_s3(book_pages, today)
    except Exception as e:
        logging.info(f'Writeing to s3 failed {e}')


    time_end = datetime.now()
    logging.info(f'Time end {time_end}')
    logging.info(f'Time taken {time_end - time_start}')



def get_image_url(img):
    
    img_tag = [i for i in [i for i in img][0]][0]

    dynamic_imgs = re.findall("\{.*\}", str(img_tag))

    dynamic_imgs_seperated = dynamic_imgs[0].split("[")

    img_links = [re.findall("http.*.jpg", i) for i in dynamic_imgs_seperated]


    # this is a horrible hack :P 
    # want the link which had 906 (or any three number begingging with 9)
    answer = None
    for i in img_links:
        try:
            re.search("9[0-9]{2},", i[0]).group(0)
            answer = i[0]
        except:
            pass

    return answer

def get_child(html, pos):
    return [i for i in html[pos].children][0]



def extract_books(page, today, catagory):

    book_list = page.find_all('span', {'class' : 'zg-bdg-text'})

    assert len(book_list) > 0, 'no books found'
    books = {}
    book_covers = {}

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

                img = "unknown"
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

        img_url = get_image_url(img)

        img = {
            "img_url": img_url,
            "book_title": book['book_title_txt'],
            "author": book['author_txt'],
        }

        book_covers[book_rank_scrape] = img

    return books, book_covers


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


def load_existing(s3):
    response = s3.get_object(Bucket='books-webscrape', Key="existing.json")
    existing_bytes = response['Body'].read()
    existing = json.loads(existing_bytes)
    return existing

def save_existing(s3, existing):
    serializedExisting = json.dumps(existing)
    response = s3.put_object(Body = serializedExisting, Bucket='books-webscrape', Key="existing.json")
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
        logging.info(f"Successful S3 put_object response. Status - {status}")
    else:
        logging.info(f"Unsuccessful S3 put_object response. Status - {status}")
        raise Exception(f"Unsuccessful S3 get_object response. Status - {status}")


def save_book_cover(img_url, s3, ref: str):
    image_url = img_url['url']

    img_data = requests.get(image_url).content
    response = s3.put_object(Body = img_data, Bucket='books-webscrape', Key= "covers/" + ref)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        logging.info(f"Successful S3 put_object response. Status - {status}")
    else:
        logging.info(f"Unsuccessful S3 put_object response. Status - {status}")
        raise Exception(f"Unsuccessful S3 get_object response. Status - {status}")


def process_imgs(img_urls: dict, existing:dict, s3) -> dict :
    for rank in img_urls.keys():
        ref = str(uuid.uuid1())

        book_metadata = {
            "author": img_urls[rank]['author'] ,
            "title": img_urls[rank]['book_title'],
            "url": img_urls[rank]['img_url']
        }


        existing_authors = [existing[i]['author'] for i in existing]

        if book_metadata['author'] in existing_authors:

            references_author = [ref for ref in existing if existing[ref]['author'] ==  book_metadata['author'] ]
            exisiting_titles = [existing[ref]['title'] for ref in references_author]

            if book_metadata['title']  in exisiting_titles:
                logging.info(f"book already exists for author: {book_metadata['author']} and book {book_metadata['title'] }")
            else:
                logging.info("book doesn't exist but author does")
                save_book_cover(book_metadata, s3, ref)
                existing[ref] = book_metadata
        else:
            logging.info("new author")
            save_book_cover(book_metadata, s3, ref)
            existing[ref] = book_metadata

    return existing



def write_books_s3(book_pages: dict, today: str):

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
    csv_filename = "books.csv"

    response = s3.get_object(Bucket=s3_bucket_name, Key=csv_filename)

    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        logging.info(f"Successful S3 get_object response. Status - {status}")
    else:
        logging.info(f"Unsuccessful S3 get_object response. Status - {status}")
        raise Exception(f"Unsuccessful S3 get_object response. Status - {status}")


    data = response['Body'].read().decode('utf-8').splitlines()
    records = csv.DictReader(data)

    existing = [i for i in records]

    rows = []
    for catagory in book_pages.keys():
        for rank in book_pages[catagory].keys():
            rows.append(book_pages[catagory][rank])


    latest_date = get_latest_date(existing)
    if latest_date == today:
        logging.info("This date already exists, not saving")
        return


    combined = existing + rows

    stream = io.StringIO()
    headers = list(combined[0].keys())
    writer = csv.DictWriter(stream, fieldnames=headers)
    writer.writeheader()
    writer.writerows(combined)

    csv_string_object = stream.getvalue()

    response = s3.put_object(
                Bucket = s3_bucket_name, Key = csv_filename, Body = csv_string_object
            )

    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        logging.info(f"Successful S3 put_object response. Status - {status}")
    else:
        logging.info(f"Unsuccessful S3 put_object response. Status - {status}")
        raise Exception(f"Unsuccessful S3 get_object response. Status - {status}")


def get_latest_date(existing: List):
    all_dates = [i['date'] for i in existing]

    unique_dates = set(all_dates)

    latest_date_raw = max([datetime.strptime(i, '%d_%m_%Y').date() for i in unique_dates])

    latest_date = re.sub("-", "_", latest_date_raw.strftime("%d_%m_%Y"))

    return(latest_date)

def lambda_handler(event, context):
    main()
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Successful')
    }
