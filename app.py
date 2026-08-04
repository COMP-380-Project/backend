from flask import Flask
from flask_cors import CORS
from config import Config
from database.db import db, init_db
from models.customer import Customer
from models.movie import Movie
from models.theatre import Theatre
from models.auditorium import Auditorium
from models.showtime import Showtime
from models.seat import Seat
from models.cart import Cart
from models.ticket import Ticket
from models.payment import Payment
from models.all_movies import AllMovies
from models.order import Order

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app)
    init_db(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    @app.route('/api/test', methods=['GET'])
    def test():
        return {'message': 'Backend is running!'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8080)