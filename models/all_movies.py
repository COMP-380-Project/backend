"""
AllMovies Model
* **Date:** 8/4/26
* **Programmers:** Mark and Chutiwat

Represents currently showing movies.
"""
from database.db import db
from models.movie import Movie

class AllMovies(db.Model):
    """
    AllMovies Model tracking the active showing status of movies in the system for movie catalog management.

    Attributes:

        id (int): The primary key for the record.
        movie_id (int): The foreign key linking to Movie.
        is_currently_showing (bool): Whether the movie is currently available for booking.
    """
    __tablename__ = 'all_movies'
    
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    is_currently_showing = db.Column(db.Boolean, default=True)
    
    # Relationship
    movie = db.relationship('Movie', backref='all_movies')
    
    def display_movies(self):
        """Display all currently showing movies.
        
            Returns:

                list: List of AllMovies objects where is_currently_showing is True."""
        return AllMovies.query.filter_by(is_currently_showing=True).all()
    
    def search_movies(self, title):
        """Searches for active movies by a specific title.
        
            Args:

                title (str): The search string for the movie title.
                
            Returns:

                list: List of matching movies that are currently showing."""
        return AllMovies.query.join(Movie).filter(
            Movie.title.contains(title),
            AllMovies.is_currently_showing == True
        ).all()
    
    def get_movie_details(self, movie_id):
        """Get details of a specific movie.
        
            Args:

                movie_id (int): ID of movie to retrieve.
            
            Returns:

                AllMovies: Movie object if found, none otherwise."""
        return AllMovies.query.filter_by(movie_id=movie_id).first()
    
    def __repr__(self):
        """Returns a string representation of ALLMovies."""
        return f"<AllMovies {self.movie_id}>"