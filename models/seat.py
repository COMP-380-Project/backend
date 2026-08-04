from database.db import db
from datetime import datetime, timedelta

class Seat(db.Model):
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    showtime_id = db.Column(db.Integer, db.ForeignKey('showtimes.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)  # e.g., "A1", "B5"
    is_booked = db.Column(db.Boolean, default=False)  # Permanently booked
    is_locked = db.Column(db.Boolean, default=False)  # Temporarily locked (in cart)
    locked_by_user = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)  # User who locked it
    lock_expires_at = db.Column(db.DateTime, nullable=True)  # When lock expires (5 min from now)
    
    def lock_seat(self, user_id, lock_duration_minutes=5):
        """Lock seat for a user for X minutes"""
        self.is_locked = True
        self.locked_by_user = user_id
        self.lock_expires_at = datetime.now() + timedelta(minutes=lock_duration_minutes)
    
    def unlock_seat(self):
        """Unlock the seat"""
        self.is_locked = False
        self.locked_by_user = None
        self.lock_expires_at = None
    
    def is_lock_expired(self):
        """Check if lock has expired"""
        if self.lock_expires_at and datetime.now() > self.lock_expires_at:
            return True
        return False
    
    def __repr__(self):
        return f"<Seat {self.seat_number}>"