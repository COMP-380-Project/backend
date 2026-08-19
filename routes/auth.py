"""
Authentication Routes

Date: 8/4/26
Programmers: Mark and Chutiwat

Handles all endpoints related to customer registration, login, and session management.
"""
from flask import Blueprint, request, jsonify
from database.db import db
from models.customer import Customer
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new customer.
    
    Expected JSON Payload:

        email(str): The customer's email address.
        password (str): The chosen password.
        name (str): The customer's full name.

    Returns:
        
        - 201 (Created): A JSON object containing the new customer's details on success.
        - 400 (Bad Request): A JSON error message if required fields are missing.
        - 400 (Bad Request): A JSON error message if the email is already registered.
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if customer already exists
    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new customer
    new_customer = Customer(
        email=data['email'],
        password=generate_password_hash(data['password']),
        name=data['name'],
        role='customer'
    )
    
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({
        'message': 'Registration successful',
        'customer': {
            'id': new_customer.id,
            'email': new_customer.email,
            'name': new_customer.name,
            'role': new_customer.role
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticates a customer and returns an access token.
        
        Expected JSON Payload:
            
            email (str): The registered email address.
            password (str): The account password.
            
        Returns:
        
            - 200 (OK): A JSON object with authentication data on success.
            - 400 (Bad Request): A JSON error message if email or password fields are missing.
            - 401 (Unauthorized): A JSON error message if the email or password is invalid.
            """
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    # Find customer by email
    customer = Customer.query.filter_by(email=data['email']).first()
    
    if not customer or not check_password_hash(customer.password, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # TODO: Generate JWT token in production
    # For now, we'll use a simple auth object matching frontend's AuthUser shape
    auth_data = {
        'userId': customer.id,
        'name': customer.name,
        'role': customer.role
    }
    
    return jsonify({
        'message': 'Login successful',
        'auth': auth_data,
        'token': f'token_{customer.id}'  # Placeholder token
    }), 200