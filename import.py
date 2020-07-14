import csv
  # Same setup code as before.
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL")) # database engine object from SQLAlchemy that manages connections to the database
                                                    # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
                                                    # database are kept separate

def main():
     db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL)")
     f = open("books.csv")
     reader = csv.reader(f)
     for isbn, title, author, year in reader: # loop gives each column a name
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                  {"isbn": isbn, "title": title, "author": author, "year": year}) # substitute values from CSV line into SQL command, as per this dict
        print(f"Added books with book information isbn = {isbn} title = {title} author = {author} year = {year}.")
     db.commit()
if __name__ == '__main__':
    main()