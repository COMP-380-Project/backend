from flask import Blueprint, request, jsonify
from database.db import db
from models.seat import Seat
from models.showtime import Showtime
from datetime import datetime

seats_bp = Blueprint('seats', __name__)

@seats_bp.route('/showtime/<int:showtime_id>', methods=['GET'])
def get_showtime_seats(showtime_id):
    """Get all seats for a specific showtime"""
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
    """Get status of a specific seat"""
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
    """Release all expired seat locks"""
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