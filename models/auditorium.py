"""
Auditorium Model
* **Date:** 8/4/26
* **Programmers:** Mark and Chutiwat

Represents a specific physical theatre room within a theatre.
Each auditorium can show different movies at different showtimes.
"""
from database.db import db

class Auditorium(db.Model):
    """
    Auditorium Model storing the physical characteristics of a single auditorium

    Attributes:

        id (int): The primary key for the auditorium.
        theatre_id (int): The foreign key linking to Theatre.
        auditorium_type (str): The type of auditorium (IMAX, Standard, Premium)
        seat_capacity (int): The total number of seats in auditorium.
    """
    __tablename__ = 'auditoriums'
    
    id = db.Column(db.Integer, primary_key=True)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'), nullable=False)
    auditorium_type = db.Column(db.String(100), nullable=False)  # e.g., "IMAX", "Standard", "Premium"
    seat_capacity = db.Column(db.Integer, nullable=False)
    
    # Relationship to Showtimes
    showtimes = db.relationship('Showtime', backref='auditorium', lazy=True)
    
    def __repr__(self):
        """Returns a string representation of Auditorium."""
        return f"<Auditorium {self.id} - {self.auditorium_type}>"