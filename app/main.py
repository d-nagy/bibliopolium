from flask import Blueprint, render_template, request, url_for, jsonify, redirect
from flask_login import login_required, current_user
from sqlalchemy import and_
from . import db
from .models import Book, Rating
from .recommender import get_recommendations

main = Blueprint('main', __name__)

def get_ratings(books):
    ratings = []
    for book in books:
        rating_values = [r.rating for r in book.users.all()]
        num_ratings = len(rating_values)
        mean_rating = 0 if num_ratings < 1 else round(sum(rating_values) / num_ratings, 2)

        user_rating = 0
        if current_user.is_authenticated:
            user_rating = Rating.query.filter(and_(Rating.user_id==current_user.user_id, Rating.book_id==book.book_id)).first()
            if user_rating is None:
                user_rating = 0
            else:
                user_rating = user_rating.rating

        ratings.append((num_ratings, mean_rating, int(user_rating)))

    return ratings

@main.route('/')
@main.route('/index')
def index():
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)

    if search == '':
        books = Book.query.paginate(page, 24, False)
    else:
        books = Book.query.filter(Book.title.like(f'%{search}%')).paginate(page, 24, False)

    ratings = get_ratings(books.items)

    next_url = url_for('main.index', page=books.next_num, search=search) if books.has_next else None
    prev_url = url_for('main.index', page=books.prev_num, search=search) if books.has_prev else None

    return render_template('index.html', books=books.items, ratings=ratings,
                            page=page, search=search, next_url=next_url,
                            prev_url=prev_url, num_pages=books.pages)

@main.route('/recommended')
@login_required
def recommended():
    if current_user.books.count() > 0:
        recommendations = get_recommendations(current_user.user_id, db.engine, 12)
    else:
        sql = ("SELECT book_id "
               "FROM rating "
               "GROUP BY book_id "
               "HAVING COUNT(*) > 10 "
               "ORDER BY AVG(rating) DESC "
               "LIMIT 12;")
        query_result = db.engine.execute(sql)
        recommendations = [row[0] for row in query_result]

    books = [Book.query.filter_by(book_id=book_id).first() for book_id in recommendations]
    ratings = get_ratings(books)

    return render_template('recommended.html', books=books, ratings=ratings,
                            num_pages=1)

@main.route('/profile')
@login_required
def profile():
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)

    if search == '':
        user_ratings = current_user.books.paginate(page, 24, False)
        books = [r.book for r in user_ratings.items]
        num_pages = user_ratings.pages
        has_next = user_ratings.has_next
        has_prev = user_ratings.has_prev
        next_num = user_ratings.next_num
        prev_num = user_ratings.prev_num
    else:
        user_ratings = current_user.books.all()
        all_books = [r.book for r in user_ratings if search.lower() in r.book.title.lower()]
        num_pages = ((len(all_books)-1) // 24) + 1
        l = 24 * (page - 1)
        h = l + 24
        books = all_books[l:h]
        has_next = page < num_pages
        has_prev = page > 1 and num_pages > 1
        next_num = page + 1
        prev_num = page - 1

    ratings = get_ratings(books)

    next_url = url_for('main.profile', page=next_num, search=search) if has_next else None
    prev_url = url_for('main.profile', page=prev_num, search=search) if has_prev else None

    return render_template('profile.html', books=books, ratings=ratings,
                            page=page, search=search, num_pages=num_pages,
                            next_url=next_url, prev_url=prev_url)

@main.route('/rate_book', methods=['POST'])
@login_required
def rate_book():
    book_id = int(request.form.get('book_id'))
    rating = int(request.form.get('rating'))
    next_url = request.form.get('next_url')

    user_rating = Rating.query.filter(and_(Rating.user_id==current_user.user_id, Rating.book_id==book_id)).first()
    if user_rating is not None:
        if rating == 0:
            # Delete rating
            db.session.delete(user_rating)
        else:
            # Update rating
            user_rating.rating = rating
    else:
        if rating != 0:
            # Add new rating
            new_rating = Rating(user_id=current_user.user_id, book_id=book_id, rating=rating)
            db.session.add(new_rating)

    db.session.commit()

    return redirect(next_url)

@main.route('/search_index')
def search_index():
    term = request.args.get('term')
    books = Book.query.filter(Book.title.like(f'%{term}%')).all()

    titles = [book.title for book in books]

    return jsonify(titles)

@main.route('/search_profile')
def search_profile():
    term = request.args.get('term')
    user_ratings = current_user.books.all()

    books = [r.book for r in user_ratings]
    titles = [book.title for book in books if term.lower() in book.title.lower()]

    return jsonify(titles)
