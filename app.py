from flask import Flask
from flask_cors import CORS
from config import Config
from database.db import db, init_db
from models.user import User
from models.movie import Movie
from models.theatre import Theatre
from models.auditorium import Auditorium
from models.showtime import Showtime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app)
    init_db(app)
    
    @app.route('/api/test', methods=['GET'])
    def test():
        return {'message': 'Backend is running!'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)