from flask import Blueprint, render_template, request, url_for
from flask_login import login_required, current_user
from . import db
from .models import Book
from .recommender import get_recommendations

main = Blueprint('main', __name__)

def get_ratings(books):
    ratings = []
    for book in books:
        rating_values = [r.rating for r in book.users.all()]
        num_ratings = len(rating_values)
        mean_rating = 0 if num_ratings < 1 else round(sum(rating_values) / num_ratings, 2)
        ratings.append((num_ratings, mean_rating))
    return ratings

@main.route('/')
@main.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    books = Book.query.paginate(page, 12, False)

    ratings = get_ratings(books.items)

    next_url = url_for('main.index', page=books.next_num) if books.has_next else None
    prev_url = url_for('main.index', page=books.prev_num) if books.has_prev else None

    return render_template('index.html', books=books.items, ratings=ratings,
                            page=page, next_url=next_url, prev_url=prev_url)

@main.route('/recommended')
@login_required
def recommended():
    recommendations = get_recommendations(current_user.user_id, db.engine, 12)
    books = [Book.query.filter_by(book_id=book_id).first() for book_id in recommendations]
    ratings = get_ratings(books)

    return render_template('recommended.html', books=books, ratings=ratings,
                            num_pages=1)

@main.route('/profile')
@login_required
def profile():
    page = request.args.get('page', 1, type=int)
    user_ratings = current_user.books.paginate(page, 12, False)

    books = [r.book for r in user_ratings.items]
    num_pages = user_ratings.pages
    ratings = get_ratings(books)

    next_url = url_for('main.profile', page=user_ratings.next_num) if user_ratings.has_next else None
    prev_url = url_for('main.profile', page=user_ratings.prev_num) if user_ratings.has_prev else None

    return render_template('profile.html', books=books, ratings=ratings,
                            page=page, num_pages=num_pages,
                            next_url=next_url, prev_url=prev_url)
