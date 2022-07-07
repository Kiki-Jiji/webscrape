
import json
import pandas as pd
import os

from utils import match_cover_catagory, find_matching_catagory, get_catagories, move_cover

assert os.path.exists("existing.json"), "existing.json must exist in same directory"
assert os.path.exists("books.csv"), "books.csvmust exist in same directory"
assert os.path.isdir("covers"), "covers directory must exist in same directory"



with open("existing.json") as f:
    existing = json.load(f)

books = pd.read_csv("books.csv")
books = books[~books['catagory'].str.contains('http')]


cover_catagories =  match_cover_catagory(books, existing)


key = [i for i in cover_catagories.keys()][10]


current_catagories = get_catagories(cover_catagories)


catagories = {
    'history' : [
        'UK_Hist_Romance',
        'US_Hist_Romance',
        'US_Gothic_Romance',
        'US_Tudor_Romance',
        'US_Renaissance_Romance',
        'UK_Reg Romance',
        'US_Reg_Romance',
    ],
    'modern' : [
        'UK_Womens_Romance_Fiction',
        'US_Womens_Rom_Fiction',
        'US_Womens_Fiction',
        'US_Holiday_Romance',
        'UK_Womens_Fiction',
        'US_Contemporary_Romance',
        'US_Rom_Com',
    ]

}


covers = os.listdir("covers")

for key in cover_catagories:

    if key == '6545d468-dbb7-11ec-bf86-d3492d711bc0':
        print("accidently deleted this file, whoopseys")
        continue

    assert key in covers, "file doesnlt seem to exist"
    cats = cover_catagories[key]

    if isinstance(cats, str):
        cats = [cats]

    for cat in cats:

        catagory = find_matching_catagory(cat, catagories)

        assert catagory is not None, "no matching catagory was found"

        move_cover(catagory, key)

