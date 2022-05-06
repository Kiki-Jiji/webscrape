from ipaddress import ip_address
from itertools import count
import json
from re import T
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
import gspread
import logging
import yaml
import boto3
import os
import pandas as pd
import io


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




def write_gs(df):

    gc = gspread.service_account("webscrape-346716-e7082b6f73c5.json")

    sh = gc.open("Amazon Data")

    sheetName = date.today().strftime("%d_%m_%Y") 

    try:
        sh.add_worksheet(sheetName, rows = 20, cols = 10)
    except:
        sheetName = sheetName + '_1'
        sh.add_worksheet(sheetName, rows = 20, cols = 10)

    logging.info(f'Created excel sheetnamer was: {sheetName}')

    worksheet = sh.worksheet(sheetName)

    worksheet.update([df.columns.values.tolist()] + df.values.tolist())


def get_webpage(url):

    api_key =  os.getenv('proxy_api')
    assert api_key is not None, "envrioment var proxy_api not found"

    api_url = "https://api.webscrapingapi.com/v1"

    params = {
        "api_key": api_key['api_key'],
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



def load_all_data():

    gc = gspread.service_account("webscrape-346716-e7082b6f73c5.json")

    sh = gc.open("Amazon Data")

    worksheet_list = sh.worksheets()

    sheet_dfs = {}

    for sheet in worksheet_list:
        dataframe = pd.DataFrame(sheet.get_all_records())
        dataframe['date'] = sheet.title
        sheet_dfs[sheet.title] = dataframe


    all_data =  pd.concat(sheet_dfs.values(), ignore_index=True)
    return all_data


def write_books_s3(book_dict, filename):
    

    aws_access_key = os.environ.get('access_key')
    aws_secret_access = os.environ.get('secret')

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


def convert_to_pd(book_pages: Dict, date: chr):

    books_dfs = {}

    for cato in book_pages.keys():

        cato_df = pd.DataFrame.from_dict(book_pages[cato], orient='index')
        cato_df['catagory'] = cato

        books_dfs[cato] = cato_df

    day_df = pd.concat(books_dfs.values(), ignore_index=True)
    day_df['date'] = date
    
    return day_df

def write_books_s3(book_pages_df, today):

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

    response = s3.get_object(Bucket=s3_bucket_name, Key="books.csv")

    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        logging.info(f"Successful S3 get_object response. Status - {status}")
        books_df = pd.read_csv(response.get("Body"))
    else:
        logging.info(f"Unsuccessful S3 get_object response. Status - {status}")


    if today in books_df.date.unique():
        logging.info("Data already exists, not saving")
        return
    else:
        logging.info("Data doesn't exists, adding to total")
        combined_data = pd.concat([books_df, book_pages_df])
        
        
    with io.StringIO() as csv_buffer:
        combined_data.to_csv(csv_buffer, index=False)

        response = s3.put_object(
            Bucket=s3_bucket_name, Key="books.csv", Body=csv_buffer.getvalue()
        )

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if status == 200:
            logging.info(f"Successful S3 put_object response. Status - {status}")
        else:
            logging.info(f"Unsuccessful S3 put_object response. Status - {status}")
