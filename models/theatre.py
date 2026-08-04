from database.db import db

class Theatre(db.Model):
    __tablename__ = 'theatres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    num_auditoriums = db.Column(db.Integer, nullable=False)
    
    # Relationship to Auditoriums
    auditoriums = db.relationship('Auditorium', backref='theatre', lazy=True)
    
    def __repr__(self):
        return f"<Theatre {self.name}>"