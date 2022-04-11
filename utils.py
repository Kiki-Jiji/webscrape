
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
