from database.db import db

class Auditorium(db.Model):
    __tablename__ = 'auditoriums'
    
    id = db.Column(db.Integer, primary_key=True)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'), nullable=False)
    auditorium_type = db.Column(db.String(100), nullable=False)  # e.g., "IMAX", "Standard", "Premium"
    seat_capacity = db.Column(db.Integer, nullable=False)
    
    # Relationship to Showtimes
    showtimes = db.relationship('Showtime', backref='auditorium', lazy=True)
    
    def __repr__(self):
        return f"<Auditorium {self.id} - {self.auditorium_type}>"