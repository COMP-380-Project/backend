"""
Cart Routes

* **Date:** 8/4/26
* **Programmers: Mark and Chutiwat

Manages temporary seat locks, cart subtotals, and ticket staging prior to checkout.
Supports both logged-in customers (keyed by customer_id) and guests (keyed by
a cart_id returned from POST /guest, with no customer attached).
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


def _serialize_cart(cart):
    """
    Builds the JSON-ready representation of a cart and its tickets.

    Args:

        cart (Cart): The cart to serialize.

    Returns:

        dict: Cart id, customer_id, subtotal, and a list of ticket details.
    """
    tickets_list = [{
        'id': ticket.id,
        'showtime_id': ticket.showtime_id,
        'seat_id': ticket.seat_id,
        'seat_number': ticket.seat.seat_number,
        'ticket_type': ticket.ticket_type,
        'price': ticket.price,
        'movie_title': ticket.showtime.movie.title if ticket.showtime and ticket.showtime.movie else None,
        'showtime': ticket.showtime.showtime.isoformat() if ticket.showtime else None
    } for ticket in cart.tickets]

    return {
        'id': cart.id,
        'customer_id': cart.customer_id,
        'subtotal': cart.subtotal,
        'tickets': tickets_list
    }


def _add_seat_to_cart(cart, data):
    """
    Shared logic for locking a seat and adding it to a given cart, used by
    both the registered-customer and guest add-seat routes.

    Args:

        cart (Cart): The cart to add the ticket to.
        data (dict): Request JSON containing showtime_id, seat_id, ticket_type.

    Returns:

        tuple: (response_dict, status_code)
    """
    if not data or not data.get('showtime_id') or not data.get('seat_id') or not data.get('ticket_type'):
        return {'error': 'Missing required fields'}, 400

    seat = Seat.query.get(data['seat_id'])
    if not seat:
        return {'error': 'Seat not found'}, 404

    if seat.is_booked:
        return {'error': 'Seat is already booked'}, 400

    if seat.is_locked and seat.lock_expires_at and datetime.now() < seat.lock_expires_at:
        return {'error': 'Seat is already locked by another user'}, 400

    showtime = Showtime.query.get(data['showtime_id'])
    if not showtime:
        return {'error': 'Showtime not found'}, 404

    # Lock under the cart's customer if registered; guests lock with no owner id
    seat.lock_seat(cart.customer_id, lock_duration_minutes=5)

    ticket = Ticket(
        cart_id=cart.id,
        showtime_id=data['showtime_id'],
        seat_id=data['seat_id'],
        ticket_type=data['ticket_type'],
        price=showtime.price
    )
    db.session.add(ticket)
    db.session.commit()

    cart.calculate_subtotal()
    db.session.commit()

    return {
        'message': 'Seat added to cart',
        'ticket': {
            'id': ticket.id,
            'seat_number': seat.seat_number,
            'ticket_type': ticket.ticket_type,
            'price': ticket.price
        },
        'cart_subtotal': cart.subtotal
    }, 201


def _remove_seat_from_cart(data):
    """
    Shared logic for unlocking a seat and removing its ticket from a cart.

    Args:

        data (dict): Request JSON containing ticket_id.

    Returns:

        tuple: (response_dict, status_code)
    """
    if not data or not data.get('ticket_id'):
        return {'error': 'Missing ticket_id'}, 400

    ticket = Ticket.query.get(data['ticket_id'])
    if not ticket:
        return {'error': 'Ticket not found'}, 404

    seat = Seat.query.get(ticket.seat_id)
    seat.unlock_seat()

    db.session.delete(ticket)

    cart = Cart.query.get(ticket.cart_id)
    cart.calculate_subtotal()

    db.session.commit()

    return {
        'message': 'Seat removed from cart',
        'cart_subtotal': cart.subtotal
    }, 200


def _calculate_total(cart):
    """
    Shared logic for computing subtotal, tax, fees, and total for a cart.

    Args:

        cart (Cart): The cart to total.

    Returns:

        dict: subtotal, tax, fees, and total.
    """
    subtotal = cart.subtotal
    tax = subtotal * 0.10  # 10% tax
    fees = 2.50  # Fixed convenience fee
    total = subtotal + tax + fees

    return {
        'subtotal': subtotal,
        'tax': tax,
        'fees': fees,
        'total': total
    }


# ---- Registered customer routes (existing behavior, unchanged) ----

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

        return jsonify(_serialize_cart(cart)), 200
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

        cart = Cart.query.filter_by(customer_id=customer_id).first()
        if not cart:
            cart = Cart(customer_id=customer_id)
            db.session.add(cart)
            db.session.commit()

        response, status = _add_seat_to_cart(cart, data)
        return jsonify(response), status
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
        response, status = _remove_seat_from_cart(data)
        return jsonify(response), status
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

        return jsonify(_calculate_total(cart)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- Guest routes (new — keyed by cart_id instead of customer_id) ----

@cart_bp.route('/guest', methods=['POST'])
def create_guest_cart():
    """
    Creates a new, empty cart with no customer attached, for a guest checkout flow.

    Returns:

        - 201 (Created): A JSON object containing the new cart_id — store this
          client-side (e.g. localStorage) and reuse it on the /by-id routes below.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        cart = Cart(customer_id=None)
        db.session.add(cart)
        db.session.commit()

        return jsonify({
            'message': 'Guest cart created',
            'cart_id': cart.id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/by-id/<int:cart_id>', methods=['GET'])
def get_cart_by_id(cart_id):
    """
    Retrieves a cart directly by its own id (guest flow).

    Args:

        cart_id (int): The ID of the cart gotten from the URL path.

    Returns:

        - 200 (OK): A JSON object containing cart details, subtotal and ticket information.
        - 404 (Not Found): A JSON error message if the cart is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        cart = Cart.query.get(cart_id)

        if not cart:
            return jsonify({'error': 'Cart not found'}), 404

        return jsonify(_serialize_cart(cart)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/by-id/<int:cart_id>/add-seat', methods=['POST'])
def add_seat_to_cart_by_id(cart_id):
    """
    Adds a selected seat to a guest cart (keyed by cart_id) and applies a temporary lock.

    Args:

        cart_id (int): The ID of the cart gotten from the URL path.

    Expected JSON Payload:

        showtime_id (int): The ID of the movie showtime.
        seat_id (int): The ID of the physical seat.
        ticket_type (str): The type of ticket.

    Returns:

        - 201 (Created): A JSON object with the updated ticket and subtotal.
        - 400 (Bad Request): A JSON error if required fields are missing, or if the seat is already booked or locked by another user.
        - 404 (Not Found): A JSON error if the cart, seat, or showtime is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        cart = Cart.query.get(cart_id)
        if not cart:
            return jsonify({'error': 'Cart not found'}), 404

        data = request.get_json()
        response, status = _add_seat_to_cart(cart, data)
        return jsonify(response), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/by-id/<int:cart_id>/remove-seat', methods=['DELETE'])
def remove_seat_from_cart_by_id(cart_id):
    """
    Removes a ticket from a guest cart and clears its temporary seat lock.

    Args:

        cart_id (int): The ID of the cart gotten from the URL path.

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
        response, status = _remove_seat_from_cart(data)
        return jsonify(response), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/by-id/<int:cart_id>/calculate-total', methods=['GET'])
def calculate_total_by_id(cart_id):
    """
    Calculates the final checkout total including taxes and fees for a guest cart.

    Args:

        cart_id (int): The ID of the cart gotten from the URL path.

    Returns:

        - 200 (OK): A JSON object detailing the subtotal, calculated tax, convenience fees, and final total.
        - 404 (Not Found): A JSON error message if the cart is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        cart = Cart.query.get(cart_id)

        if not cart:
            return jsonify({'error': 'Cart not found'}), 404

        return jsonify(_calculate_total(cart)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500