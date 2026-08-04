from flask import Blueprint, request, jsonify
from database.db import db
from models.order import Order
from models.ticket import Ticket
from models.seat import Seat
from models.customer import Customer

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer_orders(customer_id):
    """Get all orders for a customer"""
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
    """Get details of a specific order"""
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Get all tickets associated with this order through cart
        # (Tickets are in cart, and cart is linked to payment/order)
        tickets = Ticket.query.filter_by(cart_id=order.payment.order[0].id if order.payment else None).all()
        
        # Simpler approach: get from payment and work backwards
        # For now, return order info
        return jsonify({
            'id': order.id,
            'customer_id': order.customer_id,
            'payment_id': order.payment_id,
            'total_amount': order.total_amount,
            'order_status': order.order_status,
            'created_at': order.created_at.isoformat(),
            'payment_status': order.payment.payment_status if order.payment else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<int:order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    """Cancel an order and unlock seats"""
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.order_status == 'cancelled':
            return jsonify({'error': 'Order is already cancelled'}), 400
        
        # Find all tickets for this order and unlock seats
        # Get cart from payment
        from models.cart import Cart
        cart = Cart.query.filter_by(customer_id=order.customer_id).first()
        
        if cart:
            for ticket in cart.tickets:
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