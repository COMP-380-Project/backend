"""
Cart Model
Date: 8/4/26
Programmers: Mark and Chutiwat

Represents a shopping cart for customers containing selected tickets.
"""
from database.db import db
from datetime import datetime

class Cart(db.Model):
    """
    Cart Model handling adding/removing tickets and calculating subtotals for customer shopping carts.

    Attributes:

        id (int): The primary key for the cart.
        customer_id (int): The foreign key linking to Customer.
        subtotal (float): The current total price, defaulting to 0.0.
        created_at (datetime): The timestamp when the cart was created.
    """
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    subtotal = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship to Tickets
    tickets = db.relationship('Ticket', backref='cart', lazy=True)
    
    def calculate_subtotal(self):
        """Calculate total price of all tickets in cart
            
            Returns:

                float: Sum of all ticket prices."""
        self.subtotal = sum(ticket.price for ticket in self.tickets)
        return self.subtotal
    
    def add_ticket(self, ticket):
        """Add ticket to cart

            Args:

                ticket(Ticket): Ticket object to add."""
        self.tickets.append(ticket)
        self.calculate_subtotal()
    
    def remove_ticket(self, ticket):
        """Remove ticket from cart
            
            Args:

                ticket(Ticket): Ticket object to remove."""
        self.tickets.remove(ticket)
        self.calculate_subtotal()
    
    def __repr__(self):
        """Returns a string representation of Cart."""
        return f"<Cart {self.id} - Customer {self.customer_id}>"