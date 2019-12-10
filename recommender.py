import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from scipy.sparse.linalg import svds

# Get data from database
engine = create_engine('sqlite:///./test.db')
conn = engine.connect()
ratings_df = pd.read_sql_table('rating', con=conn)
books_df = pd.read_sql_table('book', con=conn)
conn.close()
engine.dispose()


# Create ratings matrix
R_df = ratings_df.pivot(index='user_id', columns='book_id', values='rating').fillna(0)

# Normalize the matrix
R = R_df.values
user_ratings_mean = np.mean(R, axis=1)
R_demeaned = R - user_ratings_mean.reshape(-1, 1)

# Perform Singular Value Decomposition
U, sigma, Vt = svds(R_demeaned, k=50)
sigma = np.diag(sigma) # Turn sigma into a diagonal matrix

# Create predictions matrix
all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
preds_df = pd.DataFrame(all_user_predicted_ratings, index=R_df.index, columns=R_df.columns)


def recommend_books(predictions_df, user_id, books_df, original_ratings_df, num_recommendations=5):
    # Get and sort the user's predictions
    sorted_user_predictions = predictions_df.loc[user_id].sort_values(ascending=False)

    # Get the user's data and merge in the book information
    user_data = original_ratings_df[original_ratings_df.user_id == (user_id)]
    user_full = (user_data.merge(books_df, how='left', left_on='book_id', right_on='book_id').
                    sort_values(['rating'], ascending=False)
                )

    print(f'User {user_id} has alread rated {user_full.shape[0]} books.')
    print(f'Recommending the highest {num_recommendations} predicted ratings books not already rated.')

    # Recommend the highest predicted rating books that the user hasn't seen yet.
    recommendations = (books_df[~books_df['book_id'].isin(user_full['book_id'])].
        merge(pd.DataFrame(sorted_user_predictions).reset_index(), how='left',
            left_on='book_id',
            right_on='book_id').
        rename(columns={user_id: 'Predictions'}).
        sort_values('Predictions', ascending=False).
                    iloc[:num_recommendations, :-1]
                    )

    return user_full, recommendations

if __name__ == '__main__':
    already_rated, predictions = recommend_books(preds_df, 1, books_df, ratings_df, 10)

    print()
    print(already_rated.head(10))
    print()
    print(predictions.head(10))
