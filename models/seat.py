"""
Seat Model
 Date: 8/4/26
 Programmers: Mark and Chutiwat

Represents individual seats in an auditorium for a specific showtime.

Algorithm Notes:

    Lock Mechanism: Seats are locked temporarily (5 minuites) when added to cart to prevent overselling. Locks automatically expire,
    allowing the seat to be available for other users if the cart is not checked out.
"""
from database.db import db
from datetime import datetime, timedelta

class Seat(db.Model):
    """
    Seat Model handling seat availability, booking staus, and temporary locking for cart operations for individual theatre seats.

    Attributes:

        id (int): The primary key for the seat.
        showtime_id (int): The foreign key linking to Showtime.
        seat_number (str): The alphanumeric seat identifier.
        is_booked (bool): Indicates if the seat is permanently purchased.
        is_locked (bool): Indicates if the seat is temporarily held in a cart.
        locked_by_user (int): The ID of the customer currently holding the seat.
        lock_expires_at (datetime): The exact time the temporary lock expires.
    """
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    showtime_id = db.Column(db.Integer, db.ForeignKey('showtimes.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)  # e.g., "A1", "B5"
    is_booked = db.Column(db.Boolean, default=False)  # Permanently booked
    is_locked = db.Column(db.Boolean, default=False)  # Temporarily locked (in cart)
    locked_by_user = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)  # User who locked it
    lock_expires_at = db.Column(db.DateTime, nullable=True)  # When lock expires (5 min from now)
    
    def lock_seat(self, user_id, lock_duration_minutes=5):
        """
        Places a temporary hold on the seat for a specified user
            
        Args:

            user_id (int): The ID of the user locking the seat.
            lock_duration_minutes (int): The hold duration in minutes, defaulting to 5.
        """
        self.is_locked = True
        self.locked_by_user = user_id
        self.lock_expires_at = datetime.now() + timedelta(minutes=lock_duration_minutes)
    
    def unlock_seat(self):
        """
        Releases the temporary lock on the seat, making it available again.
        """
        self.is_locked = False
        self.locked_by_user = None
        self.lock_expires_at = None
    
    def is_lock_expired(self):
        """
        Checks if temporary hold duration has passed.
        
        Returns:

            bool: True if the lock has expired, False otherwise.
        """
        if self.lock_expires_at and datetime.now() > self.lock_expires_at:
            return True
        return False
    
    def __repr__(self):
        """Returns a string representation of Seat."""
        return f"<Seat {self.seat_number}>"