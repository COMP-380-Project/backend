import pytest
from datetime import datetime, timedelta, timezone
from app import create_app
from database.db import db
from models.customer import Customer
from models.seat import Seat

@pytest.fixture
def test_client():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_lock_seat(test_client):
    customer = Customer(email = "customer@gmail.com", password = "hash", name = "Customer", role = "customer")

    seat = Seat(showtime_id = 1, seat_number = "A1", is_locked = False)

    db.session.add(customer)
    db.session.add(seat)
    db.session.commit()

    seat.lock_seat(customer.id)
    db.session.commit()

    print("\n")
    print("a) Test case: Verify lock_seat method updates lock status.")
    print("b) Expected Value: True")
    print(f"c) Test Result: {seat.is_locked}")

    assert seat.is_locked is True
    assert seat.locked_by_user == customer.id
    assert seat.lock_expires_at is not None

def test_unlock_seat(test_client):
    customer = Customer(email = "customer@gmail.com", password = "hash", name = "Customer", role = "customer")

    seat = Seat(showtime_id = 1, seat_number = "A1", is_locked = True)

    db.session.add(customer)
    db.session.add(seat)
    db.session.commit()

    seat.lock_seat(customer.id)
    db.session.commit()

    seat.unlock_seat()
    db.session.commit()

    print("\n")
    print("a) Test case: Verify unlock_seat method updates lock status.")
    print("b) Expected Value: False")
    print(f"c) Test Result: {seat.is_locked}")

    assert seat.is_locked is False
    assert seat.locked_by_user is None
    assert seat.lock_expires_at is None

def test_is_lock_expired(test_client):
    customer = Customer(email = "customer@gmail.com", password = "hash", name = "Customer", role = "customer")

    seat = Seat(showtime_id = 1, seat_number = "A1", is_locked = True)

    db.session.add(customer)
    db.session.add(seat)
    db.session.commit()

    # Path 1: Ensure missing expiration timestamps safely defaults to False

    print("\n")
    print("a) Verify null expiration returns False")
    print("b) Expected Value: False")
    print(f"c) Test Result: {seat.is_lock_expired()}")

    assert seat.is_lock_expired() is False

    # Path 2: Ensure unexpired future locks evaluate as still active (False)

    seat.lock_expires_at = datetime.now() + timedelta(minutes = 5)

    print("\n")
    print("a) Verify active lock returns False")
    print("b) Expected Value: False")
    print(f"c) Test Result: {seat.is_lock_expired()}")

    assert seat.is_lock_expired() is False

    # Path 3: Ensure past locks correctly trigger the expiration state (True)

    seat.lock_expires_at = datetime.now() - timedelta(minutes = 5)

    print("\n")
    print("a) Verify expired lock returns True")
    print("b) Expected Value: True")
    print(f"c) Test Result: {seat.is_lock_expired()}")

    assert seat.is_lock_expired() is True