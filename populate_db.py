import sqlite3
import pandas as pd
import numpy as np
import bcrypt

ratings_df = pd.read_csv('./goodbooks/ratings.csv').head(5000)
books_df = pd.read_csv('./goodbooks/books.csv')
tags_df = pd.read_csv('./goodbooks/tags.csv')
book_tags_df = pd.read_csv('./goodbooks/book_tags.csv')
book_tags_df = book_tags_df[
    (book_tags_df.tag_id != 11557) &
    (book_tags_df.tag_id != 8717) &
    (book_tags_df.tag_id != 30574) &
    (book_tags_df.tag_id != 11743) &
    (book_tags_df.tag_id != 5207) &
    (book_tags_df.tag_id != 14017) &
    (book_tags_df.tag_id != 27199) &
    (book_tags_df.tag_id != 32989) &
    (book_tags_df.tag_id != 4949)]

res = pd.merge(books_df, book_tags_df, on='goodreads_book_id')
idx = res.groupby(['goodreads_book_id'])['count'].transform(max) == res['count']
res = res[idx]
res = res.drop(['goodreads_book_id', 'best_book_id', 'work_id',
       'books_count', 'isbn', 'isbn13', 'authors', 'original_publication_year',
       'original_title', 'language_code', 'average_rating',
       'ratings_count', 'work_ratings_count', 'work_text_reviews_count',
       'ratings_1', 'ratings_2', 'ratings_3', 'ratings_4', 'ratings_5', 'small_image_url','count'], axis=1)

res = pd.merge(res, tags_df, on='tag_id').drop('tag_id', axis=1)
res.rename({'book_id': 'id', 'tag_name': 'genre'}, axis=1, inplace=True)

user_ids = ratings_df.user_id.unique()
usernames = [f'user{i}' for i in user_ids]
passwords = [bcrypt.hashpw(str(i).encode(), bcrypt.gensalt())
             for i in user_ids]

data = {'id': user_ids, 'username': usernames, 'password': passwords}
users_df  = pd.DataFrame(data)

conn = sqlite3.connect('./test.db')
res.to_sql('books', con=conn, if_exists='replace', index=False)
ratings_df.to_sql('ratings', con=conn, if_exists='replace', index_label='id')
users_df.to_sql('users', con=conn, if_exists='replace', index=False)
conn.commit()
conn.close()
