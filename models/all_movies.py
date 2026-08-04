from database.db import db
from models.movie import Movie

class AllMovies(db.Model):
    __tablename__ = 'all_movies'
    
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    is_currently_showing = db.Column(db.Boolean, default=True)
    
    # Relationship
    movie = db.relationship('Movie', backref='all_movies')
    
    def display_movies(self):
        """Display all currently showing movies"""
        return AllMovies.query.filter_by(is_currently_showing=True).all()
    
    def search_movies(self, title):
        """Search movies by title"""
        return AllMovies.query.join(Movie).filter(
            Movie.title.contains(title),
            AllMovies.is_currently_showing == True
        ).all()
    
    def get_movie_details(self, movie_id):
        """Get details of a specific movie"""
        return AllMovies.query.filter_by(movie_id=movie_id).first()
    
    def __repr__(self):
        return f"<AllMovies {self.movie_id}>"