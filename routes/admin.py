"""
Admin/Manager Routes

* **Date:** 8/10/26
* **Programmer:** Mark Antonov

Manager-only endpoints for adding and managing movies, theatres,
auditoriums, and showtimes. All routes require a valid manager
customer_id, checked via require_manager().
"""
from flask import Blueprint, request, jsonify
from database.db import db
from models.movie import Movie
from models.all_movies import AllMovies
from routes.admin_utils import require_manager
from models.theatre import Theatre
from models.auditorium import Auditorium
from models.showtime import Showtime
from models.seat import Seat

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/movies', methods=['POST'])
def add_movie():
    """
    Add a new movie to the catalog and mark it as currently showing.

    Expected JSON Payload:
        customer_id (int): ID of the manager making the request
        title (str): Movie title
        genre (str): Movie genre
        duration (int): Duration in minutes
        description (str): Movie description
        rating (float, optional): Movie rating
        cast (str): Comma-separated cast list

    Returns:
        - 201 (Created): The new movie's details
        - 400 (Bad Request): Missing required fields
        - 403 (Forbidden): Requesting customer is not a manager
        - 404 (Not Found): customer_id does not exist
    """
    data = request.get_json()

    customer, error = require_manager(data.get('customer_id') if data else None)
    if error:
        return jsonify(error[0]), error[1]

    required_fields = ['title', 'genre', 'duration', 'description', 'cast']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'error': 'Missing required movie fields'}), 400

    movie = Movie(
        title=data['title'],
        genre=data['genre'],
        duration=data['duration'],
        description=data['description'],
        rating=data.get('rating', 0.0),
        cast=data['cast']
    )
    db.session.add(movie)
    db.session.flush()

    all_movies_entry = AllMovies(movie_id=movie.id, is_currently_showing=True)
    db.session.add(all_movies_entry)
    db.session.commit()

    return jsonify({
        'message': 'Movie added successfully',
        'movie': {
            'id': movie.id,
            'title': movie.title,
            'genre': movie.genre,
            'duration': movie.duration,
            'description': movie.description,
            'rating': movie.rating,
            'cast': movie.cast
        }
    }), 201


@admin_bp.route('/movies/<int:movie_id>/toggle-showing', methods=['PUT'])
def toggle_movie_showing(movie_id):
    """
    Toggle whether a movie is currently showing.

    Expected JSON Payload:
        customer_id (int): ID of the manager making the request
        is_currently_showing (bool): New showing status

    Returns:
        - 200 (OK): Updated status
        - 400 (Bad Request): Missing is_currently_showing field
        - 403 (Forbidden): Requesting customer is not a manager
        - 404 (Not Found): Movie or customer not found
    """
    data = request.get_json()

    customer, error = require_manager(data.get('customer_id') if data else None)
    if error:
        return jsonify(error[0]), error[1]

    if 'is_currently_showing' not in data:
        return jsonify({'error': 'Missing is_currently_showing field'}), 400

    all_movies_entry = AllMovies.query.filter_by(movie_id=movie_id).first()
    if not all_movies_entry:
        return jsonify({'error': 'Movie not found in catalog'}), 404

    all_movies_entry.is_currently_showing = data['is_currently_showing']
    db.session.commit()

    return jsonify({
        'message': 'Movie showing status updated',
        'movie_id': movie_id,
        'is_currently_showing': all_movies_entry.is_currently_showing
    }), 200

@admin_bp.route('/theatres', methods=['POST'])
def add_theatre():
    """
    Add a new theatre location.

    Expected JSON Payload:
        customer_id (int): ID of the manager making the request
        name (str): Theatre name
        address (str): Theatre address
        num_auditoriums (int): Number of auditoriums at this theatre

    Returns:
        - 201 (Created): The new theatre's details
        - 400 (Bad Request): Missing required fields
        - 403 (Forbidden): Requesting customer is not a manager
    """
    data = request.get_json()

    customer, error = require_manager(data.get('customer_id') if data else None)
    if error:
        return jsonify(error[0]), error[1]

    required_fields = ['name', 'address', 'num_auditoriums']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'error': 'Missing required theatre fields'}), 400

    theatre = Theatre(
        name=data['name'],
        address=data['address'],
        num_auditoriums=data['num_auditoriums']
    )
    db.session.add(theatre)
    db.session.commit()

    return jsonify({
        'message': 'Theatre added successfully',
        'theatre': {
            'id': theatre.id,
            'name': theatre.name,
            'address': theatre.address,
            'num_auditoriums': theatre.num_auditoriums
        }
    }), 201


