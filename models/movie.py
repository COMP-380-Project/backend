"""
Movie Model
* **Date:** 8/4/26
* **Programmers:** Mark and Chutiwat

Represents movie in the booking system.
"""
from database.db import db

class Movie(db.Model):
    """
    Movie Model storing information about the movie

    Attributes:

        id (int): The primary key for the movie.
        title (str): The title of the movie.
        genre (str): The genre of the movie.
        duration (int): The runtime of the movie in minutes.
        description (str): The description of the movie.
        rating (float): The current rating of the movie, defaulting to 0.0.
        cast (str): A comma-separated list of actors.
        poster_url (str): The URL link to the movie's promotional poster.
        """
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    cast = db.Column(db.String(500), nullable=False)  # comma-separated actors
    poster_url = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        """Returns a string representation of Movie."""
        return f"<Movie {self.title}>"