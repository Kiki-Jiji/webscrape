

import csv
import imp
import logging
from typing import List
from datetime import datetime
import re
import io
import pandas as pd
import boto3
import json


# read all jsons and load into csv


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




stuff = s3.list_objects(Bucket  = s3_bucket_name)

contents = [i['Key'] for i in stuff['Contents']]


data_dict = {}

for i in contents:
    print(i)

    response = s3.get_object(Bucket=s3_bucket_name, Key= i)


    book_pages = json.loads(response['Body'].read().decode('utf-8'))

    books_dfs = {}

    for cato in book_pages['data'].keys():
        print(cato)
        cato_df = pd.DataFrame.from_dict(book_pages['data'][cato], orient='index')
        cato_df['catagory'] = cato

        books_dfs[cato] = cato_df

    day_df = pd.concat(books_dfs.values(), ignore_index=True)
    day_df['date'] = book_pages['date']

    data_dict[i] = day_df





all_data = pd.concat(data_dict.values(), ignore_index=True)



with io.StringIO() as csv_buffer:
    all_data.to_csv(csv_buffer, index=False)

    response = s3.put_object(
        Bucket=s3_bucket_name, Key="books.csv", Body=csv_buffer.getvalue()
    )

    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        logging.info(f"Successful S3 put_object response. Status - {status}")
    else:
        logging.info(f"Unsuccessful S3 put_object response. Status - {status}")
