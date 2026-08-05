"""
Cart Routes

* **Date:** 8/4/26
* **Programmers: Mark and Chutiwat

Manages temporary seat locks, cart subtotals, and ticket staging prior to checkout.
"""
from flask import Blueprint, request, jsonify
from database.db import db
from models.cart import Cart
from models.ticket import Ticket
from models.seat import Seat
from models.showtime import Showtime
from models.customer import Customer
from datetime import datetime, timedelta

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/<int:customer_id>', methods=['GET'])
def get_cart(customer_id):
    """
    Retrieves the active cart for a specific customer.
    
    Args:
    
        customer_id(int): The ID of the customer extracted from the URL path.
        
    Returns:
        
        - 200 (OK): A JSON object containing cart details, subtotal and ticket information.
        - 404 (Not Found): A JSON error message if the cart is not found
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        cart = Cart.query.filter_by(customer_id=customer_id).first()
        
        if not cart:
            return jsonify({'error': 'Cart not found'}), 404
        
        tickets_list = [{
            'id': ticket.id,
            'showtime_id': ticket.showtime_id,
            'seat_id': ticket.seat_id,
            'seat_number': ticket.seat.seat_number,
            'ticket_type': ticket.ticket_type,
            'price': ticket.price
        } for ticket in cart.tickets]
        
        return jsonify({
            'id': cart.id,
            'customer_id': cart.customer_id,
            'subtotal': cart.subtotal,
            'tickets': tickets_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/<int:customer_id>/add-seat', methods=['POST'])
def add_seat_to_cart(customer_id):
    """
    Adds a selected seat to a customer's cart and applies a temporary lock.

    Args:

        customer_id (int): The ID of the customer gotten from the URL path.

    Expected JSON Payload:

        showtime_id (int): The ID of the movie showtime.
        seat_id (int): The ID of the physical seat.
        ticket_type (str): The type of ticket.

    Returns:

        - 201 (Created): A JSON object with the updated ticket and subtotal.
        - 400 (Bad Request): A JSON error if required fields are missing, or if the seat is already booked or locked by another user.
        - 404 (Not Found): A JSON error if the seat or showtime is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('showtime_id') or not data.get('seat_id') or not data.get('ticket_type'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get or create cart
        cart = Cart.query.filter_by(customer_id=customer_id).first()
        if not cart:
            cart = Cart(customer_id=customer_id)
            db.session.add(cart)
            db.session.commit()
        
        # Get seat
        seat = Seat.query.get(data['seat_id'])
        if not seat:
            return jsonify({'error': 'Seat not found'}), 404
        
        # Check if seat is already booked or locked
        if seat.is_booked:
            return jsonify({'error': 'Seat is already booked'}), 400
        
        if seat.is_locked and seat.lock_expires_at and datetime.now() < seat.lock_expires_at:
            return jsonify({'error': 'Seat is already locked by another user'}), 400
        
        # Lock the seat
        seat.lock_seat(customer_id, lock_duration_minutes=5)
        
        # Get showtime price
        showtime = Showtime.query.get(data['showtime_id'])
        if not showtime:
            return jsonify({'error': 'Showtime not found'}), 404
        
        # Create ticket
        ticket = Ticket(
            cart_id=cart.id,
            showtime_id=data['showtime_id'],
            seat_id=data['seat_id'],
            ticket_type=data['ticket_type'],
            price=showtime.price
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        # Update cart subtotal
        cart.calculate_subtotal()
        db.session.commit()
        
        return jsonify({
            'message': 'Seat added to cart',
            'ticket': {
                'id': ticket.id,
                'seat_number': seat.seat_number,
                'ticket_type': ticket.ticket_type,
                'price': ticket.price
            },
            'cart_subtotal': cart.subtotal
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/<int:customer_id>/remove-seat', methods=['DELETE'])
def remove_seat_from_cart(customer_id):
    """
    Removes a ticket from the cart and clears its temporary seat lock.
    
    Args:
        customer_id(int): The ID of the customer gotten from the URL path.
        
    Expected JSON Payload:
    
        ticket_id (int): The unique ID of the ticket to remove.
        
    Returns:
    
        - 200 (OK): A JSON object with the newly updated cart subtotal.
        - 400 (Bad Request): A JSON error if the ticket_id is missing.
        - 404 (Not Found): A JSON error if the ticket is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('ticket_id'):
            return jsonify({'error': 'Missing ticket_id'}), 400
        
        ticket = Ticket.query.get(data['ticket_id'])
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Unlock the seat
        seat = Seat.query.get(ticket.seat_id)
        seat.unlock_seat()
        
        # Remove ticket from cart
        db.session.delete(ticket)
        
        # Update cart subtotal
        cart = Cart.query.get(ticket.cart_id)
        cart.calculate_subtotal()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Seat removed from cart',
            'cart_subtotal': cart.subtotal
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/<int:customer_id>/calculate-total', methods=['GET'])
def calculate_total(customer_id):
    """
    Calculates the final checkout total including taxes and fees.
    
    Args:
        customer_id (int): The ID of the customer gotten from the URL path.
        
    Returns:
        
        - 200 (OK): A JSON object detailing the subtotal, calculated tax, convenience fees, and final total.
        - 404 (Not Found): A JSON error message if the cart is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        cart = Cart.query.filter_by(customer_id=customer_id).first()
        
        if not cart:
            return jsonify({'error': 'Cart not found'}), 404
        
        subtotal = cart.subtotal
        tax = subtotal * 0.10  # 10% tax
        fees = 2.50  # Fixed convenience fee
        total = subtotal + tax + fees
        
        return jsonify({
            'subtotal': subtotal,
            'tax': tax,
            'fees': fees,
            'total': total
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500