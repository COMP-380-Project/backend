"""
Seat Routes

* Date: 8/4/26
* Programmers: Mark and Chutiwat

Monitors the availability, locking, and automatic expiration of individual seats.
"""
from flask import Blueprint, request, jsonify
from database.db import db
from models.seat import Seat
from models.showtime import Showtime
from datetime import datetime

seats_bp = Blueprint('seats', __name__)

@seats_bp.route('/showtime/<int:showtime_id>', methods=['GET'])
def get_showtime_seats(showtime_id):
    """
    Gets the layout and status of all seats for a showtime.

    Args:

        showtime_id (int): The ID of the showtime gotten from the URL path.

    Returns:

        - 200 (OK): A JSON object detailing the availability logic of each seat.
        - 404 (Not Found): A JSON error if the showtime is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        showtime = Showtime.query.get(showtime_id)
        
        if not showtime:
            return jsonify({'error': 'Showtime not found'}), 404
        
        seats = Seat.query.filter_by(showtime_id=showtime_id).all()
        
        seats_list = [{
            'id': seat.id,
            'seat_number': seat.seat_number,
            'is_booked': seat.is_booked,
            'is_locked': seat.is_locked,
            'lock_expires_at': seat.lock_expires_at.isoformat() if seat.lock_expires_at else None,
            'status': 'booked' if seat.is_booked else ('locked' if seat.is_locked and not seat.is_lock_expired() else 'available')
        } for seat in seats]
        
        return jsonify({
            'showtime_id': showtime_id,
            'total_seats': len(seats),
            'available_seats': len([s for s in seats if not s.is_booked and (not s.is_locked or s.is_lock_expired())]),
            'seats': seats_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@seats_bp.route('/<int:seat_id>/status', methods=['GET'])
def get_seat_status(seat_id):
    """
    Checks availability of a single specific seat.
    
    Args:
    
        seat_id (int): The ID of the seat gotten from the URL path.
        
    Returns:
    
        - 200 (OK): A JSON object detailing if the seat is booked, temporarily locked, or available.
        - 404 (Not Found): A JSON error if the seat is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        seat = Seat.query.get(seat_id)
        
        if not seat:
            return jsonify({'error': 'Seat not found'}), 404
        
        # Check if lock has expired
        is_expired = seat.is_lock_expired()
        
        if is_expired and seat.is_locked:
            seat.unlock_seat()
            db.session.commit()
        
        return jsonify({
            'id': seat.id,
            'seat_number': seat.seat_number,
            'is_booked': seat.is_booked,
            'is_locked': seat.is_locked and not is_expired,
            'lock_expires_at': seat.lock_expires_at.isoformat() if seat.lock_expires_at and not is_expired else None,
            'status': 'booked' if seat.is_booked else ('locked' if seat.is_locked and not is_expired else 'available')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@seats_bp.route('/release-expired', methods=['POST'])
def release_expired_locks():
    """
    Release of all seats with expired temporary locks.
    
    Returns:
    
        - 200 (OK): A JSON object confirming how many locks were successfully released.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        seats = Seat.query.filter_by(is_locked=True).all()
        
        released_count = 0
        for seat in seats:
            if seat.is_lock_expired():
                seat.unlock_seat()
                released_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'{released_count} expired locks released',
            'released_count': released_count
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500