from flask import Blueprint, request, jsonify
from database.db import db
from models.movie import Movie
from models.all_movies import AllMovies
from models.showtime import Showtime

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('', methods=['GET'])
def get_all_movies():
    """Get all currently showing movies (events)"""
    try:
        # Get all movies that are currently showing
        all_movies = AllMovies.query.filter_by(is_currently_showing=True).all()
        
        movies_list = []
        for movie_showing in all_movies:
            movie = movie_showing.movie
            movies_list.append({
                'id': movie.id,
                'title': movie.title,
                'genre': movie.genre,
                'duration': movie.duration,
                'description': movie.description,
                'rating': movie.rating,
                'cast': movie.cast
            })
        
        return jsonify(movies_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """Get details of a specific movie (event)"""
    try:
        movie = Movie.query.get(movie_id)
        
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404
        
        # Get showtimes for this movie
        showtimes = Showtime.query.filter_by(movie_id=movie_id).all()
        
        showtimes_list = [{
            'id': showtime.id,
            'auditorium_id': showtime.auditorium_id,
            'showtime': showtime.showtime.isoformat(),
            'price': showtime.price
        } for showtime in showtimes]
        
        return jsonify({
            'id': movie.id,
            'title': movie.title,
            'genre': movie.genre,
            'duration': movie.duration,
            'description': movie.description,
            'rating': movie.rating,
            'cast': movie.cast,
            'showtimes': showtimes_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/search', methods=['GET'])
def search_movies():
    """Search for movies by title"""
    try:
        title = request.args.get('title', '')
        
        if not title:
            return jsonify({'error': 'Title parameter required'}), 400
        
        all_movies = AllMovies.query.join(Movie).filter(
            Movie.title.contains(title),
            AllMovies.is_currently_showing == True
        ).all()
        
        movies_list = [{
            'id': movie_showing.movie.id,
            'title': movie_showing.movie.title,
            'genre': movie_showing.movie.genre,
            'duration': movie_showing.movie.duration,
            'description': movie_showing.movie.description,
            'rating': movie_showing.movie.rating,
            'cast': movie_showing.movie.cast
        } for movie_showing in all_movies]
        
        return jsonify(movies_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500