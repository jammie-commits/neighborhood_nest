from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()

class Resident(db.Model, SerializerMixin):
    __tablename__ = 'residents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    house_number = db.Column(db.String(50))
    neighborhood_id = db.Column(db.Integer, db.ForeignKey('neighborhoods.id'), nullable=True)
    profile_image_url = db.Column(db.String(255))  # URL for profile picture
    role = db.Column(db.String(50), nullable=False, default='user')  # Added role column

    neighborhood = db.relationship('Neighborhood', back_populates='residents')
    activities = db.relationship('Activity', back_populates='resident', foreign_keys='Activity.resident_id')

    __table_args__ = (
        db.UniqueConstraint('email', name='unique_email'),
    )

    def __repr__(self):
        return f"<Resident {self.name} (ID: {self.id}, Email: {self.email})>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'house_number': self.house_number,
            'neighborhood_id': self.neighborhood_id,
            'profile_image_url': self.profile_image_url,
            'role': self.role
        }

class Neighborhood(db.Model, SerializerMixin):
    __tablename__ = 'neighborhoods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255))  # URL for neighborhood image

    residents = db.relationship('Resident', back_populates='neighborhood')

    def __repr__(self):
        return f"<Neighborhood {self.name} (ID: {self.id}, Location: {self.location})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'image_url': self.image_url
        }

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('residents.id'))
    event_id = db.Column(db.Integer)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('residents.id'))

    resident = db.relationship('Resident', back_populates='activities', foreign_keys=[resident_id])
    user = db.relationship('Resident', foreign_keys=[user_id])

    def __repr__(self):
        return f"<Activity (ID: {self.id}, Resident ID: {self.resident_id}, Event ID: {self.event_id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'resident_id': self.resident_id,
            'event_id': self.event_id,
            'news_id': self.news_id,
            'user_id': self.user_id
        }

class News(db.Model, SerializerMixin):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(255))  # URL for news image
    resident_id = db.Column(db.Integer, db.ForeignKey('residents.id'), nullable=False)  # ForeignKey to Resident model
    neighborhood_id = db.Column(db.Integer, db.ForeignKey('neighborhoods.id'), nullable=False)  # ForeignKey to Neighborhood model
    
    # Relationships
    resident = db.relationship('Resident', backref=db.backref('news', lazy=True))
    neighborhood = db.relationship('Neighborhood', backref=db.backref('news', lazy=True))

    def __repr__(self):
        return f"<News {self.title} (ID: {self.id}, Created: {self.date_created})>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'resident_id': self.resident_id,
            'resident_name': self.resident.name,  # Assuming you want the resident's name in the dict
            'neighborhood_id': self.neighborhood_id,
            'neighborhood_name': self.neighborhood.name  # Assuming you want the neighborhood's name in the dict
        }

class Event(db.Model, SerializerMixin):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    image_url = db.Column(db.String(255))  # URL for event image
    neighborhood_id = db.Column(db.Integer, db.ForeignKey('neighborhoods.id'), nullable=False)  # ForeignKey to Neighborhood model
    resident_id = db.Column(db.Integer, db.ForeignKey('residents.id'), nullable=True)  # Add this line if it's missing

    # Relationships
    neighborhood = db.relationship('Neighborhood', backref=db.backref('events', lazy=True))
    resident = db.relationship('Resident', backref=db.backref('events', lazy=True))

    def __repr__(self):
        return f"<Event {self.name} (ID: {self.id}, Date: {self.date})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date': self.date,
            'image_url': self.image_url,
            'neighborhood_id': self.neighborhood_id,
            'neighborhood_name': self.neighborhood.name,  # Assuming you want the neighborhood's name in the dict
            'resident_id': self.resident_id
        }


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'message': self.message,
            'date_submitted': self.date_submitted.isoformat()
        }
    
class Notifications(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    neighborhood_id = db.Column(db.Integer, db.ForeignKey('neighborhoods.id'), nullable=False)
    resident_id = db.Column(db.Integer, db.ForeignKey('residents.id'), nullable=False)

    # Relationship between notifications and residents
    resident = db.relationship('Resident', backref='notifications')
    #relationship between notifications and neighborhoods
    neighborhood = db.relationship('Neighborhood', backref='notifications')
    
    

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'date_created': self.date_created.isoformat(),  # Ensures ISO format for date
            'neighborhood_id': self.neighborhood_id,
            'resident_id': self.resident_id
        }