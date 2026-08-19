"""
Theatre model
 Date: 8/4/26
 Programmers: Mark and Chutiwat

Represents a physical theatre location containing multiple auditoriums.
"""
from database.db import db

class Theatre(db.Model):
    """
    Theatre Model storing information for theatre locations

    Attributes:

        id (int): The primary key for the theatre location.
        name (str): The designated name of the theatre.
        address (str): The physical street address of the theatre.
        num_auditoriums (int): The total count of auditoriums within the theatre.
    """    
    __tablename__ = 'theatres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    num_auditoriums = db.Column(db.Integer, nullable=False)
    
    # Relationship to Auditoriums
    auditoriums = db.relationship('Auditorium', backref='theatre', lazy=True)
    
    def __repr__(self):
        """Returns string representation of Theatre."""
        return f"<Theatre {self.name}>"