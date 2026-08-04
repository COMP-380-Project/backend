from database.db import db

class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    cast = db.Column(db.String(500), nullable=False)  # comma-separated actors
    
    def __repr__(self):
        return f"<Movie {self.title}>"