"""
User Model

* **Date:** 8/5/26
* **Programmers:** Mark and Chutiwat

Represents a system user
"""

from database.db import db
from datetime import datetime

class User(db.Model):
    """
    User Model storing information about the user, including the classification of the user.

    Attributes:

        id (int): The primary key for the user.
        email (str): The unique email address used for login and contact.
        password (str): The stored password for the account.
        name (str): The user's full name.
        role (str): The classification of the role of user, defaults to 'customer'.
        created_at (datetime): The timestamp of when the user account was created.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='customer')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<User {self.email}>"