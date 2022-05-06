# webscrape

## Webscrape

Deploy lambda folder top AWS lambda function. 

Becuase AWS lambda doesn't support BeautifulSoup or Requests these need to be bundled with the function. 

Make any changes to the `lambda_function.py` in lambda, this is what is ran when the lambda function is invoked. Any libraries need to be installed INTO the lambda folder. e.g

```bash
# to install requests navigate to lambda folder and run
pip install requests -t ./
```

* requests
* bs4


Ins


The contents of the lambda folder then need to be zipped. 

```bash
zip -r zip.zip .
```

> Note this is the contents (everything inside lambda) NOT the actual folder

Create a lambda function and select the upload from zip option.

Create in the lambda configuration three envrioment variables

* proxy_api
* secret
* access_key

proxy_api is used for the webscraping. The service used is [web scrape api](https://www.webscrapingapi.com/). Create an account, get an API access key, this is the proxy_api

secret and access_key are AWS keys for an S3 bucket. The scraped web page is auto uploaded to an S3 bucket.

## bookApp

This is an RShiny WebApp. Currentl in development. 

In bookApp directory run `run_dev.R` to run the dev version.

```{r}
Rscript run_dev.R
```