from database.db import db

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    showtime_id = db.Column(db.Integer, db.ForeignKey('showtimes.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)
    ticket_type = db.Column(db.String(20), nullable=False)  # Adult, Kid, Senior
    price = db.Column(db.Float, nullable=False)
    
    # Relationships
    showtime = db.relationship('Showtime', backref='tickets')
    seat = db.relationship('Seat', backref='tickets')
    
    def __repr__(self):
        return f"<Ticket {self.id} - {self.ticket_type}>"