"""
Order Model
* **Date:** 8/4/26
* **Programmers:** Mark and Chutiwat

Represents a confirmed ticket order after payment.
"""
from database.db import db
from datetime import datetime

class Order(db.Model):
    """
    Order Model tracking order status and links to payment information for confirmed orders.

    Attributes:

        id (int): The primary key for the order.
        customer_id (int): The foreign key linking to Customer.
        payment_id (int): The foreign key linking to Payment.
        cart_id (int): The foreign key linking to the Cart that produced this order.
        total_amount (float): The final price charged.
        order_status (str): The status of the order (confirmed, cancelled)
        created_at (datetime): The timestamp when the order was created.
    """
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    order_status = db.Column(db.String(50), default='confirmed')  # confirmed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    payment = db.relationship('Payment', backref='order')
    customer = db.relationship('Customer', backref='orders')
    cart = db.relationship('Cart', backref='orders')

    def get_seat_number(self):
        """Get all seat numbers for this order"""
        if not self.cart:
            return []
        return [ticket.seat.seat_number for ticket in self.cart.tickets]

    def get_auditorium(self):
        """Get auditorium for this order"""
        if not self.cart or not self.cart.tickets:
            return None
        return self.cart.tickets[0].showtime.auditorium

    def get_showtime(self):
        """Get showtime for this order"""
        if not self.cart or not self.cart.tickets:
            return None
        return self.cart.tickets[0].showtime

    def __repr__(self):
        """Returns a string representation of Order."""
        return f"<Order {self.id} - Customer {self.customer_id}>"