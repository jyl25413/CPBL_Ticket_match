import bcrypt
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash as werkzeug_check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(64), nullable=False, default='球迷')
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    social_link = db.Column(db.String(255), nullable=True)  # FB or IG link
    rating_avg = db.Column(db.Float, default=5.0)
    default_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    listings = db.relationship('Listing', backref='seller', lazy='dynamic', foreign_keys='Listing.seller_id')
    wants_to_buy = db.relationship('WantToBuy', backref='buyer', lazy='dynamic')
    applications = db.relationship('Application', backref='buyer', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception:
            return werkzeug_check_password_hash(self.password_hash, password)

    def recalculate_stats(self):
        ratings_received = Rating.query.filter_by(ratee_id=self.id).all()
        if ratings_received:
            total_score = sum(r.score for r in ratings_received)
            self.rating_avg = round(total_score / len(ratings_received), 1)
        else:
            self.rating_avg = 5.0
            
        defaults = Rating.query.filter_by(ratee_id=self.id, is_default=True).count()
        self.default_count = defaults

class Listing(db.Model):
    __tablename__ = 'listings'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(32), default='ticket')  # 'ticket', 'merch'
    team = db.Column(db.String(64), nullable=False)        
    stadium = db.Column(db.String(64), nullable=False)     
    zone = db.Column(db.String(64), nullable=False)        
    ticket_type = db.Column(db.String(32), default='全票')  
    delivery_method = db.Column(db.String(64), default='中職官方APP轉贈') 
    original_price = db.Column(db.Integer, nullable=False)  
    price = db.Column(db.Integer, nullable=False)           
    quantity = db.Column(db.Integer, default=1)
    ticket_image_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(32), default='active')     # active, pending, sold, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    applications = db.relationship('Application', backref='listing', cascade='all, delete-orphan', lazy='dynamic')
    orders = db.relationship('Order', backref='listing', lazy='dynamic')

class WantToBuy(db.Model):
    __tablename__ = 'wants_to_buy'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(32), default='ticket')
    team = db.Column(db.String(64), nullable=False)
    stadium = db.Column(db.String(64), nullable=False)
    zone = db.Column(db.String(64), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    max_price = db.Column(db.Integer, nullable=True)
    note = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), default='active')     # active, fulfilled, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(32), default='pending')    # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(32), default='awaiting_payment') 
    buyer_defaulted = db.Column(db.Boolean, default=False)
    seller_defaulted = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text, nullable=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_orders')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_orders')
    ratings = db.relationship('Rating', backref='order', lazy='dynamic')

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    rater_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ratee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # 1-5
    is_default = db.Column(db.Boolean, default=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
