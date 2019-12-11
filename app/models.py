from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    books = db.relationship('Rating', back_populates='user', lazy='dynamic')

    def get_id(self):
        return self.user_id

class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(50))

    users = db.relationship('Rating', back_populates='book', lazy='dynamic')

class Rating(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), primary_key=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    book = db.relationship('Book', back_populates='users')
    user = db.relationship('User', back_populates='books')
