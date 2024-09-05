from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String(50), unique=True)
    # SECURITY NOTE: Don't actually store passwords like this in a real system!
    password = db.mapped_column(db.String(80))

    managed_business_id = db.mapped_column(db.Integer, db.ForeignKey('businesses.business_id'), nullable=True)
    managed_business = db.relationship('Business', backref=db.backref('managers', lazy=True))

    attended_events = db.relationship('Event', secondary='attendances', backref=db.backref('attendees', lazy=True))

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f"<User(name={self.name!r})>"


class Business(db.Model):
    __tablename__ = 'businesses'
    business_id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String, unique=True)
    business_type = db.mapped_column(db.String)
    address = db.mapped_column(db.String)
    menu = db.mapped_column(db.Text)
    promotions = db.mapped_column(db.Text)


class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String, unique=True)

    business_id = db.mapped_column(db.Integer, db.ForeignKey('businesses.business_id'), nullable=False)
    business = db.relationship('Business', backref=db.backref('events', lazy=True))

    event_type = db.mapped_column(db.String)
    start_time = db.mapped_column(db.DateTime)
    end_time = db.mapped_column(db.DateTime)


class Post(db.Model):
    __tablename__ = 'posts'
    post_id = db.mapped_column(db.Integer, primary_key=True)

    event_id = db.mapped_column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('posts', lazy=True))

    text = db.mapped_column(db.Text)
    image_url = db.mapped_column(db.String)
    created_at = db.mapped_column(db.DateTime, default=datetime.utcnow)


class Friendship(db.Model):
    __tablename__ = 'friendships'
    originator_id = db.mapped_column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    originator = db.relationship('User', backref=db.backref('friendships', lazy=True), foreign_keys=[originator_id])

    target_id = db.mapped_column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    target = db.relationship('User', backref=db.backref('target_friendships', lazy=True), foreign_keys=[target_id])


class Attendance(db.Model):
    __tablename__ = 'attendances'
    user_id = db.mapped_column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    event_id = db.mapped_column(db.Integer, db.ForeignKey('events.event_id'), primary_key=True)
