"""
Ticket Model
* **Date:** 8/4/26
* **Programmers:** Mark and Chutiwat

Represents a ticket for a specific movies showing at a specific seat
"""
from database.db import db

class Ticket(db.Model):
    """
    Ticket Model storing information for movie tickets

    Attributes:

        id (int): The primary key for the ticket.
        cart_id (int): The foreign key linking to the associated Cart.
        showtime_id (int): The foreign key linking to the specific Showtime.
        seat_id (int): The foreign key linking to the assigned Seat.
        ticket_type (str): The type of ticket (Adult, Kid, Senior).
        price (float): The price of this specific ticket.
    """
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    showtime_id = db.Column(db.Integer, db.ForeignKey('showtimes.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)
    ticket_type = db.Column(db.String(20), nullable=False)  # Adult, Kid, Senior
    price = db.Column(db.Float, nullable=False)
    
    # Relationships
    showtime = db.relationship('Showtime', backref='tickets')
    seat = db.relationship('Seat', backref='tickets')
    
    def __repr__(self):
        """Returns a string representation of Ticket."""
        return f"<Ticket {self.id} - {self.ticket_type}>"