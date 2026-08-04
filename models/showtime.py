from database.db import db
from datetime import datetime

class Showtime(db.Model):
    __tablename__ = 'showtimes'
    
    id = db.Column(db.Integer, primary_key=True)
    auditorium_id = db.Column(db.Integer, db.ForeignKey('auditoriums.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    showtime = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    # Relationship to Seats
    seats = db.relationship('Seat', backref='showtime', lazy=True)
    
    def __repr__(self):
        return f"<Showtime {self.id} - Movie {self.movie_id}>"