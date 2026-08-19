"""
Showtime Model
 Date: 8/4/26
 Programmers: Mark and Chutiwat

Represents a specific showing of a movie at a particular time.
Links movies to auditoriums with date/time and pricing information.
"""
from database.db import db
from datetime import datetime

class Showtime(db.Model):
    """
    Showtime Model storing information for movie showtimes

    Attributes:

        id (int): The primary key for the showtime.
        auditorium_id (int): The foreign key linking to Auditorium.
        movie_id (int): The foreign key linking to the Movie.
        showtime (datetime): The scheduled date and time of the showing.
        price (float): The ticket price for this showing.
    """
    __tablename__ = 'showtimes'
    
    id = db.Column(db.Integer, primary_key=True)
    auditorium_id = db.Column(db.Integer, db.ForeignKey('auditoriums.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    showtime = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    
    # Relationship to Seats
    seats = db.relationship('Seat', backref='showtime', lazy=True)
    movie = db.relationship('Movie', backref='showtimes')
    
    def __repr__(self):
        """Returns string representation of Showtime."""
        return f"<Showtime {self.id} - Movie {self.movie_id}>"