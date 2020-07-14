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
     db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, password VARCHAR NOT NULL, first_name VARCHAR NOT NULL, last_name VARCHAR NOT NULL)")
     db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, review_content VARCHAR NOT NULL, rating INTEGER NOT NULL, book_id INTEGER REFERENCEs books, user_id INTEGER REFERENCES users)")
     print("Creat two more tables")
     db.commit()
if __name__ == '__main__':
    main()
