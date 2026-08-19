"""
Theatre Routes

Date: 8/4/26
Programmers: Mark and Chutiwat

Provides data on physical theatre locations, auditoriums, and scheduled showtimes.
"""
from flask import Blueprint, request, jsonify
from database.db import db
from models.theatre import Theatre
from models.auditorium import Auditorium
from models.showtime import Showtime
from models.movie import Movie

theatres_bp = Blueprint('theatres', __name__)

@theatres_bp.route('', methods=['GET'])
def get_all_theatres():
    """
    Gets a list of all physical theatre locations in system.
    
    Returns:
    
        - 200 (OK): A JSON list of theatre details.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        theatres = Theatre.query.all()
        
        theatres_list = [{
            'id': theatre.id,
            'name': theatre.name,
            'address': theatre.address,
            'num_auditoriums': theatre.num_auditoriums
        } for theatre in theatres]
        
        return jsonify(theatres_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@theatres_bp.route('/<int:theatre_id>', methods=['GET'])
def get_theatre_details(theatre_id):
    """
    Get specific theatre information and all its associated auditoriums.
    
    Args:
    
        theatre_id (int): The ID of the theatre gotten from the URL path.
        
    Returns:
    
        - 200 (OK): A JSON object outliing the theatre and a nested list of auditoriums.
        - 404 (Not Found): A JSON error if the theatre is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        theatre = Theatre.query.get(theatre_id)
        
        if not theatre:
            return jsonify({'error': 'Theatre not found'}), 404
        
        auditoriums = Auditorium.query.filter_by(theatre_id=theatre_id).all()
        
        auditoriums_list = [{
            'id': auditorium.id,
            'auditorium_type': auditorium.auditorium_type,
            'seat_capacity': auditorium.seat_capacity
        } for auditorium in auditoriums]
        
        return jsonify({
            'id': theatre.id,
            'name': theatre.name,
            'address': theatre.address,
            'num_auditoriums': theatre.num_auditoriums,
            'auditoriums': auditoriums_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@theatres_bp.route('/auditorium/<int:auditorium_id>', methods=['GET'])
def get_auditorium_details(auditorium_id):
    """
    Gets all details and scheduled showtimes for a specific auditorium.
    
    Args:
        
        auditorium_id (int): The ID of the auditorium gotten from the URL path.
        
    Returns:
    
        - 200 (OK): A JSON object with auditorium characteristics and a nested showtime list.
        - 404 (Not Found): A JSON error if the auditorium is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        auditorium = Auditorium.query.get(auditorium_id)
        
        if not auditorium:
            return jsonify({'error': 'Auditorium not found'}), 404
        
        showtimes = Showtime.query.filter_by(auditorium_id=auditorium_id).all()
        
        showtimes_list = [{
            'id': showtime.id,
            'movie_id': showtime.movie_id,
            'movie_title': showtime.movie.title if showtime.movie else None,
            'showtime': showtime.showtime.isoformat(),
            'price': showtime.price
        } for showtime in showtimes]
        
        return jsonify({
            'id': auditorium.id,
            'theatre_id': auditorium.theatre_id,
            'auditorium_type': auditorium.auditorium_type,
            'seat_capacity': auditorium.seat_capacity,
            'showtimes': showtimes_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500