from database.db import db
from datetime import datetime

class Cart(db.Model):
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    subtotal = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship to Tickets
    tickets = db.relationship('Ticket', backref='cart', lazy=True)
    
    def calculate_subtotal(self):
        """Calculate total price of all tickets in cart"""
        self.subtotal = sum(ticket.price for ticket in self.tickets)
        return self.subtotal
    
    def add_ticket(self, ticket):
        """Add ticket to cart"""
        self.tickets.append(ticket)
        self.calculate_subtotal()
    
    def remove_ticket(self, ticket):
        """Remove ticket from cart"""
        self.tickets.remove(ticket)
        self.calculate_subtotal()
    
    def __repr__(self):
        return f"<Cart {self.id} - Customer {self.customer_id}>"