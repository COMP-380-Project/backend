"""
Payment Model
* **Date:** 8/4/26
* **Programmers:** Mark and Chutiwat

Represents payment transactions for ticket orders.
"""
from database.db import db
from datetime import datetime

class Payment(db.Model):
    """
    Payment model handling financial transactions and payment records for payment processing.

    Attributes:

        id (int): The primary key for the payment.
        customer_id (int): The foreign key linking to Customer.
        amount (float): The total amount processed.
        payment_method (str): The method used (Credit Card, Debit Card, PayPal).
        payment_status (str): The transaction state (pending, completed, failed, refunded).
        payment_type (str): The user's checkout classification (Guest, Registered Memebr).
        created_at (datetime): The timestamp of the transaction.
    """
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # Credit Card, Debit Card, PayPal
    payment_status = db.Column(db.String(50), default='pending')  # pending, completed, failed, refunded
    payment_type = db.Column(db.String(50), nullable=False)  # Guest, Registered Member
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def process_payment(self):
        """Process the payment and updates status to 'completed'"""
        self.payment_status = 'completed'
    
    def verify_payment(self):
        """Verify if the payment transaction was successful
            
            Returns:

                bool: True if the payment status is 'completed'
        """
        return self.payment_status == 'completed'
    
    def generate_receipt(self):
        """Generate receipt for payment
        
            Returns:

                str: Formatted receipt string with ID, amount, and date."""
        return f"Receipt #{self.id} - ${self.amount} - {self.created_at}"
    
    def __repr__(self):
        """Returns a string representation of Payment."""
        return f"<Payment {self.id} - ${self.amount}>"