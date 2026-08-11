"""
Order Routes

* **Date:** 8/4/26
* **Programmers:** Mark and Chutiwat

Handles fetching customer order histories and cancelling existing ticket orders.
"""
from flask import Blueprint, request, jsonify
from database.db import db
from models.order import Order
from models.ticket import Ticket
from models.seat import Seat
from models.customer import Customer

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer_orders(customer_id):
    """
    Gets the complete order history for a specific customer.
    
    Args:
    
        customer_id (int): The ID of the customer gotten from the URL path.
        
    Returns:
    
        - 200 (OK): A JSON list containing summarized order records.
        - 404 (Not Found): A JSON error message if the customer is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        orders = Order.query.filter_by(customer_id=customer_id).all()
        
        orders_list = [{
            'id': order.id,
            'customer_id': order.customer_id,
            'total_amount': order.total_amount,
            'order_status': order.order_status,
            'created_at': order.created_at.isoformat()
        } for order in orders]
        
        return jsonify(orders_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    """
    Gets detailed information regarding a specific order and its payment status.

    Args:

        order_id (int): The ID of the order gotten from the URL path.

    Returns:

        - 200 (OK): A JSON object containing the order summary and linked payment status.
        - 404 (Not Found): A JSON error message if the order is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
    """
    try:
        order = Order.query.get(order_id)

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        showtime = order.get_showtime()
        auditorium = order.get_auditorium()

        return jsonify({
            'id': order.id,
            'customer_id': order.customer_id,
            'payment_id': order.payment_id,
            'total_amount': order.total_amount,
            'order_status': order.order_status,
            'created_at': order.created_at.isoformat(),
            'payment_status': order.payment.payment_status if order.payment else None,
            'seat_numbers': order.get_seat_number(),
            'auditorium_type': auditorium.auditorium_type if auditorium else None,
            'movie_title': showtime.movie.title if showtime and showtime.movie else None,
            'showtime': showtime.showtime.isoformat() if showtime else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<int:order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    """
    Cancel an active order and releases its associated booked seats.
    
    Args:
    
        order_id (int): The ID of the order gotten from the URL path.
        
    Returns:
        
        - 200 (OK): A JSON object with a confirmation message on success.
        - 400 (Bad Request): A JSON error if the order is already cancelled.
        - 404 (Not Found): A JSON error if the order is not found.
        - 500 (Internal Server Error): A JSON error message if a server exception occurs.
        """
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.order_status == 'cancelled':
            return jsonify({'error': 'Order is already cancelled'}), 400
        
        # Unlock/unbook all seats tied to this order's cart
        if order.cart:
            for ticket in order.cart.tickets:
                seat = Seat.query.get(ticket.seat_id)
                if seat:
                    seat.is_booked = False
                    seat.is_locked = False
                    seat.locked_by_user = None
                    seat.lock_expires_at = None
        
        # Update order status
        order.order_status = 'cancelled'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order cancelled successfully',
            'order': {
                'id': order.id,
                'order_status': order.order_status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500