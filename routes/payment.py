from flask import Blueprint, request, jsonify
from database.db import db
from models.payment import Payment
from models.order import Order
from models.cart import Cart
from models.ticket import Ticket
from models.seat import Seat
from models.customer import Customer
from datetime import datetime

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/checkout', methods=['POST'])
def checkout():
    """Process payment and create order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('amount') or not data.get('payment_method'):
            return jsonify({'error': 'Missing amount or payment_method'}), 400
        
        # Check if registered customer or guest
        customer_id = data.get('customer_id')
        payment_type = 'Registered Member' if customer_id else 'Guest'
        
        if customer_id:
            customer = Customer.query.get(customer_id)
            if not customer:
                return jsonify({'error': 'Customer not found'}), 404
            
            cart = Cart.query.filter_by(customer_id=customer_id).first()
            if not cart:
                return jsonify({'error': 'Cart not found'}), 404
        else:
            # Guest checkout
            cart_id = data.get('cart_id')
            if not cart_id:
                return jsonify({'error': 'Missing cart_id for guest checkout'}), 400
            
            cart = Cart.query.get(cart_id)
            if not cart:
                return jsonify({'error': 'Cart not found'}), 404
        
        # Check if cart has tickets
        if not cart.tickets:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Create payment record
        payment = Payment(
            customer_id=customer_id,
            amount=data['amount'],
            payment_method=data['payment_method'],
            payment_type=payment_type,
            payment_status='pending'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Process payment (mock - in production, connect to payment gateway)
        payment.process_payment()
        
        # Verify payment was successful
        if not payment.verify_payment():
            return jsonify({'error': 'Payment failed'}), 400
        
        # Create order
        order = Order(
            customer_id=customer_id,
            payment_id=payment.id,
            total_amount=data['amount'],
            order_status='confirmed'
        )
        
        db.session.add(order)
        db.session.commit()
        
        # Permanently book all seats in cart
        for ticket in cart.tickets:
            seat = Seat.query.get(ticket.seat_id)
            seat.is_booked = True
            seat.is_locked = False
            seat.locked_by_user = None
            seat.lock_expires_at = None
        
        # Clear cart (optional - keep for records or delete)
        # db.session.delete(cart)
        
        db.session.commit()
        
        # Generate receipt
        receipt = payment.generate_receipt()
        
        return jsonify({
            'message': 'Payment successful',
            'order': {
                'id': order.id,
                'customer_id': order.customer_id,
                'total_amount': order.total_amount,
                'order_status': order.order_status,
                'created_at': order.created_at.isoformat()
            },
            'payment': {
                'id': payment.id,
                'amount': payment.amount,
                'payment_status': payment.payment_status,
                'receipt': receipt
            },
            'tickets': [{
                'id': ticket.id,
                'seat_number': ticket.seat.seat_number,
                'ticket_type': ticket.ticket_type,
                'price': ticket.price
            } for ticket in cart.tickets]
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/verify-payment/<int:payment_id>', methods=['GET'])
def verify_payment(payment_id):
    """Verify if a payment was successful"""
    try:
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify({
            'payment_id': payment.id,
            'amount': payment.amount,
            'payment_status': payment.payment_status,
            'payment_method': payment.payment_method,
            'payment_type': payment.payment_type,
            'is_verified': payment.verify_payment()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500