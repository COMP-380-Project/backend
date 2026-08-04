from database.db import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    number_of_tickets = db.Column(db.Integer, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(50), default='confirmed')  # confirmed, cancelled
    total_price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f"<Booking {self.id} - User {self.user_id}>"