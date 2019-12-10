import bcrypt
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from . import db
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    password = request.form.get('password')

    # Try and find a user with the given username
    user = User.query.filter_by(username=username).first()

    # If user exists, redirect to signup page to try again
    if user:
        flash('Username already exists')
        return redirect(url_for('auth.signup'))

    # Otherwise create the new user
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    new_user = User(username=username, password=password_hash)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    # Try and find a user with the given username
    user = User.query.filter_by(username=username).first()

    # Check that the user exists and the password is correct
    if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
        flash('Please check your login details and try again')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))
