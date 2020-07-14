import os
import requests
from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "MySecretKey"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():
    session.pop("USERNAME", None)
    error = None
    if request.method == 'POST':
        user_name = request.form.get("username")
        pass_word = request.form.get("password")
        if db.execute("SELECT * FROM users WHERE username = :username and password = :password", {"username": user_name, "password": pass_word}).rowcount == 0:
            error = 'Invalid Credentials. Please try again.'
        else:
            session["USERNAME"] = user_name
            return redirect(url_for('search'))
    return render_template("index.html", error=error)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/process_new_user", methods = ["POST"])
def process_new_user():
    user_name = request.form.get("username")
    password = request.form.get("password")
    first = request.form.get("first_name")
    last = request.form.get("last_name")
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": user_name}).rowcount == 1:
        error = "Username taken!"
        return render_template("register.html", error = error)
    db.execute("INSERT INTO users (username, password, first_name, last_name) VALUES ( :username, :password, :first_name, :last_name)", {"username": user_name, "password": password, "first_name": first, "last_name": last})
    db.commit();
    return render_template("successful_registration.html")

@app.route("/search")
def search():
    if not session.get("USERNAME") is None:
        username = session.get("USERNAME")
        return render_template("search.html", user=username)
    else:
        return render_template("invalid.html")

@app.route("/search_results", methods=["POST"])
def results():
    if request.method == 'POST':
        search_category = request.form['category']
        search_value = request.form.get("credential")
        query = "%" + search_value + "%"
        query = query.title()
        if search_category == "isbn":
            rows = db.execute("SELECT * FROM books WHERE isbn LIKE :query", {"query": query})
        elif search_category == "title":
            rows = db.execute("SELECT * FROM books WHERE title LIKE :query", {"query": query})
        elif search_category == "author":
            rows = db.execute("SELECT * FROM books WHERE author LIKE :query", {"query": query})
        else:
            rows = db.execute("SELECT * FROM books WHERE year LIKE :query", {"query": query})
        if rows.rowcount == 0:
            return render_template("empty.html", query= search_value)
        else:
            books = rows.fetchall()
            return render_template("results.html", query = search_value, books = books)

@app.route("/books/<name>")
def books(name):
    session.pop("BOOK_TITLE", None)
    book = db.execute("SELECT * FROM books WHERE title = :title", {"title": name}).fetchone()
    if book is None:
          return render_template("empty.html")
    reviews = db.execute("SELECT reviews.review_content, reviews.rating, users.first_name, users.last_name FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
    key = "fGrFbqWPP4AtDCWp7PYAQQ"
    isbn = book.isbn
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
    data = res.json()
    average_rating = data['books'][0]['average_rating']
    num_ratings = data['books'][0]['ratings_count']
    return render_template("books.html", book = book, reviews = reviews, average_rating = average_rating, num_ratings = num_ratings)

@app.route("/review", methods=["POST"])
def review():
    if request.method == 'POST':
        rating_str = request.form['rating']
        if rating_str == "one":
            rating = 1
        elif rating_str == "two":
            rating = 2
        elif rating_str == "three":
            rating = 3
        elif rating_str == "four":
            rating = 4
        else:
            rating = 5
        book_isbn = request.form.get("book_isbn")
        review = request.form.get("review_content")
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
        book_id = book.id
        if not session.get("USERNAME") is None:
            username = session.get("USERNAME")
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        user_id = user.id
        if db.execute("SELECT * FROM reviews WHERE book_id = :book_id and user_id = :user_id", {"book_id": book_id, "user_id": user_id}).rowcount == 1:
            message = 'Your review was not added because you already reviewed this book. Please select another one!'
        else:
            message = "Thank you for your review to the book titled " + book.title
            db.execute("INSERT INTO reviews (review_content, rating, book_id, user_id) VALUES ( :review_content, :rating, :book_id, :user_id)",
            {"review_content": review, "rating": rating, "book_id": book_id, "user_id": user_id})
            db.commit();
        return render_template("add_review.html", message = message)



@app.route("/log_out")
def log_out():
    session.pop("USERNAME", None)
    return redirect(url_for("index"))