@admin_bp.route('/auditoriums', methods=['POST'])
def add_auditorium():
    """
    Add a new auditorium to an existing theatre.

    Expected JSON Payload:
        customer_id (int): ID of the manager making the request
        theatre_id (int): ID of the theatre this auditorium belongs to
        auditorium_type (str): e.g. "Standard" or "IMAX"
        seat_capacity (int): Total seats in this auditorium

    Returns:
        - 201 (Created): The new auditorium's details
        - 400 (Bad Request): Missing required fields
        - 403 (Forbidden): Requesting customer is not a manager
        - 404 (Not Found): Theatre does not exist
    """
    data = request.get_json()

    customer, error = require_manager(data.get('customer_id') if data else None)
    if error:
        return jsonify(error[0]), error[1]

    required_fields = ['theatre_id', 'auditorium_type', 'seat_capacity']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'error': 'Missing required auditorium fields'}), 400

    theatre = Theatre.query.get(data['theatre_id'])
    if not theatre:
        return jsonify({'error': 'Theatre not found'}), 404

    auditorium = Auditorium(
        theatre_id=data['theatre_id'],
        auditorium_type=data['auditorium_type'],
        seat_capacity=data['seat_capacity']
    )
    db.session.add(auditorium)
    db.session.commit()

    return jsonify({
        'message': 'Auditorium added successfully',
        'auditorium': {
            'id': auditorium.id,
            'theatre_id': auditorium.theatre_id,
            'auditorium_type': auditorium.auditorium_type,
            'seat_capacity': auditorium.seat_capacity
        }
    }), 201


@admin_bp.route('/showtimes', methods=['POST'])
def add_showtime():
    """
    Add a new showtime for a movie in an auditorium, and automatically
    generate one Seat row per seat in that auditorium's capacity.

    Expected JSON Payload:
        customer_id (int): ID of the manager making the request
        movie_id (int): Movie being shown
        auditorium_id (int): Auditorium it's shown in
        showtime (str): ISO 8601 datetime string, e.g. "2026-08-15T19:30:00"
        price (float): Ticket price for this showing

    Returns:
        - 201 (Created): The new showtime's details, including seats created
        - 400 (Bad Request): Missing or invalid fields
        - 403 (Forbidden): Requesting customer is not a manager
        - 404 (Not Found): Movie or auditorium does not exist
    """
    from datetime import datetime

    data = request.get_json()

    customer, error = require_manager(data.get('customer_id') if data else None)
    if error:
        return jsonify(error[0]), error[1]

    required_fields = ['movie_id', 'auditorium_id', 'showtime', 'price']
    if not all(data.get(field) is not None for field in required_fields):
        return jsonify({'error': 'Missing required showtime fields'}), 400

    auditorium = Auditorium.query.get(data['auditorium_id'])
    if not auditorium:
        return jsonify({'error': 'Auditorium not found'}), 404

    try:
        showtime_dt = datetime.fromisoformat(data['showtime'])
    except ValueError:
        return jsonify({'error': 'showtime must be a valid ISO 8601 datetime string'}), 400

    showtime = Showtime(
        auditorium_id=data['auditorium_id'],
        movie_id=data['movie_id'],
        showtime=showtime_dt,
        price=data['price']
    )
    db.session.add(showtime)
    db.session.flush()  # get showtime.id before generating seats

    # Auto-generate seats based on auditorium capacity (rows A-Z, 10 seats per row)
    capacity = auditorium.seat_capacity
    rows = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    seat_count = 0

    for row in rows:
        for num in range(1, 11):
            if seat_count >= capacity:
                break
            seat = Seat(
                showtime_id=showtime.id,
                seat_number=f"{row}{num}",
                is_booked=False,
                is_locked=False
            )
            db.session.add(seat)
            seat_count += 1
        if seat_count >= capacity:
            break

    db.session.commit()

    return jsonify({
        'message': 'Showtime added successfully',
        'showtime': {
            'id': showtime.id,
            'movie_id': showtime.movie_id,
            'auditorium_id': showtime.auditorium_id,
            'showtime': showtime.showtime.isoformat(),
            'price': showtime.price
        },
        'seats_created': seat_count
    }), 201