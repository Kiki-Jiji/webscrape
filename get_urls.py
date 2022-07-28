import os
import requests
from bs4 import BeautifulSoup
import logging
import json

from envvars import set_envars

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

def get_top_level_cats():
    url = "https://www.amazon.co.uk/best-sellers-books-Amazon/zgbs/books/ref=zg_bs_unv_books_1_91_1"

    pg = get_webpage(url)

    cats = pg.find_all('div', {'class' : '_p13n-zg-nav-tree-all_style_zg-browse-group__88fbz'})

    all_cats = [i for i in [i for i in cats]][1]

    catagorys = {
        'root' :  "https://www.amazon.co.uk"
    }

    for i in range(len(all_cats)):

        c = [i for i in all_cats.children][i]

        d = [i for i in c][0]

        href = d.attrs['href']

        name = [i for i in [i for i in c][0]][0]

        catagorys[name] = href

    return catagorys

def get_sub_catagories(url, subsub = False):

    pg = get_webpage(url)

    cats = pg.find_all('div', {'class' : '_p13n-zg-nav-tree-all_style_zg-browse-group__88fbz'})

    all_cats = [i for i in [i for i in cats]][1]

    catagorys = {}

    all_cats = [i for i in all_cats][1]

    if subsub:
        all_cats = [i for i in all_cats][1]

    for i in range(len(all_cats)):
        
        c = [i for i in all_cats.children][i]

        d = [i for i in c][0]

        href = d.attrs['href']

        name = [i for i in [i for i in d]][0]

        catagorys[name] = href

    return catagorys




def get_subsub_catagories(sub_cats, root):

    # manual define what subsub to look at
    # use all to go through allsub cats
    subsubs = {
        'Science Fiction & Fantasy': "all",
        'Romance': ['Historical Romance']
    }

    subsub_data = {}

    for sub in subsubs.keys():
        data = {}
        if subsubs[sub] == "all":
            for i in sub_cats[sub].keys():
                suburl = root + sub_cats[sub][i]
                data[i] = get_sub_catagories(suburl, subsub=True)
        else:
            for i in subsubs[sub]:
                suburl = root + sub_cats[sub][i]
                data[i] = get_sub_catagories(suburl, subsub = True)
        subsub_data[sub] = data

    return subsub_data


################################
# main

def main():
    """
    get catagories and saves them as catagories.json
    """

    set_envars()

    catagorys = get_top_level_cats()
    root = catagorys['root']

    sub_cats = {}
    for c in catagorys:
        if c == 'root': continue
        url = root + catagorys[c]

        sub_cats[c] = get_sub_catagories(url)

    subsub_cats =get_subsub_catagories(sub_cats, root)

    all_cats = {
        'top_level' : catagorys,
        'sub_domains': sub_cats,
        'subsub_cats': subsub_cats
    }

    try:
        with open('catagories.json', 'w') as f:
            json.dump(all_cats, f)
    except:
        print("failed to save")

    cat_count = len(all_cats['top_level'])
    for i in all_cats['sub_domains']:
        cat_count += len(all_cats['sub_domains'][i])

    print(f'The number of top level catagories is {len(all_cats["top_level"])}')
    print(f'The total number of catagories is {cat_count}')



main()

############
# eda

# with open('catagories.json') as f:
#     cats = json.load(f)


# cat_count = len(cats['top_level'])
# for i in cats['sub_domains']:
#     cat_count += len(cats['sub_domains'][i])

# print(f'The number of top level catagories is {len(all_cats["top_level"])}')
# print(f'The total number of catagories is {cat_count}')

def cats_urls():

    # the original urls
    # move away to using json cats
    urls = {
            'UK_Hist_Romance': 'https://www.amazon.co.uk/Best-Sellers-Kindle-Store-Historical-Romance/zgbs/digital-text/362727031/ref=zg_bs_unv_digital-text_4_3507148031_2',
            'UK_Reg Romance': 'https://www.amazon.co.uk/Best-Sellers-Kindle-Store-Regency-Historical-Romance/zgbs/digital-text/3507148031/ref=zg_bs_nav_digital-text_4_362727031',
            'US_Hist_Romance': 'https://www.amazon.com/Best-Sellers-Kindle-Store-Historical-Romance/zgbs/digital-text/158571011/ref=zg_bs_unv_digital-text_4_158573011_2',
            'US_Reg_Romance' : 'https://www.amazon.com/Best-Sellers-Regency-Historical-Romance/zgbs/digital-text/158573011',
            'UK_Womens_Fiction' : 'https://www.amazon.co.uk/Best-Sellers-Kindle-Store-Womens-Fiction/zgbs/digital-text/4542772031/ref=zg_bs_nav_digital-text_3_362270031',
            'UK_Womens_Romance_Fiction': 'https://www.amazon.co.uk/Best-Sellers-Kindle-Store-Womens-Romance-Fiction/zgbs/digital-text/4542787031/ref=zg_bs_nav_digital-text_4_4542772031',
            'US_Womens_Fiction' : 'https://www.amazon.com/Best-Sellers-Kindle-Store-Womens-Fiction/zgbs/digital-text/6190492011/ref=zg_bs_nav_digital-text_3_157028011',
            'US_Womens_Rom_Fiction' : 'https://www.amazon.com/Best-Sellers-Kindle-Store-Womens-Romance-Fiction/zgbs/digital-text/7588898011/ref=zg_bs_nav_digital-text_4_6190492011',
            'US_Gothic_Romance': 'https://www.amazon.com/gp/bestsellers/digital-text/6487830011/ref=pd_zg_hrsr_digital-text',
            'US_Rom_Com': 'https://www.amazon.com/Best-Sellers-Kindle-Store-Romantic-Comedy/zgbs/digital-text/6487841011/ref=zg_bs_nav_digital-text_3_6487830011', 
            'US_Holiday_Romance': 'https://www.amazon.com/Best-Sellers-Kindle-Store-Holiday-Romance/zgbs/digital-text/6487831011/ref=zg_bs_nav_digital-text_3_6487841011',
            'US_Contemporary_Romance': 'https://www.amazon.com/Best-Sellers-Kindle-Store-Contemporary-Romance/zgbs/digital-text/158568011/ref=zg_bs_nav_digital-text_3_6487831011',
            'US_Tudor_Romance': 'https://www.amazon.com/Best-Sellers-Kindle-Store-Tudor-Romance/zgbs/digital-text/14530455011/ref=zg_bs_nav_digital-text_4_158571011',
            'US_Renaissance_Romance': 'https://www.amazon.com/Best-Sellers-Kindle-Store-Renaissance-Historical-Romance/zgbs/digital-text/17744543011/ref=zg_bs_nav_digital-text_4_14530455011',
        }

    def add_root(dic: dict, root: str, country: str = "UK") -> dict:
        padded = {}
        for k in dic.keys():
            if k == "root": continue
            padded[f'{country} {k}'] =  root +dic[k]
        return padded 


    with open('catagories.json') as f:
        cats = json.load(f)


    root = cats['top_level']['root']

    top_level = add_root(cats['top_level'], root)

    all_urls = {**urls, **top_level}

    return all_urls
