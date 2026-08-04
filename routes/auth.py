from flask import Blueprint, request, jsonify
from database.db import db
from models.customer import Customer

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new customer"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password') or not data.get('name') or not data.get('username'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if customer already exists
    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if Customer.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    # Create new customer
    new_customer = Customer(
        email=data['email'],
        password=data['password'],  # TODO: Hash password in production!
        name=data['name'],
        username=data['username']
    )
    
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({
        'message': 'Registration successful',
        'customer': {
            'id': new_customer.id,
            'email': new_customer.email,
            'name': new_customer.name,
            'username': new_customer.username
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a customer and return a token"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    # Find customer by email
    customer = Customer.query.filter_by(email=data['email']).first()
    
    if not customer or customer.password != data['password']:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # TODO: Generate JWT token in production
    # For now, we'll use a simple auth object
    auth_data = {
        'id': customer.id,
        'email': customer.email,
        'name': customer.name,
        'username': customer.username
    }
    
    return jsonify({
        'message': 'Login successful',
        'auth': auth_data,
        'token': f'token_{customer.id}'  # Placeholder token
    }), 200