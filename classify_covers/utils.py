
import os
from PIL import Image

def match_cover_catagory(books, existing):

    cover_cats = {}

    for exp in existing.keys():

        author = books[books['author_txt'] == existing[exp]['author']]

        author_book = author[author['book_title_txt'] == existing[exp]['title']]

        catagories = author_book['catagory'].unique()

        if len(catagories) == 1:
            cover_cats[exp] = catagories[0]
        elif len(catagories) > 1:
            cover_cats[exp] = list(catagories)
        else:
            raise Exception("whoops")

    return cover_cats

def move_cover(catagory, key):
    root = "cover_catagories"

    if not os.path.isdir(root):
        print("Creating root")
        os.mkdir(root)

    catagory_path = root + "/" + catagory

    if not os.path.isdir(catagory_path):
        print(f"Creating {catagory_path}")
        os.mkdir(catagory_path)

    img_path = "covers/" + key

    assert os.path.isfile(img_path), 'img doesnt exist'

    im = Image.open(img_path)

    width = im.width
    height = im.height

    white_space = 257

    im2 = im.crop(
        (white_space, 0, width - white_space, height)
    )

    im2.save(catagory_path + "/" + key + ".png")


def find_matching_catagory(catagory, catagories):
    for cg in catagories:
        if catagory in catagories[cg]:
            return cg

def get_catagories(cover_catagories):
        
    cats = []

    for i in cover_catagories:

        catay = cover_catagories[i]

        if isinstance(catay, str):
                catay = [catay]

        for x in catay:
            if x not in cats:
                cats.append(x)
    return cats
