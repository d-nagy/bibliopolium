from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(50))

class Rating(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), primary_key=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
