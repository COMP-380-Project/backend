"""
Database Seed Script
Date: August 2026
Programmer: Mark Antonov
Description: Populates the database with sample data for testing purposes.
    Creates sample movies, theatres, auditoriums, showtimes, and seats
    so the full booking flow can be tested end-to-end.

Usage: Run with `python seed.py` while virtual environment is active.
    WARNING: This will add duplicate data if run multiple times unless
    the database is cleared first.
"""

from datetime import datetime, timedelta
from app import create_app
from database.db import db
from models.movie import Movie
from models.all_movies import AllMovies
from models.theatre import Theatre
from models.auditorium import Auditorium
from models.showtime import Showtime
from models.seat import Seat


def seed_movies():
    """Create sample movies and mark them as currently showing"""
    movies_data = [
        {
            "title": "Spider-Man",
            "genre": "Action/Sci-Fi",
            "duration": 130,
            "description": "A young hero balances everyday life with the responsibility of protecting the city using his extraordinary abilities.",
            "rating": 8.2,
            "cast": "Tom Holland, Zendaya, Jacob Batalon"
        },
        {
            "title": "The Odyssey",
            "genre": "Adventure/Epic",
            "duration": 150,
            "description": "A legendary warrior faces trials across land and sea on a perilous journey home after a decade-long war.",
            "rating": 8.0,
            "cast": "Matt Damon, Tom Holland, Anne Hathaway"
        },
        {
            "title": "Minions",
            "genre": "Animation/Comedy",
            "duration": 91,
            "description": "A mischievous group of yellow henchmen search for a new villain to serve, leading to chaotic misadventures.",
            "rating": 7.0,
            "cast": "Steve Carell, Pierre Coffin, Alan Arkin"
        },
        {
            "title": "Toy Story 5",
            "genre": "Animation/Family",
            "duration": 105,
            "description": "Woody, Buzz, and the gang face a new challenge as their kid grows up and technology reshapes the world of toys.",
            "rating": 7.9,
            "cast": "Tom Hanks, Tim Allen, Annie Potts"
        }
    ]

    created_movies = []
    for data in movies_data:
        movie = Movie(**data)
        db.session.add(movie)
        db.session.flush()  # Get movie.id before commit

        # Mark it as currently showing
        all_movies_entry = AllMovies(movie_id=movie.id, is_currently_showing=True)
        db.session.add(all_movies_entry)

        created_movies.append(movie)

    db.session.commit()
    print(f"Created {len(created_movies)} movies")
    return created_movies


def seed_theatres():
    """Create sample theatres with auditoriums"""
    theatre = Theatre(
        name="CSUN Metro Cinemas",
        address="18111 Nordhoff St, Northridge, CA 91330",
        num_auditoriums=2
    )
    db.session.add(theatre)
    db.session.flush()  # Get theatre.id before commit

    auditoriums_data = [
        {"auditorium_type": "Standard", "seat_capacity": 50},
        {"auditorium_type": "IMAX", "seat_capacity": 35}
    ]

    created_auditoriums = []
    for data in auditoriums_data:
        auditorium = Auditorium(theatre_id=theatre.id, **data)
        db.session.add(auditorium)
        created_auditoriums.append(auditorium)

    db.session.commit()
    print(f"Created 1 theatre with {len(created_auditoriums)} auditoriums")
    return theatre, created_auditoriums

def seed_showtimes(movies, auditoriums):
    """Create showtimes linking movies to auditoriums"""
    base_time = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)

    showtime_slots = [
        base_time,
        base_time + timedelta(hours=3),
        base_time + timedelta(days=1),
    ]

    prices = {"Standard": 12.50, "IMAX": 18.00}

    created_showtimes = []
    for i, movie in enumerate(movies):
        auditorium = auditoriums[i % len(auditoriums)]
        for slot in showtime_slots:
            showtime = Showtime(
                auditorium_id=auditorium.id,
                movie_id=movie.id,
                showtime=slot,
                price=prices.get(auditorium.auditorium_type, 12.50)
            )
            db.session.add(showtime)
            db.session.flush()
            created_showtimes.append((showtime, auditorium))

    db.session.commit()
    print(f"Created {len(created_showtimes)} showtimes")
    return created_showtimes


def seed_seats(showtimes_with_auditorium):
    """Generate seats for each showtime based on auditorium capacity"""
    total_seats_created = 0

    for showtime, auditorium in showtimes_with_auditorium:
        capacity = auditorium.seat_capacity
        seats_per_row = 10
        rows = "ABCDEFGH"

        seat_count = 0
        for row in rows:
            for num in range(1, seats_per_row + 1):
                if seat_count >= capacity:
                    break
                seat = Seat(
                    showtime_id=showtime.id,
                    seat_number=f"{row}{num}",
                    is_booked=False,
                    is_locked=False
                )
                db.session.add(seat)
                seat_count += 1
                total_seats_created += 1
            if seat_count >= capacity:
                break

    db.session.commit()
    print(f"Created {total_seats_created} seats across all showtimes")


def seed_manager():
    """Create one manager account for testing admin functionality"""
    from werkzeug.security import generate_password_hash
    from models.customer import Customer

    manager = Customer(
        email="manager@cinema.com",
        password=generate_password_hash("manager123"),
        name="Theatre Manager",
        role="manager"
    )
    db.session.add(manager)
    db.session.commit()
    print(f"Created manager account (email: manager@cinema.com, password: manager123)")
    return manager


def run_seed():
    """Main entry point to seed the database"""
    app = create_app()

    with app.app_context():
        print("Starting database seed...")

        movies = seed_movies()
        theatre, auditoriums = seed_theatres()
        showtimes_with_auditorium = seed_showtimes(movies, auditoriums)
        seed_seats(showtimes_with_auditorium)
        seed_manager()

        print("Database seed complete!")




if __name__ == "__main__":
    run_seed()