from database.db import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # Credit Card, Debit Card, PayPal
    payment_status = db.Column(db.String(50), default='pending')  # pending, completed, failed, refunded
    payment_type = db.Column(db.String(50), nullable=False)  # Guest, Registered Member
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def process_payment(self):
        """Process the payment"""
        self.payment_status = 'completed'
    
    def verify_payment(self):
        """Verify if payment was successful"""
        return self.payment_status == 'completed'
    
    def generate_receipt(self):
        """Generate receipt for payment"""
        return f"Receipt #{self.id} - ${self.amount} - {self.created_at}"
    
    def __repr__(self):
        return f"<Payment {self.id} - ${self.amount}>"