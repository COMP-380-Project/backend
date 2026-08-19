"""
Customer Model
Date: 8/4/26
Programmers: Mark and Chutiwat

Represents a registered user within the system.
Handles customer registration, login, and account management.
"""
from database.db import db
from datetime import datetime

class Customer(db.Model):
    """ 
    Customer Model storing information for authentication and user management

    Attributes:

        id (int): The primary key for the customer.
        email (str): The unique email address used for contact and login.
        password (str): The stored password (should be hased in production) for account security.
        name (str): The full name of the customer.
        role (str): Access level, either 'customer' or 'manager'.
        created_at (datetime): The exact date and time the account was registered.
    """
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='customer', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        """Returns string representation of Customer."""
        return f"<Customer {self.email} ({self.role})>"