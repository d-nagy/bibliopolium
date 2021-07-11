import sqlite3
import pandas as pd
import bcrypt
from app import db, create_app

ratings_df = pd.read_csv('./goodbooks/ratings.csv').head(10000)
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
res = res.drop([
    'goodreads_book_id', 'best_book_id', 'work_id',
    'books_count', 'isbn', 'isbn13', 'authors', 'original_publication_year',
    'original_title', 'language_code', 'average_rating',
    'ratings_count', 'work_ratings_count', 'work_text_reviews_count',
    'ratings_1', 'ratings_2', 'ratings_3', 'ratings_4', 'ratings_5',
    'small_image_url', 'count'
], axis=1)

res = pd.merge(res, tags_df, on='tag_id').drop('tag_id', axis=1)
res.rename({'book_id': 'id', 'tag_name': 'genre'}, axis=1, inplace=True)
res.drop_duplicates('id', inplace=True)

user_ids = [int(i) for i in ratings_df.user_id.unique()]
usernames = [f'user{i}' for i in user_ids]
password = bcrypt.hashpw(('letmein').encode(), bcrypt.gensalt()).decode()
passwords = [password for i in user_ids]

rating_values = [
    tuple([int(v) for v in row.values])
    for _, row in ratings_df.iterrows()
]
book_values = [tuple([v for v in row.values]) for _, row in res.iterrows()]
user_values = [values for values in zip(user_ids, usernames, passwords)]


db.drop_all(app=create_app())
db.create_all(app=create_app())

conn = sqlite3.connect('./test.db')
c = conn.cursor()

c.executemany(
    "INSERT INTO rating (user_id, book_id, rating) VALUES (?, ?, ?)",
    rating_values
)
c.executemany("INSERT INTO book VALUES (?, ?, ?, ?)", book_values)
c.executemany("INSERT INTO user VALUES (?, ?, ?)", user_values)

conn.commit()
conn.close()
